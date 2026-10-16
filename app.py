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
    "Nagamese": "Hello",
    "Nepali": "Namaste"
}

# FIX 1 - FIRST REPLY = Welcome to our AI from Meghalaya
if "messages" not in st.session_state:
    st.session_state.messages=[{"role":"assistant","content":"Welcome to our AI from Meghalaya! 🏔️ Main Northeast ka pehla 10-language voice AI hu. Apni bhasa chuno aur bolo, main Roman English me clear jawab dunga."}]

st.title("🏔️ Northeast AI")
st.markdown("""
**🌟 Meghalaya's First 10-Language Voice AI | Northeast India**
🎙️ **Bolke puchho, sunke samjho** - Apni bhasa me baat karo!
💬 Garo | Khasi | Mizo | Kokborok | Assamese | Bengali | Hindi | English | Nagamese | Nepali
""")
st.info("👇 Bhasa chuno, phir Type karo ya 🎤 Mic se Bolo!")

col1, col2 = st.columns([2,1])
with col1:
    lang = st.selectbox("🌐 Language Chuno:", list(LANGUAGES.keys()), index=0)
with col2:
    if st.button("🗑️ Clear"):
        # FIX 2 - Clear par bhi Welcome from Meghalaya
        st.session_state.messages=[{"role":"assistant","content":"Welcome to our AI from Meghalaya! 🏔️ Bolo, kya help chahiye?"}]
        st.rerun()

def get_api_key():
    k = st.secrets.get("GROQ_API_KEY","") if hasattr(st, 'secrets') else ""
    return k.strip()

def get_reply(text, language):
    low=text.lower()
    creator_keywords = ["who made you","kisne banaya","tumhe kisne","creator","banaya kisne","who created","kaun bana","kon banaya","kisne bnaya","tumko kaun","tujhe kisne","tumhe kaun","tum ko kaun","bana ia","kaun banaya"]
    if any(k in low for k in creator_keywords):
        return f"Mujhe banaya hai {CREATOR_NAME} ne, {CREATOR_PLACE} se! 🏔️"

    api_key=get_api_key()
    if GROQ_AVAILABLE and api_key:
        try:
            client=Groq(api_key=api_key)
            # FIX 3 - GARO LOOP + NO NAME UNLESS ASKED
            if language in ["Garo", "Khasi", "Mizo", "Kokborok", "Nagamese"]:
                prompt = f"You are Northeast AI from Meghalaya. User language {language}. Reply in SIMPLE clear Roman English A-Z only, no repeat, max 4 lines. Do not mention creator. User: {text}"
            else:
                prompt = f"You are Northeast AI from Meghalaya. Do NOT mention creator {CREATOR_NAME} unless user asks who made you. Never say OpenAI. ONLY Roman English A-Z letters. Language={language}. User: {text}"

            comp=client.chat.completions.create(
                messages=[{"role":"system","content":"You are Northeast AI from Meghalaya. Reply only in Roman English, no loops, no OpenAI."},{"role":"user","content":prompt}],
                model="openai/gpt-oss-20b",
                max_tokens=800,
                temperature=0.6,
                extra_body={"reasoning_effort": "low"}
            )
            content = comp.choices[0].message.content
            if content and content.strip():
                if "openai" in content.lower():
                    return f"{LANGUAGES[language]}! Bolo kya help chahiye?"
                return content
            else:
                raise Exception("Empty")
        except Exception as e:
            try:
                prompt2 = f"Reply in {language} but ONLY Roman English A-Z, no repeat, no creator mention. User: {text}"
                comp=client.chat.completions.create(
                    messages=[{"role":"user","content":prompt2}],
                    model="qwen/qwen3-32b",
                    max_tokens=500)
                return comp.choices[0].message.content or f"{LANGUAGES[language]}! Hii"
            except Exception as e2:
                return f"{LANGUAGES[language]}! Bolo kya puchna hai?"
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

def speak_clear(text):
    try:
        tts=gTTS(text=text[:400], lang='en', tld='co.in', slow=False)
        fp=io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except:
        try:
            tts=gTTS(text=text[:400], lang='en', slow=False)
            fp=io.BytesIO()
            tts.write_to_fp(fp)
            return fp.getvalue()
        except:
            return None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"]=="assistant" and msg["content"].strip():
            audio = speak_clear(msg["content"])
            if audio:
                st.audio(audio, format="audio/mp3")

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
        audio = speak_clear(reply)
        if audio:
            st.audio(audio, format="audio/mp3", autoplay=True)
