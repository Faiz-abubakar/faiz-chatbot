import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
import requests
from bs4 import BeautifulSoup
import json

st.set_page_config(page_title="Faiz ChatBot", page_icon="Faiz Chatbot Logo.png", layout="wide")

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API key missing. Add GROQ_API_KEY to .streamlit/secrets.toml")
    st.stop()

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are Faiz ChatBot, a powerful all-purpose AI assistant built for Kenyan users.

CAPABILITIES:
- Answer any question accurately and thoroughly
- Write and debug code in any language
- Generate creative content (stories, scripts, marketing copy)
- Research and explain complex topics clearly
- Kenya/Nairobi context: local advice, Swahili translation, M-Pesa, recommendations
- Math, logic, and reasoning problems

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
    
    file_type = uploaded_file.type
    
    try:
        if file_type == "text/plain":
            return uploaded_file.read().decode()
        elif file_type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text[:5000]
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return docx2txt.process(uploaded_file)[:5000]
        elif file_type.startswith("image/"):
            img = Image.open(uploaded_file)
            return f"[Image uploaded: {uploaded_file.name}, size: {img.size}]"
    except:
        return f"[File: {uploaded_file.name}]"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_groq(api_msgs):
    return client.chat.completions.create(
        model=MODEL,
        messages=api_msgs,
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
    try:
        st.image("Faiz Chatbot Logo.png", use_container_width=True)
    except Exception:
        pass

    st.markdown("## Faiz ChatBot")
    st.caption("All-purpose AI assistant")
    st.divider()

    if st.button("New Chat", use_container_width=True, type="primary", key="new_chat"):
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

# Custom chat input with plus button for file upload
col1, col2 = st.columns([12, 1])

with col1:
    prompt = st.chat_input("Ask me anything...")

with col2:
    # Plus button for file upload
    uploaded_file = st.file_uploader(
        "📎", 
        type=['png', 'jpg', 'jpeg', 'pdf', 'docx', 'txt', 'csv'],
        label_visibility="collapsed",
        key="file_uploader_plus"
    )
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"✅ {uploaded_file.name}")

# Handle the query
if prompt:
    final_prompt = prompt
    file_content = None
    
    # Process uploaded file if exists
    if st.session_state.uploaded_file:
        file_content = extract_text_from_file(st.session_state.uploaded_file)
        if file_content:
            final_prompt = f"[FILE CONTEXT from {st.session_state.uploaded_file.name}]:\n{file_content}\n\n[USER QUESTION]:\n{prompt}"
    
    # Store user message with file indicator
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
            messages_for_api += [{"role": m["role"], "content": m["content"] if isinstance(m["content"], str) else m["content"]["text"]} 
                                for m in st.session_state.messages[-20:]]
            
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