import streamlit as st
# Try the modern import first, fallback if the server is cached
try:
    from google import genai
except ImportError:
    import google.generativeai as genai

# 1. Page Config & CSS (Fixed parameter)
st.set_page_config(page_title="Faiz AI General Tool", page_icon="🛠️")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; }}
    [data-testid="stSidebar"] {{ background-color: #CBDDE9; }}
    .stButton>button {{
        background-color: #2872A1;
        color: white;
        border-radius: 8px;
    }}
    h1, h2, h3, p {{ color: #2872A1; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Client Initialization
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    # Handle both new and old SDK versions automatically
    try:
        client = genai.Client(api_key=api_key)
        use_new_sdk = True
    except AttributeError:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        use_new_sdk = False
else:
    st.error("Missing GEMINI_API_KEY in secrets!")
    st.stop()

# 3. Chat Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("How can I help with ICT or Design?"):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        if use_new_sdk:
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            output = response.text
        else:
            response = model.generate_content(prompt)
            output = response.text
            
        st.write(output)
        st.session_state.messages.append({"role": "assistant", "content": output})