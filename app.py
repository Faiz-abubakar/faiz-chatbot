import streamlit as st
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
import json, urllib.parse

st.set_page_config(
    page_title="Faiz ChatBot",
    page_icon="Faiz Chatbot Logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:        #080a10;
  --surface:   #0e1118;
  --surface2:  #141820;
  --surface3:  #1c2130;
  --border:    rgba(255,255,255,0.06);
  --border2:   rgba(255,255,255,0.10);
  --text:      #dde1ec;
  --muted:     #5a6175;
  --accent1:   #7c9fff;
  --accent2:   #c084fc;
  --accent3:   #38bdf8;
  --success:   #34d399;
  --danger:    #f87171;
  --grad:      linear-gradient(135deg,#7c9fff 0%,#c084fc 100%);
  --grad-soft: linear-gradient(135deg,rgba(124,159,255,0.12) 0%,rgba(192,132,252,0.12) 100%);
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Sora', sans-serif !important; }

/* ── App ── */
.stApp { background: var(--bg) !important; }
.main .block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 0.5rem !important;
    max-width: 100% !important;
}

/* ── Sidebar shell ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { padding: 1.1rem 0.9rem !important; }

/* Sidebar text */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: var(--muted) !important;
    font-size: 12px !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--muted) !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
}
hr { border-color: var(--border) !important; margin: 0.55rem 0 !important; }

