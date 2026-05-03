import streamlit as st
from google import genai

# 1. Page Config & Professional Theme
st.set_page_config(page_title="Faiz AI General Tool", page_icon="🛠️", layout="wide")

# Applying your specific #CBDDE9 and #2872A1 color scheme
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #FFFFFF;
    }}
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: #CBDDE9;
    }}
    /* Button and Header styling */
    .stButton>button {{
        background-color: #2872A1;
        color: white;
        border-radius: 8px;
        border: none;
    }}
    h1, h2, h3, p {{
        color: #2872A1;
    }}
    /* Chat message bubble styling */
    .stChatMessage {{
        border-radius: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Securely Initialize Gemini Client
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.sidebar.error("⚠️ API Key not found in Streamlit Secrets.")
    st.stop()

# 3. Sidebar Information
with st.sidebar:
    st.title("Faiz Design Tool")
    st.markdown("---")
    st.write("**Location:** Nairobi / Nakuru")
    st.write("**Focus:** ICT, STEM, & Graphics")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# 4. Main Chat Interface
st.title("🚀 Faiz AI General Tool")
st.caption("Powered by Gemini 3 Flash")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Logic
if prompt := st.chat_input("How can I assist with your ICT or Design project?"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Streamed Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Using Gemini 3 Flash for maximum speed
            response = client.models.generate_content_stream(
                model="gemini-3-flash",
                contents=prompt
            )
            
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Developer Error: {e}")