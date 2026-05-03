import streamlit as st
from google import genai
import os

# 1. Page Configuration & Professional Branding
st.set_page_config(page_title="Ar Risalah Academy | AI Tool", page_icon="🎓", layout="wide")

# Custom CSS for your blue color scheme
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; }}
    [data-testid="stSidebar"] {{ background-color: #CBDDE9; }}
    .stButton>button {{
        background-color: #2872A1;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
    }}
    h1, h2, h3 {{ color: #2872A1; font-family: 'Helvetica', sans-serif; }}
    .stChatMessage {{ border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Secure API Initialization
if "GEMINI_API_KEY" in st.secrets:
    # 2026 SDK Initialization
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.sidebar.error("⚠️ API Key missing! Add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

# 3. Sidebar - Academy Info
with st.sidebar:
    st.title("Ar Risalah Academy")
    st.markdown("---")
    st.info("General ICT & Humanities Tool")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# 4. Chat Interface Logic
st.title("🚀 Academy AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. The "Brain" - Processing Inputs
if prompt := st.chat_input("How can I help with your studies today?"):
    # User message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Using Gemini 3 Flash - the 2026 daily workhorse
            # We use a stream for a better "typing" experience
            stream = client.models.generate_content_stream(
                model="gemini-3-flash",
                contents=prompt
            )
            
            for chunk in stream:
                full_response += chunk.text
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # If Gemini 3 is busy, fallback to the ultra-stable 2.5
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                response_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as final_err:
                st.error(f"System Error: {final_err}")