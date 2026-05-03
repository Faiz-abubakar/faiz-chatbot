import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
import pyperclip

st.set_page_config(page_title="Faiz ChatBot", page_icon="Faiz Chatbot Logo.png", layout="wide")

# Custom CSS with dark theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif !important; }

/* Dark background */
.stApp { background: #0d0f14; }
section[data-testid="stSidebar"] { background: #161a24 !important; border-right: 1px solid rgba(255,255,255,0.07); }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6e8efb, #a777e3) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-family: 'Sora', sans-serif !important;
    font-size: 12px !important; font-weight: 500 !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Chat messages */
[data-testid="stChatMessage"] { background: #1e2333 !important; border-radius: 14px !important; border: 1px solid rgba(255,255,255,0.07) !important; }

/* Chat input */
[data-testid="stChatInput"] { background: #161a24 !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 16px !important; }
textarea { background: transparent !important; color: #e8eaf0 !important; font-family: 'Sora', sans-serif !important; }

/* Text colors */
p, h1, h2, h3, label, span { color: #e8eaf0 !important; }

/* Action buttons styling */
.message-actions { display: flex; gap: 12px; margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.07); }
.action-button { background: transparent; border: 1px solid rgba(255,255,255,0.15); color: #a0a4b0; cursor: pointer; font-size: 12px; padding: 4px 12px; border-radius: 8px; }
.action-button:hover { background: rgba(255,255,255,0.05); color: white; }

/* File uploader */
[data-testid="stFileUploader"] button { background: #161a24 !important; border: 1px solid rgba(255,255,255,0.15) !important; color: #e8eaf0 !important; }
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
- Answer ANY question accurately
- Write and debug code
- Generate creative content
- Provide academic research
- Explain complex topics
- Give directions and navigation help

STYLE:
- Be helpful, thorough, and detailed
- Be conversational and friendly
- Prioritize Kenyan context
"""

def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        if uploaded_file.type == "text/plain":
            return uploaded_file.read().decode()[:5000]
        else:
            return f"[File uploaded: {uploaded_file.name}]"
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

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# Sidebar
with st.sidebar:
    st.image("Faiz Chatbot Logo.png", use_container_width=True)
    st.markdown("# Faiz ChatBot")
    st.caption("Your All-Purpose AI Assistant")
    st.markdown("---")
    
    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.uploaded_file = None
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    
    quick_actions = [
        "What's on the agenda today?",
        "Create an image",
        "Write or edit text",
        "Look something up"
    ]
    
    for action in quick_actions:
        if st.button(action, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": action})
            st.rerun()
    
    st.markdown("---")
    web_access = st.checkbox("Web access")
    st.caption("Powered by Groq")

# Display chat messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, dict):
            st.markdown(content["text"])
            st.caption(f"Attached: {content['file']}")
        else:
            st.markdown(content)
        
        if message["role"] == "assistant":
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("Copy", key=f"copy_{idx}"):
                    try:
                        text_to_copy = content if isinstance(content, str) else content["text"]
                        pyperclip.copy(text_to_copy)
                        st.toast("Copied to clipboard!", icon="✓")
                    except:
                        st.toast("Copy manually", icon="⚠️")
            
            with col2:
                if st.button("Retry", key=f"retry_{idx}"):
                    with st.spinner("Regenerating..."):
                        try:
                            user_msg_idx = idx - 1
                            if user_msg_idx >= 0 and st.session_state.messages[user_msg_idx]["role"] == "user":
                                user_prompt = st.session_state.messages[user_msg_idx]["content"]
                                if isinstance(user_prompt, dict):
                                    user_prompt = user_prompt["text"]
                                
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
                    st.toast("Cannot stop completed response", icon="⚠️")
            
            with col4:
                if st.button("Share", key=f"share_{idx}"):
                    try:
                        share_text = content if isinstance(content, str) else content["text"]
                        pyperclip.copy(share_text[:300] + "...")
                        st.toast("Share text copied!", icon="✓")
                    except:
                        st.toast("Select and copy to share", icon="⚠️")

# Chat input area
col1, col2 = st.columns([10, 1])

with col1:
    prompt = st.chat_input("Ask anything...")

with col2:
    uploaded_file = st.file_uploader(
        "+", 
        type=['txt', 'png', 'jpg', 'jpeg', 'pdf', 'docx'],
        label_visibility="collapsed",
        key="file_uploader_plus"
    )
    if uploaded_file:
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("Maximum size is 5MB")
        else:
            st.session_state.uploaded_file = uploaded_file
            st.success(f"Loaded: {uploaded_file.name}")

if prompt:
    if st.session_state.uploaded_file:
        file_content = extract_text_from_file(st.session_state.uploaded_file)
        final_prompt = f"[FILE: {st.session_state.uploaded_file.name}]\n{file_content}\n[QUESTION]: {prompt}"
    else:
        final_prompt = prompt
    
    if web_access:
        final_prompt = f"[USE WEB SEARCH FOR CURRENT INFO]\n{final_prompt}"
    
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
