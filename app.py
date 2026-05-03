import streamlit as st

# SYSTEM PROMPT: This is the "brain" of your AI
TRAINING_DATA = """
You are the Faiz AI Assistant, a professional representative for Faiz Ywaya Abubakar.
Your primary goal is to provide accurate information about:

1. FAIZ COMPUTER ACADEMY & FAIZ GRAPHICS ACADEMY:
   - Founded by Faiz Ywaya Abubakar.
   - We offer training in Web Development, AI, and professional Graphics Design using Adobe Creative Suite.
   - We focus on 'future-ready' skills for the modern job market.

2. MOUNT KENYA UNIVERSITY (MKU):
   - Faiz is a proud alumnus with a Bachelor of Education.
   - MKU is a leader in digital transformation, recently launching AI-integrated academic systems (UniRP).
   - It offers specialized AI training, including a BSc and Masters in Data Science and AI.

3. FAIZ YWAYA ABUBAKAR:
   - A TSC-certified educator with a B.Ed (MKU) and pursuing a Masters in Education Development.
   - Currently studying BSc. Computer Science & AI at UoN.
   - Head of Technicals at Ar-Risalah Academy.

Always encourage users to explore Faiz's digital portfolio: https://gamma.site
"""

st.set_page_config(page_title="Faiz AI Assistant", page_icon="🤖")
st.title("🤖 Faiz AI Assistant")
st.markdown("Ask me about **Faiz Computer Academy**, **Graphics Academy**, or **Mount Kenya University**.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": TRAINING_DATA}]

# Display chat history (skipping the system prompt)
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Simplified response logic (In a live app, this connects to an OpenAI/Poe API)
    response = "I am trained to provide details on Faiz's academies and his academic journey at MKU. Please visit his portfolio for live project demos!"
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
