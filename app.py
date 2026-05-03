import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
import pypdf
import docx
import io

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Faiz ChatBot Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS (Optimized) ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif !important; }
.stApp { background: #0d0f14 !important; color: #e8eaf0 !important; }

/* Better Message Spacing */
[data-testid="stChatMessage"] {
    background: #161a24 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 15px !important;
    margin-bottom: 12px !important;
}

/* User Message Gradient */
[data-testid="stChatMessage"][data-testid*="user"] {
    background: linear-gradient(135deg, rgba(110,142,251,0.1), rgba(167,119,227,0.1)) !important;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] { background: #161a24 !important; border-right: 1px solid rgba(255,255,255,0.07) !important; }

/* Status Badge */
.status-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.2);
    border-radius: 20px; padding: 3px 10px; font-size: 11px; color: #22c55e;
}
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

/* Model Badge */
.model-badge {
    background: rgba(110,142,251,0.1); border: 1px solid rgba(110,142,251,0.2);
    border-radius: 6px; padding: 3px 8px; font-size: 10px; color: #6e8efb; font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# ── API & Model Setup ────────────────────────────────────────────────────────
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("⚠️ API Key not found. Please add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = """You are Faiz ChatBot, a premier AI built for Kenyan users. 
Context: You understand Sheng, Swahili, and English. You are an expert in coding, research, and local Kenyan context (M-Pesa, KRA, Nairobi life).
Style: Conversational, professional, and helpful. Use Markdown and LaTeX for formulas."""

# ── Logic: File Processing ──────────────────────────────────────────────────
def extract_text_from_file(uploaded_file):
    try:
        file_type = uploaded_file.type
        if file_type == "text/plain":
            return uploaded_file.read().decode("utf-8")
        elif file_type == "application/pdf":
            pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
            return "\n".join([page.extract_text() for page in pdf_reader.pages])
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            return "\n".join([para.text for para in doc.paragraphs])
        return f"[File attached: {uploaded_file.name}]"
    except Exception as e:
        return f"Error reading file: {str(e)}"

# ── Logic: Streaming Completion ──────────────────────────────────────────────
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=6))
def get_streaming_response(messages):
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=4096,
        stream=True
    )

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_context" not in st.session_state:
    st.session_state.file_context = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Faiz ChatBot")
    st.markdown('<div class="status-badge"><span class="status-dot"></span> Online</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.file_context = None
        st.rerun()

    st.markdown("### Document Intelligence")
    uploaded_file = st.file_uploader("Upload PDF, Docx, or TXT", type=["pdf", "docx", "txt"])
    if uploaded_file:
        with st.spinner("Analyzing document..."):
            text = extract_text_from_file(uploaded_file)
            st.session_state.file_context = {"name": uploaded_file.name, "content": text}
            st.success(f"Loaded: {uploaded_file.name}")

    st.markdown("---")
    st.markdown(f'<div class="model-badge">{MODEL}</div>', unsafe_allow_html=True)

# ── Main Chat Area ────────────────────────────────────────────────────────────
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask Faiz anything..."):
    # Prepare User Message
    user_display = prompt
    full_prompt = prompt
    
    # Inject File Context if exists
    if st.session_state.file_context:
        full_prompt = f"Context from file '{st.session_state.file_context['name']}':\n{st.session_state.file_context['content']}\n\nUser Question: {prompt}"
        st.session_state.file_context = None # Clear context after use or keep based on preference

    st.session_state.messages.append({"role": "user", "content": user_display, "hidden_content": full_prompt})
    
    with st.chat_message("user"):
        st.markdown(user_display)

    # Assistant Response with Streaming
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Build Message History
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in st.session_state.messages:
            api_messages.append({
                "role": m["role"], 
                "content": m.get("hidden_content") if m.get("hidden_content") else m["content"]
            })

        try:
            stream = get_streaming_response(api_messages)
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Something went wrong: {e}")
