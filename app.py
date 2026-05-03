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

ACADEMIC_TRAINING = """
You are the Faiz ChatBot, a real-time researcher and portal analyst.

CRITICAL RULES:
1. NO APA CITATIONS: Never provide a 'References' section or academic citations. Provide direct facts only.
2. KENYAN CONTEXT: Prioritize Kenyan institutions and local information.
3. PORTAL ANALYSIS: Generate summary tables for transcript data.
4. DOCUMENT ANALYSIS: Analyze text from uploaded files provided by the user.
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

if prompt := st.chat_input("Ask a question or discuss your uploaded file..."):
    final_prompt = prompt
    if uploaded_file:
        final_prompt = f"File Context: {uploaded_file.name}. Question: {prompt}"

    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Processing..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": ACADEMIC_TRAINING}] + st.session_state.messages,
                temperature=0.3
            )
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
