import streamlit as st
from groq import Groq
import PyPDF2
import docx2txt
from tenacity import retry, stop_after_attempt, wait_exponential

st.set_page_config(page_title="Faiz ChatBot", page_icon="⚡", layout="wide")

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found. Please check Streamlit Secrets.")
    st.stop()

CLAUDE_PROTOCOL = """
You are Faiz ChatBot, a direct, concise academic assistant.
- Be extremely concise (1-3 sentences when possible)
- No preamble or postamble - answer directly
- No citations or markdown formatting
- Prioritize Kenyan context
- Do what has been asked; nothing more, nothing less
"""

def extract_file_content(uploaded_file):
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode()
    elif uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        return " ".join([page.extract_text() for page in reader.pages[:5]])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return docx2txt.process(uploaded_file)
    return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_completion(messages):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.2,
        max_tokens=1024
    )

# Sidebar
with st.sidebar:
    st.image("Faiz Chatbot Logo.png", use_container_width=True)
    st.markdown("### Faiz ChatBot")
    st.caption("Academic Research & Portal Intelligence Partner")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Upload Image or Document", type=['png', 'jpg', 'pdf', 'docx', 'txt'], 
                                      help="PNG, JPG, PDF, DOCX, TXT (Max 200MB)")
    
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption("v2.0 | Powered by Groq")

# Main chat area
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question..."):
    final_prompt = prompt
    file_content = None
    
    if uploaded_file and uploaded_file.name:
        file_content = extract_file_content(uploaded_file)
        if file_content:
            final_prompt = f"Context from {uploaded_file.name}:\n{file_content[:3000]}\n\nQuestion: {prompt}"
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Thinking..."):
        try:
            messages_for_api = [{"role": "system", "content": CLAUDE_PROTOCOL}]
            messages_for_api += st.session_state.messages[-10:]
            
            completion = get_completion(messages_for_api)
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            if file_content:
                st.toast(f"✅ Processed: {uploaded_file.name}", icon="📄")
                
        except Exception as e:
            st.error(f"Error: {e}")