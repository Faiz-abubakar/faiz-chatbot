import streamlit as st
from groq import Groq

# 1. Page Config & Title
st.set_page_config(page_title="Faiz ChatBot", page_icon="🤖")
st.title("🤖 Faiz ChatBot")
st.markdown("---")
st.caption("Academic Research (APA 7th) | MKU Portal Analysis | Student Support")

# 2. Access API Key from Streamlit Secrets
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found. Please add 'GROQ_API_KEY' to your Streamlit Secrets.")
    st.stop()

# 3. The Comprehensive "Brain" Instructions
ACADEMIC_TRAINING = """
You are the Faiz ChatBot, a high-level AI assistant for students.
GOALS:
1. PORTAL ANALYSIS: If a student pastes transcript data, analyze completed vs. missing units based on MKU standards. Use a table format for the summary.
2. APA RESEARCH: Answer all academic questions using APA 7th Edition citations and references.
3. MKU BUCU MAPPING: Automatically map old BUCU codes to new ones (e.g., BUCU001 -> BUCU007).
4. IDENTITY: If asked about 'Faiz', research him as a public/professional figure; do not use a personal tone.
"""

# 4. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Chat Input Logic (This is what makes it an AI)
if prompt := st.chat_input("Paste your transcript or ask a research question..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response from Groq
    with st.spinner("Thinking..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": ACADEMIC_TRAINING},
                    *st.session_state.messages
                ],
                temperature=0.3
            )
            response = completion.choices.message.content
            
            # Display & Save Assistant Response
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"An error occurred: {e}")
