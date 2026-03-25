import streamlit as st
import google.generativeai as genai

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Text Summarizer · Gemini",
    page_icon="✦",
    layout="centered",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Background */
    .stApp {
        background: #0d0d0d;
        color: #e8e4dc;
    }

    /* Header */
    .hero {
        text-align: center;
        padding: 3rem 0 1.5rem;
    }
    .hero h1 {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        color: #e8e4dc;
        letter-spacing: -0.5px;
        margin-bottom: 0.25rem;
    }
    .hero .accent {
        color: #c9a84c;
    }
    .hero p {
        color: #7a7468;
        font-size: 1rem;
        font-weight: 300;
        margin-top: 0.5rem;
    }

    /* Divider */
    .divider {
        border: none;
        border-top: 1px solid #2a2a2a;
        margin: 1.5rem 0;
    }

    /* Label override */
    label, .stTextArea label {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        color: #7a7468 !important;
    }

    /* Textarea */
    textarea {
        background: #161616 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 10px !important;
        color: #e8e4dc !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.95rem !important;
        caret-color: #c9a84c !important;
    }
    textarea:focus {
        border-color: #c9a84c !important;
        box-shadow: 0 0 0 2px rgba(201,168,76,0.12) !important;
    }

    /* Text input (API key) */
    input[type="password"], input[type="text"] {
        background: #161616 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
        color: #e8e4dc !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    input:focus {
        border-color: #c9a84c !important;
        box-shadow: 0 0 0 2px rgba(201,168,76,0.12) !important;
    }

    /* Button */
    .stButton > button {
        width: 100%;
        background: #c9a84c !important;
        color: #0d0d0d !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.5rem !important;
        transition: opacity 0.2s ease !important;
    }
    .stButton > button:hover {
        opacity: 0.85 !important;
        color: #0d0d0d !important;
    }

    /* Summary output box */
    .summary-box {
        background: #161616;
        border: 1px solid #2a2a2a;
        border-left: 3px solid #c9a84c;
        border-radius: 10px;
        padding: 1.4rem 1.6rem;
        margin-top: 1.2rem;
        line-height: 1.75;
        font-size: 0.97rem;
        color: #d8d4cc;
    }
    .summary-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        color: #c9a84c;
        font-weight: 500;
        margin-bottom: 0.6rem;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background: #161616 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
        color: #e8e4dc !important;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Hero header ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>Text <span class="accent">Summarizer</span></h1>
        <p>Powered by Gemini 1.5 Flash · Instant, intelligent condensation</p>
    </div>
    <hr class="divider">
    """,
    unsafe_allow_html=True,
)

# ── Sidebar: API Key ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙ Configuration")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Get your key at https://aistudio.google.com/app/apikey",
    )
    st.caption("Your key is never stored and only used for this session.")

    st.markdown("---")
    st.markdown("### Options")
    summary_length = st.selectbox(
        "Summary length",
        ["Short (2–3 sentences)", "Medium (1 paragraph)", "Detailed (2–3 paragraphs)"],
        index=1,
    )
    tone = st.selectbox(
        "Tone",
        ["Neutral", "Formal", "Casual", "Bullet points"],
        index=0,
    )

# ── Main UI ────────────────────────────────────────────────────────────────────
input_text = st.text_area(
    "Paste your text below",
    placeholder="Enter any article, document, or passage you'd like summarized…",
    height=280,
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    summarize_clicked = st.button("✦  Summarize", use_container_width=True)

# ── Summarization logic ────────────────────────────────────────────────────────
length_map = {
    "Short (2–3 sentences)": "in 2–3 concise sentences",
    "Medium (1 paragraph)": "in one clear paragraph",
    "Detailed (2–3 paragraphs)": "in 2–3 well-structured paragraphs",
}
tone_map = {
    "Neutral": "Use a neutral, objective tone.",
    "Formal": "Use a formal, professional tone.",
    "Casual": "Use a friendly, conversational tone.",
    "Bullet points": "Format the summary as concise bullet points.",
}

if summarize_clicked:
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar.")
    elif not input_text.strip():
        st.warning("Please paste some text before summarizing.")
    else:
        length_instruction = length_map[summary_length]
        tone_instruction = tone_map[tone]

        prompt = (
            f"Summarize the following text {length_instruction}. "
            f"{tone_instruction}\n\n"
            f"Text:\n{input_text.strip()}"
        )

        with st.spinner("Generating summary…"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(prompt)
                summary = response.text.strip()

                st.markdown(
                    f"""
                    <div class="summary-box">
                        <div class="summary-label">✦ Summary</div>
                        {summary}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Word-count stats
                original_wc = len(input_text.split())
                summary_wc = len(summary.split())
                reduction = round((1 - summary_wc / original_wc) * 100) if original_wc else 0

                m1, m2, m3 = st.columns(3)
                m1.metric("Original words", f"{original_wc:,}")
                m2.metric("Summary words", f"{summary_wc:,}")
                m3.metric("Reduction", f"{reduction}%")

            except Exception as e:
                st.error(f"API error: {e}")
