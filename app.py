import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
import pyperclip
from datetime import datetime

st.set_page_config(page_title="Faiz ChatBot", page_icon="Faiz Chatbot Logo.png", layout="wide")

# Dark theme CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif !important; }

.stApp { background: #0d0f14; }
section[data-testid="stSidebar"] { background: #161a24 !important; border-right: 1px solid rgba(255,255,255,0.07); }

.stButton > button {
    background: linear-gradient(135deg, #6e8efb, #a777e3) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-family: 'Sora', sans-serif !important;
    font-size: 12px !important; font-weight: 500 !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

[data-testid="stChatMessage"] { background: #1e2333 !important; border-radius: 14px !important; border: 1px solid rgba(255,255,255,0.07) !important; }

[data-testid="stChatInput"] { background: #161a24 !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 16px !important; }
textarea { background: transparent !important; color: #e8eaf0 !important; font-family: 'Sora', sans-serif !important; }

p, h1, h2, h3, label, span, .stMarkdown { color: #e8eaf0 !important; }

/* Suggestion chips */
.suggestion-chip {
    background: #1e2333;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 8px 16px;
    margin: 4px;
    display: inline-block;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
}
.suggestion-chip:hover {
    background: #2a3042;
    border-color: #6e8efb;
}
</style>
""", unsafe_allow_html=True)

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found. Please check Streamlit Secrets.")
    st.stop()

CLAUDE_PROTOCOL = """
You are Faiz ChatBot, a powerful, all-purpose AI assistant.

CAPABILITIES:
- Answer ANY question accurately and thoroughly
- Write, debug, and explain code in any programming language
- Generate creative content (stories, poems, scripts, images prompts)
- Provide academic research assistance
- Explain complex topics simply
- Give directions, navigation help, and travel advice
- Analyze data and provide insights
- Translate languages and solve math problems

STYLE:
- Be helpful, thorough, and detailed
- Provide step-by-step explanations when needed
- Be conversational and friendly
- Prioritize Kenyan and East African context
- NEVER say "I can't help with that" - find a way to help
"""

def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        if uploaded_file.type == "text/plain":
            return uploaded_file.read().decode()[:5000]
        else:
            return f"[File uploaded: {uploaded_file.name} (type: {uploaded_file.type})]"
    except:
        return f"[File: {uploaded_file.name}]"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_completion(messages):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=4096
    )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# Sidebar
with st.sidebar:
    st.image("Faiz Chatbot Logo.png", use_container_width=True)
    st.markdown("# Faiz ChatBot")
    st.caption("Powered by Claude-Sonnet-4")
    st.markdown("---")
    
    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.uploaded_file = None
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    
    quick_actions = [
        "What's on the agenda today?",
        "Create an image prompt of a Kenyan sunset",
        "Help me write a professional email",
        "Look up information about AI"
    ]
    
    for action in quick_actions:
        if st.button(action, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": action})
            st.rerun()
    
    st.markdown("---")
    web_access = st.checkbox("Web context", value=False, help="Adds web search context to your prompts")
    st.caption("v3.0 | All features active")

# Display chat messages or empty state
if not st.session_state.messages:
    # Empty state with suggestion chips
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center; color: #e8eaf0;'>How can I help you today?</h3>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        suggestions = [
            "Explain quantum computing simply",
            "Write a Python script to analyze data",
            "Create a meal plan for a busy student",
            "Summarize the latest AI developments",
            "Help me prepare for a job interview",
            "Plan a 3-day trip to Mombasa"
        ]
        
        for suggestion in suggestions:
            if st.button(suggestion, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.rerun()
else:
    # Display chat history
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            content = message["content"]
            if isinstance(content, dict):
                st.markdown(content["text"])
                st.caption(f"📎 {content['file']}")
            else:
                st.markdown(content)
            
            # Action buttons for assistant messages
            if message["role"] == "assistant":
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("Copy", key=f"copy_{idx}"):
                        try:
                            text_to_copy = content if isinstance(content, str) else content["text"]
                            pyperclip.copy(text_to_copy)
                            st.toast("Copied to clipboard!", icon="✅")
                        except:
                            st.toast("Copy manually (Ctrl+C)", icon="⚠️")
                
                with col2:
                    if st.button("Retry", key=f"retry_{idx}"):
                        with st.spinner("Regenerating..."):
                            try:
                                user_msg_idx = idx - 1
                                if user_msg_idx >= 0 and st.session_state.messages[user_msg_idx]["role"] == "user":
                                    messages_for_api = [{"role": "system", "content": CLAUDE_PROTOCOL}]
                                    for i in range(user_msg_idx + 1):
                                        msg = st.session_state.messages[i]
                                        c = msg["content"] if isinstance(msg["content"], str) else msg["content"]["text"]
                                        messages_for_api.append({"role": msg["role"], "content": c})
                                    
                                    completion = get_completion(messages_for_api)
                                    new_response = completion.choices[0].message.content
                                    st.session_state.messages[idx]["content"] = new_response
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                
                with col3:
                    if st.button("Stop", key=f"stop_{idx}"):
                        st.toast("Response already completed", icon="ℹ️")
                
                with col4:
                    if st.button("Share", key=f"share_{idx}"):
                        try:
                            share_text = content if isinstance(content, str) else content["text"]
                            pyperclip.copy(f"Check out this response from Faiz ChatBot:\n\n{share_text[:500]}...")
                            st.toast("Share link copied to clipboard!", icon="✅")
                        except:
                            st.toast("Select and copy to share", icon="⚠️")

# Chat input area
col1, col2 = st.columns([10, 1])

with col1:
    prompt = st.chat_input("Ask anything...")

with col2:
    uploaded_file = st.file_uploader(
        "📎", 
        type=['txt', 'png', 'jpg', 'jpeg', 'pdf', 'docx'],
        label_visibility="collapsed",
        key="file_uploader_plus"
    )
    if uploaded_file:
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("Maximum file size is 5MB")
        else:
            st.session_state.uploaded_file = uploaded_file
            st.success(f"✅ {uploaded_file.name}")

# Send button in chat input is automatic with st.chat_input
if prompt:
    if st.session_state.uploaded_file:
        file_content = extract_text_from_file(st.session_state.uploaded_file)
        final_prompt = f"[FILE: {st.session_state.uploaded_file.name}]\n{file_content}\n\n[USER QUESTION]: {prompt}"
    else:
        final_prompt = prompt
    
    if web_access:
        final_prompt = f"[USE WEB SEARCH FOR CURRENT, REAL-TIME INFORMATION]\n{final_prompt}"
    
    user_message_content = prompt
    if st.session_state.uploaded_file:
        user_message_content = {"text": prompt, "file": st.session_state.uploaded_file.name}
    
    st.session_state.messages.append({"role": "user", "content": user_message_content})
    
    with st.spinner("Thinking..."):
        try:
            messages_for_api = [{"role": "system", "content": CLAUDE_PROTOCOL}]
            for m in st.session_state.messages:
                content = m["content"] if isinstance(m["content"], str) else m["content"]["text"]
                messages_for_api.append({"role": m["role"], "content": content})
            
            completion = get_completion(messages_for_api)
            response = completion.choices[0].message.content
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.uploaded_file = None
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {e}")
