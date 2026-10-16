import streamlit as st
from gtts import gTTS
import io
import os

# Try to import groq for real brain
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

st.set_page_config(page_title="Northeast AI by Samewan", page_icon="🏔️", layout="centered")

# --- CREATOR INFO - FIXED ---
CREATOR_NAME = "Samewan"
CREATOR_PLACE = "Meghalaya"
CREATOR_TAG = "Founder of Northeast 9 Language AI - Meghalaya"

# --- LANGUAGES ---
LANGUAGES = {
    "Garo": {"code": "en", "greet": "Mitela"},
    "English": {"code": "en", "greet": "Hello"},
    "Hindi": {"code": "hi", "greet": "Namaste"},
    "Khasi": {"code": "en", "greet": "Khublei"},
    "Mizo": {"code": "en", "greet": "Chibai"},
    "Tripura (Kokborok)": {"code": "en", "greet": "Hamjakma"},
    "Nagaland": {"code": "en", "greet": "Kuknalim"},
    "Assamese": {"code": "en", "greet": "Nomoskar"},
    "Bengali": {"code": "bn", "greet": "Nomoskar"}
}

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- HEADER WITH YOUR NAME ---
st.title("🏔️ Northeast AI")
st.markdown(f"**Created by {CREATOR_NAME} | {CREATOR_PLACE}**")
st.caption(f"🚀 {CREATOR_TAG} | 9 Bhasa - Garo | Khasi | Mizo | Kokborok | Assamese | Bengali | Hindi | English | Nagamese")
st.markdown("---")

# Sidebar with creator credit
with st.sidebar:
    st.markdown(f"### 👨‍💻 Creator")
    st.markdown(f"**{CREATOR_NAME}**")
    st.markdown(f"📍 {CREATOR_PLACE}")
    st.markdown(f"🏆 Northeast ka pehla 9-Bhasa Voice AI")
    st.divider()
    st.markdown("**Bhasa Chuno:**")
    lang = st.selectbox("Language:", list(LANGUAGES.keys()), label_visibility="collapsed")
    st.divider()
    st.markdown(f"Made with ❤️ by **{CREATOR_NAME}**")
    st.markdown("© 2026 Northeast AI")
    if st.button("🗑️ Chat Clear Karo"):
        st.session_state.messages = []
        st.rerun()

# Language selection if not in sidebar (mobile)
if 'lang' not in locals():
    lang = st.selectbox("👇 Bhasa Chuno:", list(LANGUAGES.keys()))

# --- AI BRAIN FUNCTION - FIXED FOR SAMEWAN ---
def get_ai_reply(user_text, language):
    user_lower = user_text.lower()

    # 1. Creator question - MUST say Samewan Meghalaya
    creator_keywords = ["who made you","who created you","kisne banaya","tumhe kisne banaya","creator","tumhara creator","banaya kisne","who is your creator","tumhe kisne","who built you","who are you made by","aapko kisne"]
    if any(k in user_lower for k in creator_keywords):
        return f"Mujhe banaya hai **{CREATOR_NAME}** ne, **{CREATOR_PLACE}** se! 🏔️ Mitela! I am Northeast ka pehla 9-Bhasa Voice AI, made with love by {CREATOR_NAME} from {CREATOR_PLACE}."

    # 2. Try Groq real brain if key exists
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    if GROQ_AVAILABLE and api_key:
        try:
            client = Groq(api_key=api_key)
            prompt = f"""You are Northeast AI created by {CREATOR_NAME} from {CREATOR_PLACE}.
            You are the first 9-language voice AI of Northeast India.
            User selected language: {language}. Reply in {language} language.
            If Garo, use Mitela. If Khasi use Khublei. If Mizo use Chibai. If Kokborok use Hamjakma.
            IMPORTANT: If user asks who made you, always say you were created by {CREATOR_NAME} from {CREATOR_PLACE}, Meghalaya.
            Keep reply short, friendly, ChatGPT style under 150 words.
            User said: {user_text}"""
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                max_tokens=300,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            pass

    if "from" in user_lower:
        return f"{LANGUAGES[language]['greet']}! I am Northeast AI, created by {CREATOR_NAME} from {CREATOR_PLACE}. I can speak 9 languages including {language}. Ask me anything!"

    return f"{LANGUAGES[language]['greet']}! You said: {user_text}. I am Northeast AI by {CREATOR_NAME} from {CREATOR_PLACE}. I understand 9 languages - {language} me kaise madad karu?"

# Show chat history (ChatGPT style)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            try:
                lang_code = LANGUAGES[lang]["code"] if LANGUAGES[lang]["code"] in ['en','hi','bn'] else 'en'
                tts = gTTS(text=msg["content"][:400], lang=lang_code, slow=False)
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp.getvalue(), format="audio/mp3")
            except:
                pass

# Chat Input
prompt = st.chat_input(f"{LANGUAGES[lang]['greet']}! Yahan likho / Type in {lang}...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    reply = get_ai_reply(prompt, lang)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
        try:
            lang_code = LANGUAGES[lang]["code"] if LANGUAGES[lang]["code"] in ['en','hi','bn'] else 'en'
            tts = gTTS(text=reply[:400], lang=lang_code, slow=False)
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp.getvalue(), format="audio/mp3")
        except:
            pass
    st.rerun()

# Footer with big creator name
st.divider()
st.markdown(f"<center><h3>Made with ❤️ by <b>{CREATOR_NAME}</b></h3><p>{CREATOR_PLACE} | Northeast 9 Language Voice AI<br>ChatGPT Style Text + Voice</p><p>If anyone asks 'Who made you?' -> I was made by {CREATOR_NAME} from {CREATOR_PLACE}!</p></center>", unsafe_allow_html=True)
