import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

st.set_page_config(
    page_title="Faiz ChatBot",
    page_icon="Faiz Chatbot Logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif !important;
}

/* ── App background ── */
.stApp { background: #0b0d12 !important; }
.main .block-container { padding-top: 1rem !important; padding-bottom: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #10131a !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
section[data-testid="stSidebar"] > div { padding: 1.2rem 1rem !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label { color: #8a909e !important; font-size: 12px !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #e2e4ea !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
hr { border-color: rgba(255,255,255,0.06) !important; margin: 0.5rem 0 !important; }

/* ── All buttons base ── */
.stButton > button {
    font-family: 'Sora', sans-serif !important;
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    color: #8a909e !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    padding: 7px 12px !important;
    width: 100% !important;
    text-align: left !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(110,142,251,0.35) !important;
    color: #d8dae2 !important;
}
.stButton > button:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* ── New Chat: target by key ── */
button[kind="primary"],
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #6e8efb 0%, #a777e3 100%) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 500 !important;
    text-align: center !important;
}
[data-testid="baseButton-primary"]:hover {
    opacity: 0.88 !important;
}

/* ── Checkbox (Web Search) ── */
[data-testid="stCheckbox"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
    padding: 8px 10px !important;
}
[data-testid="stCheckbox"] span { color: #8a909e !important; font-size: 12px !important; }

/* ── File uploader ── */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(110,142,251,0.03) !important;
    border: 1px dashed rgba(110,142,251,0.25) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span { color: #4a5060 !important; font-size: 11px !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: rgba(110,142,251,0.1) !important;
    border: 1px solid rgba(110,142,251,0.3) !important;
    color: #6e8efb !important;
    border-radius: 7px !important;
    font-size: 11px !important;
    width: auto !important;
    padding: 4px 12px !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: rgba(110,142,251,0.18) !important;
    color: #fff !important;
}
[data-testid="stFileUploaderFile"] {
    background: rgba(110,142,251,0.06) !important;
    border: 1px solid rgba(110,142,251,0.18) !important;
    border-radius: 8px !important;
    padding: 5px 10px !important;
}
[data-testid="stFileUploaderFile"] span { color: #6e8efb !important; font-size: 11px !important; }
[data-testid="stFileUploaderFile"] button {
    background: transparent !important;
    border: none !important;
    color: #4a5060 !important;
    width: auto !important;
    padding: 2px !important;
    font-size: 13px !important;
}
[data-testid="stFileUploaderFile"] button:hover { color: #d8dae2 !important; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: #13161f !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    margin-bottom: 6px !important;
}
[data-testid="stChatMessage"] p {
    color: #d0d2da !important;
    font-size: 13.5px !important;
    line-height: 1.75 !important;
    margin: 0 !important;
}
[data-testid="stChatMessage"] code {
    background: rgba(0,0,0,0.4) !important;
    color: #a5b4fc !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 5px !important;
    padding: 1px 6px !important;
    font-size: 11.5px !important;
}
[data-testid="stChatMessage"] pre {
    background: #0b0d12 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    padding: 14px !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: #13161f !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(110,142,251,0.4) !important;
    box-shadow: 0 0 0 3px rgba(110,142,251,0.07) !important;
}
[data-testid="stChatInput"] textarea {
    color: #d0d2da !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 13px !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #3a3f50 !important; }
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #6e8efb, #a777e3) !important;
    border: none !important;
    border-radius: 9px !important;
}

/* ── Action buttons (Copy / Retry / Delete) in columns ── */
div[data-testid="column"] .stButton > button {
    text-align: center !important;
    padding: 3px 8px !important;
    font-size: 11px !important;
    color: #3a3f50 !important;
    border-color: rgba(255,255,255,0.06) !important;
    border-radius: 6px !important;
}
div[data-testid="column"] .stButton > button:hover {
    color: #d0d2da !important;
    border-color: rgba(255,255,255,0.14) !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ── Toast ── */
[data-testid="stToast"] {
    background: #1a1e2a !important;
    color: #d0d2da !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    font-size: 12px !important;
}

/* ── Info / Success alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 12px !important;
    padding: 8px 14px !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] > div { border-top-color: #6e8efb !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.07); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── API ────────────────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("API key missing. Add GROQ_API_KEY to .streamlit/secrets.toml")
    st.stop()

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are Faiz ChatBot, a powerful all-purpose AI assistant built for Kenyan users.

CAPABILITIES:
- Answer any question accurately and thoroughly
- Write and debug code in any language
- Generate creative content (stories, scripts, marketing copy)
- Research and explain complex topics clearly
- Kenya/Nairobi context: local advice, Swahili translation, M-Pesa, recommendations
- Math, logic, and reasoning problems

STYLE:
- Conversational, helpful, and direct
- Use markdown formatting (code blocks, lists, bold) when it aids clarity
- Prioritise Kenyan context where relevant
- Be concise unless detail is requested"""

QUICK_ACTIONS = [
    ("Today's agenda",    "Help me plan a productive agenda for today. Ask what tasks I have, then help prioritise them."),
    ("Image prompt",      "Generate a vivid, detailed prompt I can paste into an AI image generator."),
    ("Write or edit",     "I need help writing or editing some text. Ask me what I am working on."),
    ("Look something up", "What topic would you like me to research and explain for you?"),
    ("Write code",        "I need help writing some code. Ask me what I want to build."),
    ("Translate",         "What would you like me to translate, and to which language?"),
]

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {
    "messages": [],
    "file_data": None,
    "web_search": False,
    "pending_prompt": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────────────────────────────
def read_file(f):
    try:
        if f.type == "text/plain":
            return f.read().decode("utf-8")[:6000]
        return f"[Binary file attached: {f.name} ({f.type})]"
    except Exception:
        return f"[Could not read: {f.name}]"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_groq(api_msgs):
    return client.chat.completions.create(
        model=MODEL,
        messages=api_msgs,
        temperature=0.7,
        max_tokens=4096,
    )


def do_send(user_text, file_data=None):
    """Compose final prompt, update history, call API, rerun."""
    final = user_text
    if file_data:
        final = (
            f"[Attached file: {file_data['name']}]\n"
            f"{file_data['content']}\n\n"
            f"[Question]: {user_text}"
        )
    if st.session_state.web_search:
        final = (
            "[The user has web search enabled. Provide the most current information "
            "you know and note if data may be outdated.]\n\n" + final
        )

    display_content = (
        {"text": user_text, "file": file_data["name"]} if file_data else user_text
    )
    st.session_state.messages.append({
        "role": "user",
        "content": display_content,
        "_api": final,
    })

    with st.spinner("Thinking..."):
        try:
            api_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                c = m.get("_api") or (
                    m["content"] if isinstance(m["content"], str)
                    else m["content"].get("text", "")
                )
                api_msgs.append({"role": m["role"], "content": c})
            result = call_groq(api_msgs)
            reply = result.choices[0].message.content
        except Exception as e:
            reply = f"Error calling API: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.file_data = None
    st.rerun()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.image("Faiz Chatbot Logo.png", use_container_width=True)
    except Exception:
        pass

    st.markdown("## Faiz ChatBot")
    st.caption("All-purpose AI assistant")
    st.divider()

    if st.button("New Chat", use_container_width=True, type="primary", key="new_chat"):
        st.session_state.messages = []
        st.session_state.file_data = None
        st.session_state.pending_prompt = None
        st.rerun()

    st.divider()
    st.markdown("### Quick Actions")

    for label, prompt_text in QUICK_ACTIONS:
        if st.button(label, use_container_width=True, key=f"qa_{label}"):
            st.session_state.pending_prompt = prompt_text
            st.rerun()

    st.divider()

    # Web search toggle
    st.markdown("### Web Search")
    new_web = st.checkbox(
        "Enable web context",
        value=st.session_state.web_search,
        key="web_checkbox",
        help="Tells the model to give current information and flag if data may be outdated",
    )
    if new_web != st.session_state.web_search:
        st.session_state.web_search = new_web
        # No rerun needed — value is used on next send

    st.divider()

    # File upload
    st.markdown("### Attach File")
    uploaded = st.file_uploader(
        "Choose file",
        type=["txt", "py", "md", "csv", "json", "png", "jpg", "jpeg", "pdf", "docx"],
        label_visibility="collapsed",
        key="file_upload",
    )

    if uploaded is not None:
        if uploaded.size > 5 * 1024 * 1024:
            st.error("Max file size is 5 MB")
            st.session_state.file_data = None
        else:
            # Only re-read if it's a newly uploaded file
            if (
                st.session_state.file_data is None
                or st.session_state.file_data.get("name") != uploaded.name
            ):
                content = read_file(uploaded)
                st.session_state.file_data = {"name": uploaded.name, "content": content}
            st.success(f"Ready: {uploaded.name}")
    else:
        # Widget cleared (X pressed) — clear stored data
        st.session_state.file_data = None

    st.divider()
    st.caption(f"Model: {MODEL}")
    st.caption("Powered by Groq")

# ── Pending quick action ───────────────────────────────────────────────────────
if st.session_state.pending_prompt:
    p = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    do_send(p)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    '<p style="color:#2e3348;font-size:11px;font-family:\'JetBrains Mono\',monospace;'
    'margin-bottom:0.4rem;">faiz-chatbot / llama-3.3-70b-versatile</p>',
    unsafe_allow_html=True,
)

# Empty state
if not st.session_state.messages:
    st.markdown(
        """
        <div style="text-align:center;padding:80px 40px 40px;">
            <div style="font-size:11px;color:#2e3348;font-family:'JetBrains Mono',monospace;margin-bottom:12px;">
                ready
            </div>
            <div style="font-size:24px;font-weight:600;color:#d0d2da;margin-bottom:10px;">
                How can I help you today?
            </div>
            <div style="font-size:13px;color:#3a3f50;max-width:380px;margin:0 auto;line-height:1.8;">
                Ask me anything — code, research, writing, math, or anything else.<br>
                Use the quick actions on the left to get started fast.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Messages ───────────────────────────────────────────────────────────────────
for idx, message in enumerate(st.session_state.messages):
    role = message["role"]
    content = message["content"]
    text = content if isinstance(content, str) else content.get("text", "")

    with st.chat_message(role):
        st.markdown(text)

        if isinstance(content, dict) and content.get("file"):
            st.caption(f"File: {content['file']}")

        if role == "assistant":
            c1, c2, c3, _gap = st.columns([1, 1, 1, 9])

            with c1:
                if st.button("Copy", key=f"copy_{idx}"):
                    # Inject JS clipboard write into the page
                    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("</", "<\\/")
                    st.components.v1.html(
                        f"<script>navigator.clipboard.writeText(`{safe}`);</script>",
                        height=0,
                        scrolling=False,
                    )
                    st.toast("Copied to clipboard")

            with c2:
                if st.button("Retry", key=f"retry_{idx}"):
                    user_idx = idx - 1
                    while user_idx >= 0 and st.session_state.messages[user_idx]["role"] != "user":
                        user_idx -= 1
                    if user_idx >= 0:
                        with st.spinner("Regenerating..."):
                            try:
                                api_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
                                for i in range(user_idx + 1):
                                    m = st.session_state.messages[i]
                                    c_text = m.get("_api") or (
                                        m["content"] if isinstance(m["content"], str)
                                        else m["content"].get("text", "")
                                    )
                                    api_msgs.append({"role": m["role"], "content": c_text})
                                result = call_groq(api_msgs)
                                st.session_state.messages[idx]["content"] = result.choices[0].message.content
                                st.rerun()
                            except Exception as e:
                                st.error(f"Retry failed: {e}")

            with c3:
                if st.button("Delete", key=f"delete_{idx}"):
                    to_del = {idx}
                    if idx > 0 and st.session_state.messages[idx - 1]["role"] == "user":
                        to_del.add(idx - 1)
                    st.session_state.messages = [
                        m for i, m in enumerate(st.session_state.messages) if i not in to_del
                    ]
                    st.rerun()

# ── File attached banner ───────────────────────────────────────────────────────
if st.session_state.file_data:
    st.info(
        f"File attached: **{st.session_state.file_data['name']}** — "
        "will be sent with your next message. Clear it using the X in the sidebar uploader."
    )

# ── Chat input ─────────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask anything...")
if prompt:
    do_send(prompt, file_data=st.session_state.file_data)
