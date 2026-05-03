import streamlit as st
from groq import Groq

api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

# The "Brain" now includes MKU Portal Logic
ACADEMIC_TRAINING = """
You are the MKU Academic Research & Portal Assistant. 
Your goals:
1. APA RESEARCH: Answer all academic questions using APA 7th Edition citations.
2. PORTAL ANALYSIS: If a student pastes their transcript or course outline, analyze it.
   - Match 'Done' units against the 'Course Outline'.
   - Identify 'Remaining' units.
   - Check BUCU unit mappings (e.g., BUCU001 is now BUCU007).
   - Calculate completion % and suggest a graduation timeline.
3. NO PERSONAL INFO: Do not talk about Faiz unless it's a general web search.
"""

st.set_page_config(page_title="MKU Student Portal & Research AI", page_icon="🎓")
st.title("🎓 MKU Student Portal & Research AI")
st.markdown("Paste your **Transcript** or **Course Outline** below for a graduation audit, or ask a research question.")

# ... (rest of the chat logic we used before) ...
