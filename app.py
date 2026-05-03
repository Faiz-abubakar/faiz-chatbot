import streamlit as st
from groq import Groq
import PyPDF2
import docx2txt
from tenacity import retry, stop_after_attempt, wait_exponential

st.set_page_config(page_title="Faiz ChatBot", page_icon="Faiz Chatbot Logo.png", layout="wide")

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found. Please check Streamlit Secrets.")
    st.stop()

CLAUDE_PROTOCOL = """
You are Faiz ChatBot, a direct, concise academic assistant.
- Be extremely concise (1-3 sentences when possible)
- No preamble like "Here is the answer" - answer directly
- No postamble or summaries unless asked
- No citations or markdown formatting
- Prioritize Kenyan context
- Do what has been asked; nothing more, nothing less
"""

def extract_file_content(uploaded_file):
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode()
    elif uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        return " ".join([page.extract_text() for page in reader.pages])
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

with st.sidebar:
    st.image("Faiz Chatbot Logo.png", use_container_width=True)
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

st.image("Faiz Chatbot Logo.png", width=150)
st.markdown("##### *Academic Research & Portal Intelligence Partner*")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_file = st.file_uploader("Upload context", type=['png', 'jpg', 'pdf', 'docx', 'txt'], label_visibility="collapsed")

if prompt := st.chat_input("Ask anything..."):
    final_prompt = prompt
    if uploaded_file:
        file_content = extract_file_content(uploaded_file)
        if file_content:
            final_prompt = f"Context from {uploaded_file.name}:\n{file_content[:3000]}\n\nQuestion: {prompt}"
    
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Processing..."):
        try:
            completion = get_completion([{"role": "system", "content": CLAUDE_PROTOCOL}] + st.session_state.messages[-10:])
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")