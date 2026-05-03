import streamlit as st
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="Faiz ChatBot", page_icon="🎓", layout="wide")

# 2. LOAD FONT AWESOME (Pro Icons)
st.markdown('<link rel="stylesheet" href="https://cloudflare.com">', unsafe_allow_html=True)

# 3. INITIALIZE SESSION STATES
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history_titles" not in st.session_state:
    st.session_state.history_titles = []

# 4. SIDEBAR
with st.sidebar:
    st.title("Faiz ChatBot")
    
    if st.button("Clear Conversation"): 
        st.session_state.messages = []
        st.session_state.history_titles = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Recent Chats")
    
    if not st.session_state.history_titles:
        st.caption("No recent chats yet.")
    else:
        for title in reversed(st.session_state.history_titles):
            st.write(f"• {title[:25]}...")

    st.markdown("---")
    with st.expander("User Guide", expanded=True):
        st.write("• Academic Research")
        st.write("• Portal Transcript Audit")
        st.write("• APA 7th Citations")

# 5. MAIN HEADER
st.title("🎓 Faiz ChatBot")
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
    if prompt not in st.session_state.history_titles:
        st.session_state.history_titles.append(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- FIX: Correct Indentation starts here ---
    with st.spinner("Processing..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "system", "content": ACADEMIC_TRAINING}] + st.session_state.messages,
                temperature=0.3
            )
            
            # Use choice 0 to get the content
            response = completion.choices[0].message.content
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {e}")
