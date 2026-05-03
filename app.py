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
You are the Faiz ChatBot, a high-level academic assistant.
GOALS:
1. PORTAL ANALYSIS: When a student pastes transcript data, analyze it. Identify Done vs. Missing units based on MKU standards. 
   - Use tables for clarity.
   - Automatically map BUCU001-005 to the new BUCU007-011 codes.
   - Calculate completion percentage.
2. APA RESEARCH: Every academic answer MUST include APA 7th Edition in-text citations and a References list at the end.
3. IDENTITY: If asked about 'Faiz', research him as a professional figure in ICT and Education. Do not use a personal or 'assistant' tone.
"""

# 4. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Chat Input Logic
if prompt := st.chat_input("Paste your transcript or ask a research question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[
                    {"role": "system", "content": ACADEMIC_TRAINING},
                    *st.session_state.messages
                ],
                temperature=0.3
            )
            
            # THE FIX IS HERE: Added [0]
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"An error occurred: {e}")
