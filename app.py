import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq

st.set_page_config(page_title="Faiz ChatBot", page_icon="🎓", layout="wide")

st.markdown('<link rel="stylesheet" href="https://cloudflare.com">', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history_titles" not in st.session_state:
    st.session_state.history_titles = []

def create_progress_chart(done, remaining):
    """Creates a professional pie chart for academic audits."""
    data = {'Status': ['Completed', 'Remaining'], 'Units': [done, remaining]}
    df = pd.DataFrame(data)
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ['#0d6efd', '#e9ecef'] # Professional Blue and Grey
    ax.pie(df['Units'], labels=df['Status'], autopct='%1.1f%%', colors=colors, startangle=90, wedgeprops={'edgecolor': 'white'})
    ax.axis('equal')
    plt.title("Graduation Progress Audit", fontsize=12, pad=20)
    return fig

with st.sidebar:
    st.markdown('<h2><i class="fa-solid fa-microchip"></i> Faiz ChatBot</h2>', unsafe_allow_html=True)
    
    if st.button("Clear Conversation"): 
        st.session_state.messages = []
        st.session_state.history_titles = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### <i class='fa-solid fa-clock-rotate-left'></i> Recent Chats", unsafe_allow_html=True)
    
    if not st.session_state.history_titles:
        st.caption("No recent chats yet.")
    else:
        for title in reversed(st.session_state.history_titles):
            st.write(f"• {title[:25]}...")

    st.markdown("---")
    with st.expander("User Guide", expanded=True):
        st.write("• **Research:** Ask any academic topic.")
        st.write("• **Audit:** Paste transcript for a chart.")
        st.write("• **APA:** Get formatted citations.")

st.markdown('<h1><i class="fa-solid fa-graduation-cap"></i> Faiz ChatBot</h1>', unsafe_allow_html=True)
st.markdown("##### *Academic Research & Portal Intelligence Partner*")
st.markdown("---")

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("API Key not found. Please check your Streamlit Secrets.")
    st.stop()

ACADEMIC_TRAINING = """
You are the Faiz ChatBot. 
- If a user pastes transcript data, analyze it and provide a summary table.
- At the end of every response, provide 2-3 'Next Step' suggestions.
- If asked for research, use APA 7th Edition style.
- Keep answers professional and educational.
"""

# CHAT HISTORY
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a research question or paste your transcript..."):
    # Update History
    if prompt not in st.session_state.history_titles:
        st.session_state.history_titles.append(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Analyzing data..."):
        try:
            # Call Groq API
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "system", "content": ACADEMIC_TRAINING}] + st.session_state.messages,
                temperature=0.3
            )
            
            response = completion.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response)
            
                if any(word in prompt.lower() for word in ["transcript", "units", "audit", "grades"]):
                    st.markdown("---")
                    st.markdown("### Visual Progress Report")

                    fig = create_progress_chart(30, 12)
                    st.pyplot(fig)
                
                st.markdown('<p style="color: grey;"><i class="fa-solid fa-bolt"></i> <i>Type "Continue" if needed.</i></p>', unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {e}")
