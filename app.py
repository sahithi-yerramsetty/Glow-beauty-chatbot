import streamlit as st
from chatbot import create_beauty_chatbot, chat, get_greeting

st.set_page_config(
    page_title="GlowBot — Beauty Advisor",
    page_icon="✨",
    layout="wide"
)

st.markdown("""
<style>
    :root {
        --bg-dark: #0b1020;
        --bg-panel: #141827;
        --bg-soft: #1b2134;
        --bg-card: #1d2336;
        --text-main: #f5edf9;
        --text-soft: #d7c7ef;
        --text-muted: #b8a9d8;
        --border-soft: rgba(196, 144, 234, 0.28);
        --pink: #f472b6;
        --purple: #c084fc;
        --lavender: #b89cff;
    }

    .stApp {
        background: radial-gradient(circle at top, rgba(192, 132, 252, 0.15), transparent 30%),
                    linear-gradient(135deg, #120f1a 0%, #1a1325 45%, #0f172a 100%);
    }

    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .stChatMessage {
        background: rgba(26, 31, 45, 0.96) !important;
        color: var(--text-main) !important;
        border-radius: 18px !important;
        border: 1px solid var(--border-soft) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important;
        margin-bottom: 10px !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
    }

    .stChatMessage p,
    .stChatMessage li,
    .stChatMessage div,
    .stChatMessage span,
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown div,
    .stMarkdown span {
        color: var(--text-main) !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
        max-width: 100% !important;
    }

    section[data-testid="stSidebar"] {
        background: rgba(17, 17, 26, 0.97) !important;
        border-right: 1px solid rgba(196, 144, 234, 0.2) !important;
    }

    .stTextInput > div > div > input,
    .stChatInput textarea,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background: rgba(14, 18, 29, 0.96) !important;
        color: var(--text-main) !important;
        border: 1px solid rgba(196, 144, 234, 0.25) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }

    .stTextInput label,
    .stChatInput label,
    .stSelectbox label,
    .stNumberInput label {
        color: var(--text-soft) !important;
    }

    .stButton button {
        background: linear-gradient(135deg, var(--purple), var(--pink)) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
        box-shadow: 0 12px 24px rgba(196, 132, 252, 0.25) !important;
    }

    .stButton button:hover {
        filter: brightness(1.05) !important;
        transform: translateY(-1px) !important;
    }

    .profile-card {
        background: rgba(29, 35, 54, 0.96);
        border: 1px solid rgba(196, 144, 234, 0.2);
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 22px rgba(12, 12, 22, 0.18);
    }

    .profile-row {
        display: flex;
        justify-content: space-between;
        padding: 7px 0;
        font-size: 13px;
        border-bottom: 1px solid rgba(196, 144, 234, 0.12);
    }

    .profile-row:last-child {
        border-bottom: none;
    }

    .profile-label {
        color: #f7c7e0;
        font-weight: 600;
    }

    .profile-value {
        color: var(--text-main);
        text-align: right;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-main) !important;
    }

    .stAlert {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)


def init_session():
    if "llm" not in st.session_state:
        st.session_state.llm = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = False
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "Focus": None, "Skin Type": None, "Hair Type": None,
            "Concern": None, "Budget": None, "Climate": None
        }

init_session()


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✨ GlowBot")
    st.markdown("<p style='color:#9f7fc0;font-size:13px;margin-top:-10px'>Your AI beauty advisor</p>", unsafe_allow_html=True)
    st.divider()

    if not st.session_state.api_key_set:
        st.markdown("**🔑 Enter your Groq API Key**")
        api_key = st.text_input("", type="password", placeholder="gsk_...", label_visibility="collapsed")
        if st.button("Start chatting ✨"):
            if api_key.startswith("gsk_"):
                st.session_state.llm = create_beauty_chatbot(api_key)
                st.session_state.api_key_set = True
                st.session_state.messages.append({"role": "assistant", "content": get_greeting()})
                st.rerun()
            else:
                st.error("Please enter a valid Groq API key (starts with gsk_)")
        st.markdown("""
        <div style='background:rgba(29,35,54,0.96);border:1px solid rgba(196,144,234,0.25);border-radius:12px;padding:12px;margin-top:1rem;font-size:12px;color:#f7d4ef;box-shadow:0 8px 20px rgba(0,0,0,0.12)'>
        💡 Get a free API key at<br><b style='color:#f5edf9'>console.groq.com</b><br>No credit card required
        </div>""", unsafe_allow_html=True)

    else:
        st.markdown("**Your Beauty Profile**")
        profile = st.session_state.profile
        has_any = any(v for v in profile.values())
        if has_any:
            html = "<div class='profile-card'>"
            for key, val in profile.items():
                if val:
                    html += f"<div class='profile-row'><span class='profile-label'>{key}</span><span class='profile-value'>{val}</span></div>"
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:rgba(29,35,54,0.96);border:1px solid rgba(196,144,234,0.2);border-radius:12px;padding:12px;font-size:13px;color:#f7d4ef;text-align:center;box-shadow:0 8px 18px rgba(0,0,0,0.12)'>Your profile builds as we chat 🌸</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("**Quick questions**")
        quick_prompts = [
            "🧴 Suggest a morning routine",
            "💰 Show budget alternatives",
            "🔬 Explain key ingredients",
            "💇 Hair care tips",
            "🌙 Night routine for me",
        ]
        for prompt in quick_prompts:
            if st.button(prompt, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.spinner("GlowBot is thinking..."):
                    response = chat(st.session_state.llm, prompt, st.session_state.messages[:-1])
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

        st.divider()
        if st.button("🔄 Start over", use_container_width=True):
            for key in ["llm", "messages", "api_key_set", "profile"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


# ── Main chat ─────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown("""
    <div style='text-align:center;padding:1.5rem 0 1rem'>
        <h1 style='font-size:2rem;font-weight:700;background:linear-gradient(135deg,#c084fc,#f472b6);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0'>✨ GlowBot</h1>
        <p style='color:#9f7fc0;font-size:14px;margin:4px 0 0'>Your personal AI beauty advisor — skincare · haircare · routines</p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.api_key_set:
        st.markdown("""
        <div style='text-align:center;padding:3rem 1rem'>
            <div style='font-size:4rem;margin-bottom:1rem'>🌸</div>
            <h3 style='color:#7c3aed;font-weight:500'>Welcome to GlowBot</h3>
            <p style='color:#9f7fc0;max-width:400px;margin:0 auto'>
                Enter your Groq API key in the sidebar to get personalized beauty recommendations.
            </p>
        </div>
        <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:2rem'>
            <div style='background:rgba(29,35,54,0.96);border:1px solid rgba(196,144,234,0.2);border-radius:14px;padding:1.2rem;text-align:center;box-shadow:0 8px 20px rgba(0,0,0,0.12)'>
                <div style='font-size:1.8rem'>🧴</div>
                <div style='font-weight:600;color:#f7d4ef;margin-top:6px;font-size:14px'>Skincare Routines</div>
                <div style='font-size:12px;color:#d7c7ef;margin-top:4px'>AM & PM routines for your skin type</div>
            </div>
            <div style='background:rgba(29,35,54,0.96);border:1px solid rgba(196,144,234,0.2);border-radius:14px;padding:1.2rem;text-align:center;box-shadow:0 8px 20px rgba(0,0,0,0.12)'>
                <div style='font-size:1.8rem'>💰</div>
                <div style='font-weight:600;color:#f7d4ef;margin-top:6px;font-size:14px'>Budget Picks</div>
                <div style='font-size:12px;color:#d7c7ef;margin-top:4px'>From $5 drugstore to luxury</div>
            </div>
            <div style='background:rgba(29,35,54,0.96);border:1px solid rgba(196,144,234,0.2);border-radius:14px;padding:1.2rem;text-align:center;box-shadow:0 8px 20px rgba(0,0,0,0.12)'>
                <div style='font-size:1.8rem'>🔬</div>
                <div style='font-weight:600;color:#f7d4ef;margin-top:6px;font-size:14px'>Ingredient Guide</div>
                <div style='font-size:12px;color:#d7c7ef;margin-top:4px'>What to use and avoid</div>
            </div>
        </div>""", unsafe_allow_html=True)

    else:
        for message in st.session_state.messages:
            avatar = "🧑" if message["role"] == "user" else "✨"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        user_input = st.chat_input("Ask about your skin, hair, products, routines...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Auto-detect profile
            input_lower = user_input.lower()
            profile = st.session_state.profile
            if any(w in input_lower for w in ["skin", "face", "acne", "pore", "moistur"]):
                profile["Focus"] = "Skincare"
            if any(w in input_lower for w in ["hair", "scalp", "frizz", "dandruff"]):
                profile["Focus"] = "Both" if profile["Focus"] == "Skincare" else "Haircare"
            for skin in ["oily", "dry", "combination", "sensitive", "normal"]:
                if skin in input_lower:
                    profile["Skin Type"] = skin.title()
            for hair in ["straight", "wavy", "curly", "coily"]:
                if hair in input_lower:
                    profile["Hair Type"] = hair.title()
            if any(w in input_lower for w in ["under $20", "drugstore", "cheap"]):
                profile["Budget"] = "Under $20"
            elif any(w in input_lower for w in ["$20", "$50", "mid"]):
                profile["Budget"] = "$20–$50"
            elif any(w in input_lower for w in ["$100", "luxury"]):
                profile["Budget"] = "$100+"
            concerns = ["acne", "dark spots", "hyperpigmentation", "dryness", "frizz", "hair loss", "dandruff", "anti-aging", "wrinkles", "redness"]
            found = [c for c in concerns if c in input_lower]
            if found:
                profile["Concern"] = ", ".join(found[:2]).title()
            st.session_state.profile = profile

            with st.spinner("✨ GlowBot is crafting your advice..."):
                response = chat(st.session_state.llm, user_input, st.session_state.messages[:-1])

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
