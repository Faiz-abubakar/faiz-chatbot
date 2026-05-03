import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

st.set_page_config(
    page_title="Faiz ChatBot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&display=swap');

/* Base */
html, body, [class*="css"] { font-family: 'Sora', sans-serif !important; }
.stApp { background: #0d0f14 !important; color: #e8eaf0 !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #161a24 !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}
section[data-testid="stSidebar"] * { color: #e8eaf0 !important; }
section[data-testid="stSidebar"] .stCaption { color: #6b7280 !important; }

/* All buttons default */
.stButton > button {
    background: #1e2333 !important;
    color: #e8eaf0 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 9px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    transition: all 0.15s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #252c3f !important;
    border-color: rgba(110,142,251,0.35) !important;
    color: #fff !important;
}

/* New Chat button override */
div[data-testid="stSidebar"] div:first-of-type .stButton > button {
    background: linear-gradient(135deg, #6e8efb, #a777e3) !important;
    border: none !important;
    font-weight: 500 !important;
    color: #fff !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #161a24 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 12px 16px !important;
    margin-bottom: 4px !important;
}
[data-testid="stChatMessage"] p { color: #e8eaf0 !important; font-size: 13.5px !important; line-height: 1.7 !important; }
[data-testid="stChatMessage"] code {
    background: rgba(0,0,0,0.35) !important;
    color: #a5b4fc !important;
    border-radius: 5px !important;
    padding: 1px 5px !important;
    font-size: 12px !important;
}
[data-testid="stChatMessage"] pre {
    background: #0d0f14 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    padding: 12px !important;
}

/* User message bubble */
[data-testid="stChatMessage"][data-testid*="user"] {
    background: linear-gradient(135deg, rgba(110,142,251,0.15), rgba(167,119,227,0.15)) !important;
    border-color: rgba(110,142,251,0.2) !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: #161a24 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    color: #e8eaf0 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(110,142,251,0.4) !important;
}
[data-testid="stChatInput"] textarea {
    color: #e8eaf0 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #6e8efb, #a777e3) !important;
    border-radius: 9px !important;
}

/* Action buttons under messages */
.action-row .stButton > button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #6b7280 !important;
    font-size: 11px !important;
    padding: 3px 10px !important;
    border-radius: 6px !important;
    width: auto !important;
}
.action-row .stButton > button:hover {
    color: #e8eaf0 !important;
    border-color: rgba(255,255,255,0.2) !important;
    background: rgba(255,255,255,0.05) !important;
}

/* Dividers */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* Checkbox */
[data-testid="stCheckbox"] label { color: #6b7280 !important; font-size: 12px !important; }
[data-testid="stCheckbox"] span { color: #6b7280 !important; }

/* Markdown headings in sidebar */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #e8eaf0 !important; font-size: 14px !important; font-weight: 600 !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: #1e2333 !important;
    border: 1px dashed rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] label { color: #6b7280 !important; font-size: 11px !important; }

/* Toast */
[data-testid="stToast"] { background: #1e2333 !important; color: #e8eaf0 !important; border: 1px solid rgba(255,255,255,0.1) !important; }

/* Spinner */
[data-testid="stSpinner"] { color: #6e8efb !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    color: #22c55e;
    margin-bottom: 8px;
}
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; display: inline-block; }

/* Model badge */
.model-badge {
    background: rgba(110,142,251,0.1);
    border: 1px solid rgba(110,142,251,0.2);
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 10px;
    color: #6e8efb;
    font-family: monospace;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #6b7280;
}
.empty-icon {
    width: 60px; height: 60px;
    background: linear-gradient(135deg, #6e8efb, #a777e3);
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 28px;
    margin: 0 auto 16px;
}
</style>
""", unsafe_allow_html=True)

# ── API Setup ──────────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("⚠️ API Key not found. Add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

SYSTEM_PROMPT = """You are Faiz ChatBot, a powerful all-purpose AI assistant built for Kenyan users.

CAPABILITIES:
- Answer ANY question accurately and thoroughly
- Write, explain, and debug code in any language
- Generate creative content (stories, poems, scripts, marketing copy)
- Provide academic research and clear explanations
- Give Nairobi/Kenya-specific advice, recommendations, and context
- Translate to/from Swahili and other languages
- Solve math, logic, and reasoning problems
- Assist with business, productivity, and planning

STYLE:
- Helpful, thorough, and conversational
- Use markdown formatting for clarity (code blocks, lists, bold)
- Prioritize Kenyan context where relevant
- Be direct and concise unless detail is needed"""

MODEL = "llama-3.3-70b-versatile"

QUICK_ACTIONS = {
    "📅  Today's agenda": "Help me plan a productive agenda for today. Ask me what tasks I have, then help me prioritize them.",
    "🖼  Image prompt": "Generate a detailed, creative AI image generation prompt. Make it vivid and specific.",
    "✏️  Write or edit": "I need help with writing or editing. What would you like to work on?",
    "🔍  Look something up": "What topic would you like me to research and explain for you?",
    "💻  Write code": "I need help writing some code. What would you like me to build?",
    "🌍  Translate": "What text would you like me to translate, and to which language?",
}

SUGGESTION_CHIPS = [
    "Best restaurants in Nairobi 🍽️",
    "Explain machine learning simply",
    "Write a Python web scraper",
    "Translate to Swahili",
    "Help me write a CV",
    "How does M-Pesa work?",
]

# ── Session State ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None
if "web_access" not in st.session_state:
    st.session_state.web_access = False
if "pending_quick" not in st.session_state:
    st.session_state.pending_quick = None

# ── Helpers ────────────────────────────────────────────────────────────────────
def extract_text(uploaded_file):
    try:
        if uploaded_file.type == "text/plain":
            return uploaded_file.read().decode("utf-8")[:6000]
        return f"[Binary file: {uploaded_file.name} — {uploaded_file.type}]"
    except Exception:
        return f"[Could not read: {uploaded_file.name}]"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_completion(messages):
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=4096,
    )

def build_api_messages(up_to_idx=None):
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    history = st.session_state.messages if up_to_idx is None else st.session_state.messages[:up_to_idx]
    for m in history:
        c = m["content"] if isinstance(m["content"], str) else m["content"].get("text", "")
        msgs.append({"role": m["role"], "content": c})
    return msgs

def send_message(user_text, file_info=None):
    """Append user message, call API, append response, rerun."""
    final_prompt = user_text
    if file_info:
        final_prompt = f"[FILE: {file_info['name']}]\n{file_info['content']}\n\n[QUESTION]: {user_text}"
    if st.session_state.web_access:
        final_prompt = f"[Note: User wants up-to-date/web information]\n\n{final_prompt}"

    user_content = {"text": user_text, "file": file_info["name"]} if file_info else user_text
    st.session_state.messages.append({"role": "user", "content": user_content})

    # Temporarily store prompt override for API
    st.session_state.messages[-1]["_api_content"] = final_prompt

    with st.spinner(""):
        try:
            api_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                c = m.get("_api_content") or (m["content"] if isinstance(m["content"], str) else m["content"].get("text", ""))
                api_msgs.append({"role": m["role"], "content": c})

            completion = get_completion(api_msgs)
            response = completion.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.uploaded_file_data = None
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Error: {e}"})

    # Clean up temp key
    for m in st.session_state.messages:
        m.pop("_api_content", None)

    st.rerun()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.image("Faiz Chatbot Logo.png", use_container_width=True)
    except Exception:
        st.markdown('<div style="font-size:32px;text-align:center">🤖</div>', unsafe_allow_html=True)

    st.markdown("## Faiz ChatBot")
    st.markdown('<div class="status-badge"><span class="status-dot"></span> Online</div>', unsafe_allow_html=True)
    st.caption("Your All-Purpose AI Assistant")
    st.markdown("---")

    if st.button("＋  New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.uploaded_file_data = None
        st.session_state.pending_quick = None
        st.rerun()

    st.markdown("---")
    st.markdown("### Quick Actions")

    for label, prompt in QUICK_ACTIONS.items():
        if st.button(label, use_container_width=True):
            st.session_state.pending_quick = prompt
            st.rerun()

    st.markdown("---")

    # Web access toggle
    st.session_state.web_access = st.checkbox(
        "🌐  Web context hints",
        value=st.session_state.web_access,
        help="Adds a note asking the model to give current/up-to-date information"
    )

    st.markdown("---")

    # File uploader in sidebar
    uploaded = st.file_uploader(
        "📎 Attach a file",
        type=["txt", "png", "jpg", "jpeg", "pdf", "docx"],
        help="Max 5MB. Text files are read; others are referenced by name."
    )
    if uploaded:
        if uploaded.size > 5 * 1024 * 1024:
            st.error("Max file size is 5MB")
        else:
            content = extract_text(uploaded)
            st.session_state.uploaded_file_data = {"name": uploaded.name, "content": content}
            st.success(f"✓ {uploaded.name}")

    if st.session_state.uploaded_file_data:
        if st.button("✕ Remove file"):
            st.session_state.uploaded_file_data = None
            st.rerun()

    st.markdown("---")
    st.markdown(f'<div class="model-badge">{MODEL}</div>', unsafe_allow_html=True)
    st.caption("Powered by Groq")

# ── Handle pending quick action ────────────────────────────────────────────────
if st.session_state.pending_quick:
    prompt = st.session_state.pending_quick
    st.session_state.pending_quick = None
    send_message(prompt)

# ── Main Chat Area ─────────────────────────────────────────────────────────────
# Header
col_h1, col_h2 = st.columns([6, 1])
with col_h1:
    st.markdown("### 💬 Chat")
with col_h2:
    st.markdown(f'<div style="text-align:right;padding-top:8px"><span class="model-badge">llama-3.3-70b</span></div>', unsafe_allow_html=True)

st.markdown("---")

# Empty state
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size:48px;margin-bottom:16px">👋</div>
        <h2 style="color:#e8eaf0;margin-bottom:8px">How can I help you today?</h2>
        <p style="color:#6b7280;margin-bottom:24px">Ask me anything — code, research, writing, math, or just a conversation.</p>
    </div>
    """, unsafe_allow_html=True)

    # Suggestion chips
    st.markdown("**Try asking:**")
    cols = st.columns(3)
    for i, chip in enumerate(SUGGESTION_CHIPS):
        with cols[i % 3]:
            if st.button(chip, key=f"chip_{i}", use_container_width=True):
                send_message(chip)

# ── Render Messages ────────────────────────────────────────────────────────────
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        content = message["content"]
        display_text = content if isinstance(content, str) else content.get("text", "")

        st.markdown(display_text)

        if isinstance(content, dict) and content.get("file"):
            st.caption(f"📎 {content['file']}")

        # Action buttons for assistant messages
        if message["role"] == "assistant":
            st.markdown('<div class="action-row">', unsafe_allow_html=True)
            c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 5])

            with c1:
                if st.button("📋 Copy", key=f"copy_{idx}"):
                    # Use JS clipboard via component
                    st.toast("✓ Copied!", icon=None)
                    st.markdown(
                        f"<script>navigator.clipboard.writeText({repr(display_text)})</script>",
                        unsafe_allow_html=True
                    )

            with c2:
                if st.button("🔄 Retry", key=f"retry_{idx}"):
                    # Find preceding user message
                    user_idx = idx - 1
                    while user_idx >= 0 and st.session_state.messages[user_idx]["role"] != "user":
                        user_idx -= 1

                    if user_idx >= 0:
                        with st.spinner("Regenerating..."):
                            try:
                                api_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
                                for i in range(user_idx + 1):
                                    m = st.session_state.messages[i]
                                    c = m["content"] if isinstance(m["content"], str) else m["content"].get("text", "")
                                    api_msgs.append({"role": m["role"], "content": c})

                                completion = get_completion(api_msgs)
                                st.session_state.messages[idx]["content"] = completion.choices[0].message.content
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

            with c3:
                if st.button("🗑 Delete", key=f"delete_{idx}"):
                    # Remove this message and the preceding user message
                    to_remove = [idx]
                    if idx > 0 and st.session_state.messages[idx - 1]["role"] == "user":
                        to_remove.append(idx - 1)
                    for i in sorted(to_remove, reverse=True):
                        st.session_state.messages.pop(i)
                    st.rerun()

            with c4:
                if st.button("📤 Share", key=f"share_{idx}"):
                    preview = display_text[:200] + ("..." if len(display_text) > 200 else "")
                    st.toast(f"Share: {preview}", icon=None)

            st.markdown('</div>', unsafe_allow_html=True)

# ── Chat Input ─────────────────────────────────────────────────────────────────
if st.session_state.uploaded_file_data:
    st.info(f"📎 File attached: **{st.session_state.uploaded_file_data['name']}** — it will be included with your next message.")

prompt = st.chat_input("Ask anything... (Shift+Enter for new line)")

if prompt:
    send_message(prompt, file_info=st.session_state.uploaded_file_data)
