import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

st.set_page_config(page_title="Faiz ChatBot", page_icon="Faiz Chatbot Logo.png", layout="wide")

# Custom CSS for mobile responsive design and no emojis
st.markdown("""
<style>
    @media (max-width: 768px) {
        .stChatMessage {
            font-size: 14px;
        }
        .stButton button {
            font-size: 12px;
            padding: 4px 8px;
        }
    }
    
    .message-actions {
        display: flex;
        gap: 12px;
        margin-top: 8px;
        font-size: 12px;
    }
    
    .action-link {
        color: #666;
        text-decoration: none;
        cursor: pointer;
        font-size: 12px;
    }
    .action-link:hover {
        color: #000;
    }
    
    /* Hide default emoji in file uploader */
    [data-testid="stFileUploader"] button {
        font-size: 20px;
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
    
    if st.button("What's on the agenda today?", use_container_width=True):
        prompt = "What's on the agenda today?"
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
    
    if st.button("Create an image", use_container_width=True):
        prompt = "Give me a detailed prompt for generating an image"
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
    
    if st.button("Write or edit text", use_container_width=True):
        prompt = "Help me write or edit some text"
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
    
    if st.button("Look something up", use_container_width=True):
        prompt = "Help me look up information"
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
            col1, col2, col3, col4 = st.columns([1, 1, 1, 6])
            with col1:
                if st.button("Copy", key=f"copy_{idx}"):
                    st.toast("Copied to clipboard", icon=None)
            with col2:
                if st.button("Retry", key=f"retry_{idx}"):
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
            with col3:
                if st.button("Stop", key=f"stop_{idx}"):
                    st.toast("Generation stopped", icon=None)
            with col4:
                if st.button("Share", key=f"share_{idx}"):
                    st.toast("Share link ready", icon=None)

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
            st.error("Maximum file size is 5MB")
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
    with st.chat_message("user"):
        st.markdown(prompt)
        if st.session_state.uploaded_file:
            st.caption(f"Attached: {st.session_state.uploaded_file.name}")
    
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
