import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

st.set_page_config(page_title="Faiz ChatBot", page_icon="Faiz Chatbot Logo.png", layout="wide")

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found. Please check Streamlit Secrets.")
    st.stop()

CLAUDE_PROTOCOL = """
You are Faiz ChatBot, a helpful academic assistant.
- Answer questions helpfully and thoroughly
- Provide code when asked for code
- Explain concepts clearly
- Be friendly and conversational
- Prioritize Kenyan context when relevant
"""

def extract_file_content(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        if uploaded_file.type == "text/plain":
            return uploaded_file.read().decode()
    except:
        pass
    return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_completion(messages):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=2048
    )

# Sidebar
with st.sidebar:
    st.image("Faiz Chatbot Logo.png", use_container_width=True)
    st.markdown("# Faiz ChatBot")
    st.markdown("#### Your Academic Research Partner")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Upload Document", type=['txt'])
    
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat area
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you today?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question..."):
    final_prompt = prompt
    if uploaded_file:
        file_content = extract_file_content(uploaded_file)
        if file_content:
            final_prompt = f"File content:\n{file_content[:2000]}\n\nQuestion: {prompt}"
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Thinking..."):
        try:
            messages_for_api = [{"role": "system", "content": CLAUDE_PROTOCOL}]
            messages_for_api += st.session_state.messages[-20:]
            
            completion = get_completion(messages_for_api)
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
                
        except Exception as e:
            st.error(f"Error: {e}")