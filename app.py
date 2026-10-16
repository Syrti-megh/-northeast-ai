import streamlit as st
from gtts import gTTS
import io, os
try:
    from groq import Groq
    GROQ_AVAILABLE=True
except:
    GROQ_AVAILABLE=False

st.set_page_config(page_title="Northeast AI - Meghalaya", page_icon="🏔️", layout="centered")

CREATOR_NAME="Samewan"
CREATOR_PLACE="Meghalaya"

LANGUAGES = {
    "Garo": "Mitela",
    "Khasi": "Khublei",
    "Mizo": "Chibai",
    "Kokborok": "Hamjakma",
    "Assamese": "Nomoskar",
    "Bengali": "Nomoskar",
    "Hindi": "Namaste",
    "English": "Hello",
    "Nagamese": "Hello"
}

if "messages" not in st.session_state:
    st.session_state.messages=[]

st.title("🏔️ Northeast AI")
st.markdown("""
**🌟 Meghalaya's First 9-Language Voice AI | Northeast India**
🎙️ **Bolke puchho, sunke samjho** - Apni bhasa me baat karo!
💬 Garo | Khasi | Mizo | Kokborok | Assamese | Bengali | Hindi | English | Nagamese
""")
st.info("👇 Bhasa chuno, phir Type karo ya 🎤 Mic se Bolo!")

col1, col2 = st.columns([2,1])
with col1:
    lang = st.selectbox("🌐 Language Chuno:", list(LANGUAGES.keys()), index=0)
with col2:
    if st.button("🗑️ Clear"):
        st.session_state.messages=[]
        st.rerun()

def get_api_key():
    k = st.secrets.get("GROQ_API_KEY","") if hasattr(st, 'secrets') else ""
    return k.strip()

def get_reply(text, language):
    low=text.lower()
    if any(k in low for k in ["who made you","kisne banaya","tumhe kisne","creator","banaya kisne","who created"]):
        return f"Mujhe banaya hai {CREATOR_NAME} ne, {CREATOR_PLACE} se! 🏔️"

    api_key=get_api_key()
    if GROQ_AVAILABLE and api_key:
        try:
            client=Groq(api_key=api_key)
            # NAYA WORKING MODEL - 2026
            comp=client.chat.completions.create(
                messages=[{"role":"user","content":f"You are Northeast AI, creator {CREATOR_NAME} from {CREATOR_PLACE}. Reply in {language}. User: {text}"}],
                model="openai/gpt-oss-20b", max_tokens=300)
            return comp.choices[0].message.content
        except Exception as e:
            # Agar ye bhi fail to dusra try karo
            try:
                comp=client.chat.completions.create(
                    messages=[{"role":"user","content":f"You are Northeast AI, creator {CREATOR_NAME} from {CREATOR_PLACE}. Reply in {language}. User: {text}"}],
                    model="llama-3.1-8b-instant", max_tokens=300)
                return comp.choices[0].message.content
            except Exception as e2:
                return f"Groq Error: {e2}"
    return f"{LANGUAGES[language]}! You said: {text} in {language}."

def transcribe_voice(audio_file):
    api_key=get_api_key()
    if GROQ_AVAILABLE and api_key and audio_file:
        try:
            client=Groq(api_key=api_key)
            tr=client.audio.transcriptions.create(
                file=("voice.wav", audio_file.getvalue()),
                model="whisper-large-v3"
            )
            return tr.text
        except:
            return None
    return None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"]=="assistant":
            try:
                tts=gTTS(text=msg["content"][:350], lang='en')
                fp=io.BytesIO()
                tts.write_to_fp(fp)
                st.audio(fp.getvalue(), format="audio/mp3")
            except:
                pass

st.divider()
st.markdown(f"**{LANGUAGES[lang]}! Type karo ya Mic dabao 🎤**")

voice_input = st.audio_input(f"🎤 {lang} me Bolo")

user_text = None
if voice_input:
    with st.spinner("Sun raha hu..."):
        transcribed = transcribe_voice(voice_input)
        if transcribed:
            user_text = transcribed
            st.success(f"🎤 Suna: {transcribed}")
        else:
            user_text = f"Voice message in {lang}"

text_input = st.chat_input(f"{LANGUAGES[lang]}! Yahan likho...")

if text_input:
    user_text = text_input

if user_text:
    st.session_state.messages.append({"role":"user","content":user_text})
    with st.chat_message("user"):
        st.write(user_text)

    reply=get_reply(user_text, lang)
    st.session_state.messages.append({"role":"assistant","content":reply})
    with st.chat_message("assistant"):
        st.write(reply)
        try:
            tts=gTTS(text=reply[:350], lang='en')
            fp=io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)
        except Exception as e:
            st.write(f"Audio error: {e}")
