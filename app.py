import streamlit as st
from groq import Groq
import logging
import base64
import time
import pandas as pd
import matplotlib.pyplot as plt

# 1. Configure logging & Page Config
logging.basicConfig(level=logging.INFO)
st.set_page_config(
    page_title="Faiz ChatBot - Academic AI",
    page_icon="🎓",
    layout="wide"
)

# 2. API Setup (Using Groq for speed/free tier)
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found. Please add 'GROQ_API_KEY' to Streamlit Secrets.")
    st.stop()

# 3. UI Helpers (from your Streamly example)
def img_to_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return None

# 4. Data Visualization Logic
def create_progress_chart(done, remaining):
    data = {'Status': ['Completed', 'Remaining'], 'Units': [done, remaining]}
    df = pd.DataFrame(data)
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.pie(df['Units'], labels=df['Status'], autopct='%1.1f%%', colors=['#dc143c', '#f0f2f6'], startangle=90)
    ax.axis('equal')
    plt.tight_layout()
    return fig

# 5. Header Section (Streamly Style)
logo_base64 = img_to_base64("logo.png")
if logo_base64:
    st.markdown(
        f"""
        <h1>
            <span style="color: crimson;">Faiz ChatBot</span> - Academic Assistant 
            <img src="data:image/png;base64,{logo_base64}" width="50" style="border-radius: 10px; vertical-align: middle;"/>
        </h1>
        """, 
        unsafe_allow_html=True
    )
else:
    st.title("Faiz ChatBot - Academic Assistant")

st.markdown("---")

# 6. Sidebar (Streamly Style)
with st.sidebar:
    st.image("logo.png", width=100)
    st.markdown("### About Faiz ChatBot")
    st.info("""
        **Powered by Llama 3.3**
        
        This assistant is designed to:
        - Analyze MKU Portal Transcripts.
        - Generate APA 7th Edition Research.
        - Map BUCU old-to-new codes.
    """)
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# 7. Initialize Conversation
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Faiz ChatBot. How can I help with your MKU research or portal audit today?"}
    ]

# 8. Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Chat Logic
if prompt := st.chat_input("Ask a research question or paste your transcript..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Analyzing..."):
        try:
            # Training instructions
            system_instruction = "You are Faiz ChatBot. Provide academic research in APA 7th format if asked. For transcripts, provide a summary table."
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages,
                temperature=0.3
            )
            
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
                
                # Visual Audit Logic
                if any(x in prompt.lower() for x in ["audit", "transcript", "units"]):
                    st.divider()
                    st.subheader("Visual Progress Report")
                    fig = create_progress_chart(30, 12) # Example data
                    st.pyplot(fig)
                
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
