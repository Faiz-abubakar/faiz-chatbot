import streamlit as st
from groq import Groq
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Faiz ChatBot",
    page_icon="Faiz Chatbot Logo.png",
    layout="wide"
)

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found. Please check Streamlit Secrets.")
    st.stop()

CLAUDE_PROTOCOL = """
You are Faiz ChatBot, an interactive assistant built on the Claude Protocol. 
TONE AND STYLE:
- Be concise, direct, and to the point. 
- Minimize output tokens. If you can answer in 1-3 sentences, do so.
- NEVER use unnecessary preamble (e.g., "The answer is...", "Based on the info...") or postamble.
- Match the level of detail to the complexity of the query.
- Use Github-flavored markdown for formatting. 
- Only use emojis if explicitly requested.

PROFESSIONAL OBJECTIVITY:
- Prioritize technical accuracy over validating user beliefs. 
- Focus on facts and problem-solving. No unnecessary superlatives or praise.
- Disagree when necessary and provide respectful correction.

ACADEMIC/PORTAL LOGIC:
- Analyze MKU transcripts via tables. 
- Prioritize Kenyan context. 
- NO APA references or citations.
"""

with st.sidebar:
    st.image("Faiz Chatbot Logo.png", use_container_width=True)
    st.markdown("---")
    st.markdown("### Upload Lab")
    uploaded_file = st.file_uploader("Upload Image or Document", type=['png', 'jpg', 'pdf', 'docx', 'txt'])
    
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' ready.")

    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

st.image("Faiz Chatbot Logo.png", width=150)
st.markdown("##### *Your Academic Research & Portal Intelligence Partner*")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question..."):
    final_prompt = prompt
    if uploaded_file:
        final_prompt = f"File: {uploaded_file.name}. Task: {prompt}"

    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Processing..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": CLAUDE_PROTOCOL}] + st.session_state.messages,
                temperature=0.2
            )
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
