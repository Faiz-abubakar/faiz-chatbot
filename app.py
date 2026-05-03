import streamlit as st
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="Faiz ChatBot", page_icon=None, layout="wide")

# 2. LOAD FONT AWESOME (Pro Icons)
st.markdown('<link rel="stylesheet" href="https://cloudflare.com">', unsafe_allow_html=True)

# 3. SIDEBAR WITH PRO ICONS
with st.sidebar:
    st.markdown('<h2><i class="fa-solid fa-microchip"></i> Faiz ChatBot</h2>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Custom Styled Button using HTML/CSS (replacing the standard emoji button)
    if st.button("Clear Conversation"): 
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #0d6efd; color: #212529;">
        <p><b><i class="fa-solid fa-circle-info"></i> User Guide</b></p>
        <p><i class="fa-solid fa-magnifying-glass"></i> Academic Research</p>
        <p><i class="fa-solid fa-file-export"></i> Portal Transcript Audit</p>
        <p><i class="fa-solid fa-quote-right"></i> APA 7th Citations</p>
    </div>
    """, unsafe_allow_html=True)

# 4. MAIN HEADER (No Emojis)
st.markdown('<h1><i class="fa-solid fa-graduation-cap"></i> Faiz ChatBot</h1>', unsafe_allow_html=True)
st.markdown("##### *Academic Research & Portal Intelligence Partner*")
st.markdown("---")

# 5. Access API Key
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found in Secrets.")
    st.stop()

# 6. Brain Instructions
ACADEMIC_TRAINING = """
You are the Faiz ChatBot. 
RULES:
1. End every response with 2-3 'Next Steps' starting with 'Would you like to...'.
2. If asked to 'Continue', pick up exactly where you left off.
3. Use professional, clear language.
"""

# 7. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 8. Display Chat
for message in st.session_state.messages:
    # We use 'user' and 'assistant' roles which Streamlit styles automatically
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Chat Input with Smart Suggestions
if prompt := st.chat_input("Type your research question or paste transcript data..."):
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
            response = completion.choices.message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
                # Tip with icon instead of bulb emoji
                st.markdown('<p style="color: grey;"><i class="fa-solid fa-bolt"></i> <i>Tip: Type "Continue" if the response was cut off.</i></p>', unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.markdown(f'<p style="color: red;"><i class="fa-solid fa-triangle-exclamation"></i> Error: {e}</p>', unsafe_allow_html=True)
