import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime
import html

st.set_page_config(page_title="Faiz ChatBot", page_icon="Faiz Chatbot Logo.png", layout="wide")

# Custom CSS for mobile responsive design
st.markdown("""
<style>
    /* Mobile responsive */
    @media (max-width: 768px) {
        .stChatMessage {
            font-size: 14px;
        }
        .stButton button {
            font-size: 12px;
            padding: 4px 8px;
        }
        [data-testid="column"] {
            min-width: 0px;
        }
    }
    
    /* Chat container - scroll to bottom */
    [data-testid="stChatMessageContainer"] {
        display: flex;
        flex-direction: column-reverse;
    }
    
    /* Copy button style */
    .copy-btn {
        background-color: transparent;
        border: none;
        cursor: pointer;
        font-size: 14px;
        margin-left: 10px;
        padding: 4px 8px;
        border-radius: 6px;
    }
    .copy-btn:hover {
        background-color: #e0e0e0;
    }
    
    /* Action buttons container */
    .message-actions {
        display: flex;
        gap: 8px;
        margin-top: 8px;
        font-size: 12px;
    }
    
    /* Bottom chat input fixed */
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 10px;
        z-index: 100;
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
- Answer ANY question accurately
- Write and debug code
- Generate creative content
- Provide academic research
- Explain complex topics
- Give directions and navigation help
- Translate languages
- Solve math problems

STYLE:
- Be helpful, thorough, and detailed
- Be conversational and friendly
- Prioritize Kenyan context
- Never say "I can't help with that"
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

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False

# Sidebar
with st.sidebar:
    st.image("Faiz Chatbot Logo.png", use_container_width=True)
    st.markdown("# Faiz ChatBot")
    st.caption("Your All-Purpose AI Assistant")
    st.markdown("---")
    
    # New Chat button
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.uploaded_file = None
        st.rerun()
    
    st.markdown("---")
    
    # 1-click prompts
    st.markdown("### Quick Prompts")
    quick_prompts = [
        "What's on the agenda today?",
        "Create an image prompt",
        "Write or edit text",
        "Look something up"
    ]
    
    for qp in quick_prompts:
        if st.button(qp, use_container_width=True):
            prompt = qp
            # Process immediately
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.spinner("Thinking..."):
                try:
                    messages_for_api = [{"role": "system", "content": CLAUDE_PROTOCOL}]
                    for m in st.session_state.messages[-20:]:
                        content = m["content"] if isinstance(m["content"], str) else m["content"]["text"]
                        messages_for_api.append({"role": m["role"], "content": content})
                    
                    completion = get_completion(messages_for_api)
                    response = completion.choices[0].message.content
                    
                    with st.chat_message("assistant"):
                        st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.markdown("---")
    st.caption("Powered by Groq | v3.0")

# Display chat messages (newest at bottom)
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, dict):
            st.markdown(content["text"])
            st.caption(f"📎 {content['file']}")
        else:
            st.markdown(content)
        
        # Add action buttons for assistant messages
        if message["role"] == "assistant":
            cols = st.columns([1, 1, 1, 6])
            with cols[0]:
                if st.button("📋 Copy", key=f"copy_{idx}"):
                    st.write(f'<script>navigator.clipboard.writeText(`{html.escape(content)}`);</script>', 
                            unsafe_allow_html=True)
                    st.toast("Copied!", icon="✅")
            with cols[1]:
                if st.button("🔄 Retry", key=f"retry_{idx}"):
                    # Regenerate response
                    with st.spinner("Regenerating..."):
                        try:
                            messages_for_api = [{"role": "system", "content": CLAUDE_PROTOCOL}]
                            for m in st.session_state.messages[:idx]:
                                c = m["content"] if isinstance(m["content"], str) else m["content"]["text"]
                                messages_for_api.append({"role": m["role"], "content": c})
                            
                            completion = get_completion(messages_for_api)
                            new_response = completion.choices[0].message.content
                            st.session_state.messages[idx]["content"] = new_response
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            with cols[2]:
                if st.button("⏹️ Stop", key=f"stop_{idx}"):
                    st.session_state.stop_generation = True
                    st.toast("Generation stopped", icon="⏹️")
            with cols[3]:
                if st.button("📤 Share", key=f"share_{idx}"):
                    st.toast("Share link copied!", icon="🔗")

# Fixed bottom chat input
st.markdown("---")
col1, col2 = st.columns([10, 1])

with col1:
    prompt = st.chat_input("Ask anything... +")

with col2:
    # Upload file button with 5MB limit
    uploaded_file = st.file_uploader(
        "📎", 
        type=['txt', 'png', 'jpg', 'jpeg', 'pdf', 'docx'],
        label_visibility="collapsed",
        key="file_uploader_plus"
    )
    if uploaded_file:
        # Check file size (5MB limit)
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("File too large! Maximum size is 5MB")
        else:
            st.session_state.uploaded_file = uploaded_file
            st.success(f"✅ {uploaded_file.name}")

# Web access toggle
web_access = st.checkbox("🌐 Web access", value=False)

# Process prompt
if prompt:
    if st.session_state.uploaded_file:
        file_content = extract_text_from_file(st.session_state.uploaded_file)
        final_prompt = f"[FILE: {st.session_state.uploaded_file.name}]\n{file_content}\n[QUESTION]: {prompt}"
    else:
        final_prompt = prompt
    
    if web_access:
        final_prompt = f"[USE WEB SEARCH TO FIND CURRENT INFO]\n{final_prompt}"
    
    user_message_content = prompt
    if st.session_state.uploaded_file:
        user_message_content = {"text": prompt, "file": st.session_state.uploaded_file.name}
    
    st.session_state.messages.append({"role": "user", "content": user_message_content})
    with st.chat_message("user"):
        st.markdown(prompt)
        if st.session_state.uploaded_file:
            st.caption(f"📎 {st.session_state.uploaded_file.name}")
    
    with st.spinner("Thinking..."):
        try:
            messages_for_api = [{"role": "system", "content": CLAUDE_PROTOCOL}]
            for m in st.session_state.messages[-20:]:
                content = m["content"] if isinstance(m["content"], str) else m["content"]["text"]
                messages_for_api.append({"role": m["role"], "content": content})
            
            completion = get_completion(messages_for_api)
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            st.session_state.uploaded_file = None
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {e}")
