import streamlit as st
from groq import Groq
import pandas as pd
import matplotlib.pyplot as plt

# 1. PAGE CONFIGURATION
# Setting the logo file as the page_icon makes it the icon for the web page tab.
st.set_page_config(
    page_title="Faiz ChatBot",
    page_icon="Faiz Chatbot Logo.png",
    layout="wide"
)

# 2. Access API Key
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found in Secrets.")
    st.stop()

# 3. Brain Instructions (No APA)
ACADEMIC_TRAINING = """
You are the Faiz ChatBot, a professional MKU Portal & Research Assistant.

STRICT RULES:
1. NO APA CITATIONS: Do not provide references or 'Retrieved from' links.
2. PORTAL ANALYSIS: Provide summary tables for transcript data.
3. TONE: Helpful and direct.
"""

# 4. SIDEBAR (Bigger Logo)
with st.sidebar:
    # Setting width to 250 or more makes it significantly larger on the side panel.
    st.image("Faiz Chatbot Logo.png", width=250)
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# 5. MAIN HEADER (Logo only)
# Per your request, the text heading has been removed, leaving only the logo image.
st.image("Faiz Chatbot Logo.png", width=120)
st.markdown("##### *Academic Research & Portal Intelligence Partner*")
st.markdown("---")

# 6. Initialize & Display Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Chat Input Logic
if prompt := st.chat_input("Ask a question or paste your transcript..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Processing..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": ACADEMIC_TRAINING}] + st.session_state.messages,
                temperature=0.3
            )
            # Standard way to access the assistant's content in the latest Groq SDK
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
