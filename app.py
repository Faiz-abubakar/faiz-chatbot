import streamlit as st
import google.generativeai as genai

# 1. Page Configuration & Custom Theme
st.set_page_config(page_title="Faiz AI General Tool", page_icon="🛠️", layout="wide")

# Custom CSS for your #CBDDE9 and #2872A1 scheme
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #f0f4f7;
    }}
    .stSidebar {{
        background-color: #CBDDE9;
    }}
    /* Style the buttons and headers */
    .stButton>button {{
        background-color: #2872A1;
        color: white;
        border-radius: 8px;
    }}
    h1, h2, h3 {{
        color: #2872A1;
    }}
    </style>
    """, unsafe_allow_stdio=True)

# 2. Securely Initialize Gemini 3 Flash
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.sidebar.error("⚠️ API Key not found in secrets.toml")
    st.stop()

# 3. App Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150/2872A1/FFFFFF?text=Faiz+Design", width=100)
    st.title("Settings")
    # Using the Gemini 3 Flash model (2026 stable)
    model_choice = st.selectbox("Model Version", ["gemini-3-flash-preview", "gemini-2.5-flash"])
    st.info("This tool is optimized for ICT tasks, Graphics Design brainstorming, and general research.")

# 4. Main Interface
st.title("🚀 Faiz AI General Tool")
st.markdown("---")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. The Logic
if prompt := st.chat_input("Ask anything..."):
    # Show user input
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Response
    model = genai.GenerativeModel(model_choice)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Simple direct response for a general tool
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error: {e}")