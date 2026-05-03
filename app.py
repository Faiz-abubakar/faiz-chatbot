import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
import requests
from bs4 import BeautifulSoup
import json
import PyPDF2
import docx2txt
from PIL import Image
import io

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Faiz ChatBot",
    page_icon="🤖", 
    layout="wide"
)

# ── API Setup ──────────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API key missing. Add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are Faiz ChatBot, a powerful all-purpose AI assistant built for Kenyan users.

CAPABILITIES:
- Answer any question accurately and thoroughly.
- Write and debug code in any language.
- Provide local Kenyan context (M-Pesa, KRA, Nairobi life, Swahili/Sheng).
- Analyze uploaded documents and images.

STYLE:
- Helpful, thorough, and conversational.
- Use markdown for clear formatting.
"""

# ── Helper Functions ──────────────────────────────────────────────────────────
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
                text += page.extract_text() or ""
            return text[:7000]
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return docx2txt.process(uploaded_file)[:7000]
        elif file_type.startswith("image/"):
            return f"[Image Attachment: {uploaded_file.name}]"
        else:
            return f"[Binary file: {uploaded_file.name}]"
    except Exception as e:
        return f"Error reading file {uploaded_file.name}: {e}"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_groq(api_msgs):
    return client.chat.completions.create(
        model=MODEL,
        messages=api_msgs,
        temperature=0.7,
        max_tokens=4096,
        stream=True # Enabled streaming for a better UI experience
    )

# ── Session State ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Faiz ChatBot")
    st.caption("v3.0 | Powered by Groq")
    st.divider()

    if st.button("＋ New Chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.uploaded_file_data = None
        st.rerun()
    
    st.markdown("### Attachments")
    uploaded = st.file_uploader(
        "Upload a file", 
        type=['png', 'jpg', 'jpeg', 'pdf', 'docx', 'txt'],
        label_visibility="collapsed"
    )
    if uploaded:
        st.session_state.uploaded_file_data = {
            "name": uploaded.name,
            "content": extract_text_from_file(uploaded)
        }
        st.success(f"Attached: {uploaded.name}")

# ── Main Chat Area ────────────────────────────────────────────────────────────
# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, dict):
            st.markdown(content["text"])
            st.caption(f"📎 {content['file']}")
        else:
            st.markdown(content)

# Chat Input
if prompt := st.chat_input("Ask me anything..."):
    # 1. Handle File Logic
    final_prompt = prompt
    user_display_content = prompt
    
    if st.session_state.uploaded_file_data:
        file_name = st.session_state.uploaded_file_data["name"]
        file_text = st.session_state.uploaded_file_data["content"]
        final_prompt = f"[CONTEXT FROM FILE {file_name}]:\n{file_text}\n\n[USER QUESTION]: {prompt}"
        user_display_content = {"text": prompt, "file": file_name}
    
    # 2. Update UI with User Message
    st.session_state.messages.append({"role": "user", "content": user_display_content, "actual_prompt": final_prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if st.session_state.uploaded_file_data:
            st.caption(f"📎 {st.session_state.uploaded_file_data['name']}")

    # 3. Generate AI Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Prepare API Payload
        api_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in st.session_state.messages[-15:]: # Keep last 15 messages for memory
            role = m["role"]
            # Use the full context prompt for the most recent message if it had a file
            content = m.get("actual_prompt") if "actual_prompt" in m else (m["content"] if isinstance(m["content"], str) else m["content"]["text"])
            api_msgs.append({"role": role, "content": content})

        try:
            stream = call_groq(api_msgs)
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Clear file after successfully answering
            st.session_state.uploaded_file_data = None
            
        except Exception as e:
            st.error(f"Error: {e}")