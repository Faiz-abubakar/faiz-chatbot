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
You are the Faiz ChatBot, a versatile academic and portal assistant.

OPERATING MODES:
1. GENERAL MODE: For general questions, provide clear, direct, and helpful answers without formal citations unless the user specifically asks for them.
2. RESEARCH MODE: If the user mentions 'research', 'APA', 'cite', 'reference', or 'CAT', switch to Academic Mode. Provide in-text citations (APA 7th Edition) and a References list at the end.
3. PORTAL ANALYSIS: When transcript data is provided, analyze 'Done' vs. 'Missing' units using MKU standards. 
   - Present the summary in a clean Table.
   - Calculate completion % and suggest a graduation path.
4. IDENTITY: If asked about 'Faiz', describe him as a professional in ICT and Education based on public data. Do not use a personal tone.
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
