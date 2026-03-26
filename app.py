import streamlit as st
from google import genai

# ── Page config ─────────────────────────────────────────
st.set_page_config(
    page_title="Text Summarizer · Gemini",
    page_icon="✦",
    layout="centered",
)

# ── Sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙ Configuration")
    api_key = st.text_input("Gemini API Key", type="password")

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

# ── Main UI ─────────────────────────────────────────────
st.title("✦ Text Summarizer")

input_text = st.text_area("Paste your text below", height=250)

summarize_clicked = st.button("✦ Summarize")

# ── Logic ───────────────────────────────────────────────
length_map = {
    "Short (2–3 sentences)": "in 2–3 concise sentences",
    "Medium (1 paragraph)": "in one clear paragraph",
    "Detailed (2–3 paragraphs)": "in 2–3 well-structured paragraphs",
}

tone_map = {
    "Neutral": "Use a neutral tone.",
    "Formal": "Use a formal tone.",
    "Casual": "Use a friendly tone.",
    "Bullet points": "Format in bullet points.",
}

if summarize_clicked:
    if not api_key:
        st.error("Enter API key")
    elif not input_text.strip():
        st.warning("Enter some text")
    else:
        prompt = f"""
        Summarize the following text {length_map[summary_length]}.
        {tone_map[tone]}

        Text:
        {input_text}
        """

        try:
            # ✅ NEW SDK
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )

            summary = response.text

            st.subheader("Summary")
            st.write(summary)

        except Exception as e:
            st.error(f"Error: {e}")