/* ── ALL buttons reset ── */
.stButton > button {
    font-family: 'Sora', sans-serif !important;
    background: transparent !important;
    border: 1px solid var(--border2) !important;
    color: var(--muted) !important;
    border-radius: 9px !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    padding: 8px 13px !important;
    width: 100% !important;
    text-align: left !important;
    transition: background 0.18s, border-color 0.18s, color 0.18s, box-shadow 0.18s !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button:hover {
    background: var(--surface3) !important;
    border-color: rgba(124,159,255,0.4) !important;
    color: var(--text) !important;
    box-shadow: 0 0 0 1px rgba(124,159,255,0.15) inset !important;
}
.stButton > button:active {
    background: rgba(124,159,255,0.08) !important;
    transform: scale(0.985) !important;
}
.stButton > button:focus { box-shadow: none !important; outline: none !important; }

/* ── New Chat (primary) ── */
[data-testid="baseButton-primary"] {
    background: var(--grad) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    text-align: center !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 2px 16px rgba(124,159,255,0.25) !important;
}
[data-testid="baseButton-primary"]:hover {
    background: var(--grad) !important;
    opacity: 0.88 !important;
    box-shadow: 0 4px 22px rgba(124,159,255,0.38) !important;
    border: none !important;
}
[data-testid="baseButton-primary"]:active {
    transform: scale(0.97) !important;
}

/* ── Checkbox ── */
[data-testid="stCheckbox"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 9px !important;
    padding: 9px 12px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stCheckbox"]:hover { border-color: rgba(124,159,255,0.35) !important; }
[data-testid="stCheckbox"] span { color: #7a8399 !important; font-size: 12px !important; }

/* Checkbox tick accent */
[data-testid="stCheckbox"] input:checked + div {
    background: var(--accent1) !important;
    border-color: var(--accent1) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(124,159,255,0.03) !important;
    border: 1px dashed rgba(124,159,255,0.22) !important;
    border-radius: 11px !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(124,159,255,0.06) !important;
    border-color: rgba(124,159,255,0.4) !important;
}
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span { color: #3e4560 !important; font-size: 11px !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: rgba(124,159,255,0.1) !important;
    border: 1px solid rgba(124,159,255,0.28) !important;
    color: var(--accent1) !important;
    border-radius: 7px !important;
    font-size: 11px !important;
    width: auto !important;
    padding: 4px 14px !important;
    transition: background 0.18s, color 0.18s !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: rgba(124,159,255,0.2) !important;
    color: #fff !important;
}
[data-testid="stFileUploaderFile"] {
    background: rgba(124,159,255,0.06) !important;
    border: 1px solid rgba(124,159,255,0.18) !important;
    border-radius: 9px !important;
    padding: 5px 10px !important;
}
[data-testid="stFileUploaderFile"] span { color: var(--accent1) !important; font-size: 11px !important; }
[data-testid="stFileUploaderFile"] button {
    background: transparent !important;
    border: none !important;
    color: var(--muted) !important;
    width: auto !important;
    padding: 2px !important;
}
[data-testid="stFileUploaderFile"] button:hover { color: var(--danger) !important; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 15px 20px !important;
    margin-bottom: 8px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stChatMessage"]:hover { border-color: var(--border2) !important; }

[data-testid="stChatMessage"] p {
    color: #cdd1de !important;
    font-size: 13.5px !important;
    line-height: 1.8 !important;
    margin: 0 !important;
}
[data-testid="stChatMessage"] li { color: #cdd1de !important; font-size: 13.5px !important; }
[data-testid="stChatMessage"] strong { color: var(--text) !important; }
[data-testid="stChatMessage"] code {
    background: rgba(0,0,0,0.45) !important;
    color: #93c5fd !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 5px !important;
    padding: 1px 6px !important;
    font-size: 11.5px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stChatMessage"] pre {
    background: #050608 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin: 10px 0 !important;
}

/* User message tint */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: var(--grad-soft) !important;
    border-color: rgba(124,159,255,0.14) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 15px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(124,159,255,0.5) !important;
    box-shadow: 0 0 0 3px rgba(124,159,255,0.08), 0 0 20px rgba(124,159,255,0.06) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 13.5px !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #2e3450 !important; }
[data-testid="stChatInput"] button {
    background: var(--grad) !important;
    border: none !important;
    border-radius: 10px !important;
    transition: opacity 0.18s, transform 0.12s !important;
}
[data-testid="stChatInput"] button:hover { opacity: 0.85 !important; transform: scale(1.05) !important; }

/* ── Toast ── */
[data-testid="stToast"] {
    background: var(--surface3) !important;
    color: var(--text) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 11px !important;
    font-size: 12px !important;
    backdrop-filter: blur(8px) !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 11px !important;
    font-size: 12px !important;
    padding: 9px 14px !important;
    border: none !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] > div { border-top-color: var(--accent1) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.12); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SVG Icon HTML buttons — rendered via st.components, post-click via query params
# ─────────────────────────────────────────────────────────────────────────────
ICON_COPY = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>"""
ICON_RETRY = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.5"/></svg>"""
ICON_DELETE = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>"""

def icon_button_row(idx: int, msg_text: str) -> tuple[bool, bool, bool]:
    """
    Renders Copy / Retry / Delete icon buttons for a message.
    Returns (copy_clicked, retry_clicked, delete_clicked).
    Uses URL query-param round-trip so clicks survive Streamlit reruns.
    """
    # Escape text for JS template literal
    safe_text = (
        msg_text
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("</", "<\\/")
        .replace("${", "\\${")
    )

    html = f"""
    <style>
      .icon-row-{idx} {{
        display: flex;
        gap: 5px;
        align-items: center;
        margin-top: 8px;
      }}
      .icon-btn-{idx} {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 7px;
        border: 1px solid rgba(255,255,255,0.08);
        background: transparent;
        color: #3e4a65;
        cursor: pointer;
        transition: background 0.18s, border-color 0.18s, color 0.18s, transform 0.12s;
        padding: 0;
      }}
      .icon-btn-{idx}:hover {{
        background: rgba(124,159,255,0.12);
        border-color: rgba(124,159,255,0.35);
        color: #7c9fff;
        transform: scale(1.08);
      }}
      .icon-btn-{idx}.copy-btn:hover  {{ color: #34d399; border-color: rgba(52,211,153,0.35); background: rgba(52,211,153,0.1); }}
      .icon-btn-{idx}.retry-btn:hover {{ color: #7c9fff; border-color: rgba(124,159,255,0.35); background: rgba(124,159,255,0.1); }}
      .icon-btn-{idx}.del-btn:hover   {{ color: #f87171; border-color: rgba(248,113,113,0.35); background: rgba(248,113,113,0.1); }}
      .icon-btn-{idx}:active {{ transform: scale(0.94); }}
      .icon-btn-{idx}.active-flash {{ background: rgba(52,211,153,0.18) !important; color: #34d399 !important; }}
      .copy-label-{idx} {{ font-size: 10px; color: #34d399; margin-left: 2px; display: none; font-family: 'Sora', sans-serif; }}
    </style>

    <div class="icon-row-{idx}">

      <!-- Copy -->
      <button class="icon-btn-{idx} copy-btn" id="copy_{idx}" title="Copy response">
        {ICON_COPY}
      </button>
      <span class="copy-label-{idx}" id="copy_label_{idx}">Copied</span>

      <!-- Retry -->
      <button class="icon-btn-{idx} retry-btn" id="retry_{idx}" title="Retry response"
        onclick="triggerAction('retry', {idx})">
        {ICON_RETRY}
      </button>

      <!-- Delete -->
      <button class="icon-btn-{idx} del-btn" id="delete_{idx}" title="Delete message"
        onclick="triggerAction('delete', {idx})">
        {ICON_DELETE}
      </button>

    </div>

    <script>
      // Copy — pure JS, no server round-trip needed
      document.getElementById('copy_{idx}').addEventListener('click', function() {{
        navigator.clipboard.writeText(`{safe_text}`).then(function() {{
          var btn = document.getElementById('copy_{idx}');
          var lbl = document.getElementById('copy_label_{idx}');
          btn.classList.add('active-flash');
          lbl.style.display = 'inline';
          setTimeout(function() {{
            btn.classList.remove('active-flash');
            lbl.style.display = 'none';
          }}, 1800);
        }});
      }});

      // Retry / Delete — send action to Streamlit via query param
      function triggerAction(action, idx) {{
        var url = new URL(window.parent.location.href);
        url.searchParams.set('action', action);
        url.searchParams.set('idx', idx);
        window.parent.history.replaceState(null, '', url.toString());
        // Trigger a Streamlit re-render by poking the parent
        window.parent.dispatchEvent(new CustomEvent('streamlit:rerun'));
      }}
    </script>
    """

    # Render the HTML component (zero visible height for row, actual height for the buttons)
    st.components.v1.html(html, height=48, scrolling=False)

    # Read query params to detect if this message's buttons were clicked
    params = st.query_params
    action = params.get("action", "")
    action_idx = params.get("idx", "")

    copy_clicked   = False  # Copy is handled client-side
    retry_clicked  = (action == "retry"  and str(action_idx) == str(idx))
    delete_clicked = (action == "delete" and str(action_idx) == str(idx))

    return copy_clicked, retry_clicked, delete_clicked


# ─────────────────────────────────────────────────────────────────────────────
# API
# ─────────────────────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────
for k, v in {
    "messages": [],
    "file_data": None,
    "web_search": False,
    "pending_prompt": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
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


def build_api_msgs(up_to: int | None = None):
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    history = st.session_state.messages if up_to is None else st.session_state.messages[:up_to]
    for m in history:
        c = m.get("_api") or (
            m["content"] if isinstance(m["content"], str)
            else m["content"].get("text", "")
        )
        msgs.append({"role": m["role"], "content": c})
    return msgs


def do_send(user_text: str, file_data=None):
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

    display = (
        {"text": user_text, "file": file_data["name"]} if file_data else user_text
    )
    st.session_state.messages.append({"role": "user", "content": display, "_api": final})

    with st.spinner("Thinking..."):
        try:
            result = call_groq(build_api_msgs())
            reply = result.choices[0].message.content
        except Exception as e:
            reply = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.file_data = None
    # Clear any stale action params
    st.query_params.clear()
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Handle query-param actions (retry / delete) BEFORE rendering
# ─────────────────────────────────────────────────────────────────────────────
params = st.query_params
qaction = params.get("action", "")
qidx_raw = params.get("idx", "")

if qaction in ("retry", "delete") and qidx_raw.isdigit():
    qidx = int(qidx_raw)
    st.query_params.clear()  # consume immediately

    if qaction == "delete" and qidx < len(st.session_state.messages):
        to_del = {qidx}
        if qidx > 0 and st.session_state.messages[qidx - 1]["role"] == "user":
            to_del.add(qidx - 1)
        st.session_state.messages = [
            m for i, m in enumerate(st.session_state.messages) if i not in to_del
        ]
        st.rerun()

    elif qaction == "retry" and qidx < len(st.session_state.messages):
        user_idx = qidx - 1
        while user_idx >= 0 and st.session_state.messages[user_idx]["role"] != "user":
            user_idx -= 1
        if user_idx >= 0:
            with st.spinner("Regenerating..."):
                try:
                    result = call_groq(build_api_msgs(up_to=user_idx + 1))
                    st.session_state.messages[qidx]["content"] = result.choices[0].message.content
                except Exception as e:
                    st.session_state.messages[qidx]["content"] = f"Error: {e}"
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Pending quick action
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.pending_prompt:
    p = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    do_send(p)

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
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
        st.query_params.clear()
        st.rerun()

    st.divider()
    st.markdown("### Quick Actions")

    for label, prompt_text in QUICK_ACTIONS:
        if st.button(label, use_container_width=True, key=f"qa_{label}"):
            st.session_state.pending_prompt = prompt_text
            st.rerun()

    st.divider()
    st.markdown("### Web Search")
    new_web = st.checkbox(
        "Enable web context",
        value=st.session_state.web_search,
        key="web_checkbox",
        help="Tells the model to give current information and flag if data may be outdated",
    )
    if new_web != st.session_state.web_search:
        st.session_state.web_search = new_web

    st.divider()
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
            if (
                st.session_state.file_data is None
                or st.session_state.file_data.get("name") != uploaded.name
            ):
                st.session_state.file_data = {"name": uploaded.name, "content": read_file(uploaded)}
            st.success(f"Ready: {uploaded.name}")
    else:
        st.session_state.file_data = None

    st.divider()
    st.caption(f"Model: {MODEL}")
    st.caption("Powered by Groq")

# ─────────────────────────────────────────────────────────────────────────────
# Page header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<p style="color:#1e2438;font-size:11px;font-family:\'JetBrains Mono\',monospace;'
    'margin-bottom:0.3rem;letter-spacing:0.05em;">faiz-chatbot · llama-3.3-70b-versatile</p>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Empty state
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:70px 40px 30px;">
      <div style="
        width:58px;height:58px;
        background:linear-gradient(135deg,#7c9fff,#c084fc);
        border-radius:16px;
        margin:0 auto 18px;
        display:flex;align-items:center;justify-content:center;
      ">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      </div>
      <div style="font-size:22px;font-weight:700;
        background:linear-gradient(135deg,#7c9fff,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        margin-bottom:10px;">
        How can I help you today?
      </div>
      <div style="font-size:13px;color:#3e4a65;max-width:360px;margin:0 auto;line-height:1.85;">
        Ask anything — code, research, writing, math, or anything else.<br>
        Use the quick actions in the sidebar to get started fast.
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Messages
# ─────────────────────────────────────────────────────────────────────────────
for idx, message in enumerate(st.session_state.messages):
    role = message["role"]
    content = message["content"]
    text = content if isinstance(content, str) else content.get("text", "")

    with st.chat_message(role):
        st.markdown(text)
        if isinstance(content, dict) and content.get("file"):
            st.caption(f"File attached: {content['file']}")

        if role == "assistant":
            icon_button_row(idx, text)

# ─────────────────────────────────────────────────────────────────────────────
# File attached banner
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.file_data:
    st.info(
        f"File attached: **{st.session_state.file_data['name']}** — "
        "will be sent with your next message."
    )

# ─────────────────────────────────────────────────────────────────────────────
# Chat input
# ─────────────────────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask anything...")
if prompt:
    do_send(prompt, file_data=st.session_state.file_data)