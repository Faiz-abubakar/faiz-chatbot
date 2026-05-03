import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
import io

st.set_page_config(page_title="Faiz ChatBot", page_icon="Faiz Chatbot Logo.png", layout="wide")

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found. Please check Streamlit Secrets.")
    st.stop()

# Powerful system prompt for general-purpose AI
CLAUDE_PROTOCOL = """
You are Faiz ChatBot, a powerful, all-purpose AI assistant capable of handling ANY task.

CAPABILITIES:
- Answer ANY question accurately and thoroughly
- Write, debug, and explain code in any programming language
- Generate creative content (stories, poems, scripts)
- Provide academic research assistance
- Explain complex topics simply
- Navigate, plan routes, give directions
- Analyze data and provide insights
- Translate languages
- Solve math problems

STYLE:
- Be helpful, thorough, and detailed
- Provide step-by-step explanations when needed
- Be conversational and friendly
- Prioritize Kenyan context when relevant
- Never say "I can't help with that" - find a way to help

You are capable of doing PARTICULARLY EVERYTHING within ethical boundaries.
"""

def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return None
    
    try:
        # Only handle text files to avoid dependencies
        if uploaded_file.type == "text/plain":
            return uploaded_file.read().decode()[:5000]
        elif uploaded_file.type.startswith("image/"):
            return f"[Image uploaded: {uploaded_file.name}]"
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

# Sidebar (minimal - only logo and clear button)
with st.sidebar:
    st.image("Faiz Chatbot Logo.png", use_container_width=True)
    st.markdown("# Faiz ChatBot")
    st.caption("Your All-Purpose AI Assistant")
    st.markdown("---")
    
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.uploaded_file = None
        st.rerun()
    
    st.markdown("---")
    st.caption("Powered by Groq | v3.0")

# Main chat area
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, dict) and "file" in content:
            st.markdown(content["text"])
            st.caption(f"📎 {content['file']}")
        else:
            st.markdown(content)

# Custom layout for chat input with plus button
col1, col2 = st.columns([12, 1])

with col1:
    prompt = st.chat_input("Ask me anything...")

with col2:
    # Plus button for file upload
    uploaded_file = st.file_uploader(
        "➕", 
        type=['txt', 'png', 'jpg', 'jpeg', 'pdf', 'docx'],
        label_visibility="collapsed",
        key="file_uploader_plus"
    )
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"✅ {uploaded_file.name}")

# Handle the query
if prompt:
    final_prompt = prompt
    
    # Process uploaded file if exists
    if st.session_state.uploaded_file:
        file_content = extract_text_from_file(st.session_state.uploaded_file)
        if file_content:
            final_prompt = f"[FILE: {st.session_state.uploaded_file.name}]\n{file_content}\n\n[QUESTION]: {prompt}"
    
    # Store user message
    user_message_content = prompt
    if st.session_state.uploaded_file:
        user_message_content = {"text": prompt, "file": st.session_state.uploaded_file.name}
    
    st.session_state.messages.append({"role": "user", "content": user_message_content})
    with st.chat_message("user"):
        st.markdown(prompt)
        if st.session_state.uploaded_file:
            st.caption(f"📎 {st.session_state.uploaded_file.name}")
    
    # Get AI response
    with st.spinner("Thinking..."):
        try:
            messages_for_api = [{"role": "system", "content": CLAUDE_PROTOCOL}]
            for m in st.session_state.messages[-20:]:
                content = m["content"]
                if isinstance(content, dict):
                    content = content["text"]
                messages_for_api.append({"role": m["role"], "content": content})
            
            completion = get_completion(messages_for_api)
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Clear file after use
            st.session_state.uploaded_file = None
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {e}")