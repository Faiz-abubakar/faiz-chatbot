import streamlit as st
from groq import Groq

# Access your API Key from Streamlit Secrets
api_key = st.secrets["gsk_lbGfPLyIwDVX0ug6b9tZWGdyb3FYiyBXAkv0d3LiYO2DXwyI4WAIY"]
client = Groq(api_key=api_key)

# ACADEMIC SYSTEM PROMPT: This defines the AI's new persona
ACADEMIC_TRAINING = """
You are the MKU Academic Research Assistant. Your sole purpose is to assist students with research, CAT preparation, and academic writing.

STRICT RULES:
1. APA FORMAT: Every academic answer must follow APA 7th Edition guidelines. Include in-text citations (Author, Year) and a 'References' section at the end.
2. MKU CONTEXT: When relevant, provide information consistent with Mount Kenya University's academic standards and the UniRP system.
3. NO PERSONAL INFO: Do not talk about Faiz Abubakar's portfolio or personal life. If asked about 'Faiz', treat him as a general search subject or a public figure based on available internet data; do not refer to this app as his personal assistant.
4. OBJECTIVITY: Maintain a formal, academic tone. Avoid slang or casual language.
5. RESEARCH FOCUS: Help students structure their CATs, explain complex theories, and provide study summaries.
"""

st.set_page_config(page_title="MKU Research Assistant", page_icon="🎓")
st.title("🎓 MKU Academic Research Assistant")
st.caption("AI-powered research support following APA 7th Edition standards.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter your research topic or CAT question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Groq API with the new Academic Prompt
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile", # This model is excellent for logic and citations
        messages=[
            {"role": "system", "content": ACADEMIC_TRAINING},
            *st.session_state.messages
        ],
        temperature=0.3 # Lower temperature makes the AI more factual and less "creative"
    )
    
    response = completion.choices.message.content
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
