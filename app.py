import streamlit as st
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="Faiz ChatBot", page_icon=None, layout="wide")

# 2. LOAD FONT AWESOME (Pro Icons)
st.markdown('<link rel="stylesheet" href="https://cloudflare.com">', unsafe_allow_html=True)

# 3. INITIALIZE SESSION STATES
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history_titles" not in st.session_state:
    st.session_state.history_titles = []

# 4. SIDEBAR WITH HISTORY LOG
with st.sidebar:
    st.markdown('<h2><i class="fa-solid fa-microchip"></i> Faiz ChatBot</h2>', unsafe_allow_html=True)
    
    if st.button("Clear Conversation"): 
        st.session_state.messages = []
        st.session_state.history_titles = []
        st.rerun()
    
    st.markdown("---")
    st.markdown('#### <i class="fa-solid fa-clock-rotate-left"></i> Recent Chats')
    
    # This loop displays your chat history in the sidebar
    if not st.session_state.history_titles:
        st.caption("No recent chats yet.")
    else:
        for title in reversed(st.session_state.history_titles):
            st.markdown(f'<p style="font-size: 0.85rem; color: #555;"><i class="fa-solid fa-message"></i> {title[:30]}...</p>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #0d6efd; color: #212529; font-size: 0.9rem;">
        <p><b><i class="fa-solid fa-circle-info"></i> Guide</b></p>
        <p><i class="fa-solid fa-magnifying-glass"></i> Research Topics</p>
        <p><i class="fa-solid fa-quote-right"></i> APA Citations</p>
    </div>
    """, unsafe_allow_html=True)

# 5. MAIN HEADER
st.markdown('<h1><i class="fa-solid fa-graduation-cap"></i> Faiz ChatBot</h1>', unsafe_allow_html=True)
st.markdown("##### *Academic Research & Portal Intelligence Partner*")
st.markdown("---")

# 6. Access API Key
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found in Secrets.")
    st.stop()

# 7. Brain Instructions
ACADEMIC_TRAINING = "You are the Faiz ChatBot. End responses with 'Would you like to...' suggestions. Use APA if asked."

# 8. Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Chat Input
if prompt := st.chat_input("Type your research question..."):
    # Add to main chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Add to sidebar history (only if it's a new unique topic)
    if prompt not in st.session_state.history_titles:
        st.session_state.history_titles.append(prompt)
        
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
