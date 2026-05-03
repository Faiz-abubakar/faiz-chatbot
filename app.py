import streamlit as st

st.title("Faiz AI Assistant")
st.write("Welcome! I am an AI trained on Faiz Ywaya Abubakar's professional profile.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask me about Faiz's ICT skills..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Here you would connect to an API (like OpenAI or Poe) to get a real answer
    response = f"Faiz is a certified TSC educator currently studying AI at UoN. (This is a preview response)"
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
