import streamlit as st
from gtts import gTTS
import io
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

st.set_page_config(page_title="Northeast AI - Meghalaya", page_icon="🏔️", layout="centered")

CREATOR_NAME = "Samewan"
CREATOR_PLACE = "Meghalaya"

LANGUAGES = {
    "Garo": "Mitela", "Khasi": "Khublei", "Mizo": "Chibai",
    "Kokborok": "Hamjakma", "Assamese": "Nomoskar", "Bengali": "Nomoskar",
    "Hindi": "Namaste", "English": "Hello", "Nagamese": "Hello", "Nepali": "Namaste"
}

def get_welcome_text(lang):
    greets = {
        "Garo": "Mitela! Meghalaya a.songni Northeast AI-na welcome! 🏔️",
        "Mizo": "Chibai! Meghalaya atanga Northeast AI-ah kan lo lawm a che! 🏔️",
        "Khasi": "Khublei! Welcome from Meghalaya Northeast AI! 🏔️",
    }
    return greets.get(lang, "Welcome to our AI from Meghalaya! 🏔️")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": get_welcome_text("Garo")}]

st.title("🏔️ Northeast AI")
st.markdown("**🌟 Meghalaya's First 10-Language Voice AI**")
st.info("👇 Bhasa chuno, phir Type karo ya Mic se Bolo!")

col1, col2 = st.columns([2,1])
with col1:
    lang = st.selectbox("🌐 Language Chuno:", list(LANGUAGES.keys()), index=0)
with col2:
    if st.button("🗑️ Clear"):
        st.session_state.messages = [{"role": "assistant", "content": get_welcome_text(lang)}]
        st.rerun()

def get_api_key():
    try:
        if hasattr(st, 'secrets'):
            for name in ["GROQ_API_KEY", "groq_api_key", "GROQ"]:
                if name in st.secrets:
                    v = str(st.secrets[name])
                    v = v.replace("\n","").replace("\r","").replace(" ","").replace('"',"").replace("'","")
                    if len(v) > 20 and v.startswith("gsk_"):
                        return v
    except:
        pass
    import os
    return os.getenv("GROQ_API_KEY","").replace("\n","").strip()

def get_reply(text, language):
    low = text.lower().strip()
    is_mizo = any(w in low for w in ["ngaihtuah","i dam em","chibai","ka lawm","muttui","thiam em","chanchin"])
    is_hindi = any(w in low for w in ["kabre","batao","kaun hai","kya hai","mujhe","kaise","banana"])

    if "chief minister" in low and "meghalaya" in low:
        return "Hello! Chief Minister of Meghalaya is **Conrad K. Sangma**! NPP party, CM since 2018! Capital Shillong! 🏔️"
    if "chief minister" in low and "mizoram" in low:
        return "Chibai! Chief Minister of Mizoram is **Lalduhoma**! ZPM party! 🏔️"
    if "capital" in low and "meghalaya" in low:
        return "Hello! Capital of Meghalaya is **Shillong**! Scotland of the East! 🏔️"
    if "prime minister" in low and "india" in low:
        return "Hello! Prime Minister of India is **Narendra Modi**! Since 2014! 🏔️"

    if "shillong" in low:
        return "Hello! Shillong is capital of Meghalaya! Called Scotland of the East! Famous for Umiam Lake, Elephant Falls, Police Bazar! 🏔️"

    if any(k in low for k in ["kaise ai bana","ai kaise ban","ai banana hai","how to make ai"]):
        return f"Namaste! AI banana hai? {CREATOR_NAME} ne {CREATOR_PLACE} se banaya: 1) Python+Streamlit 2) groq.com se FREE API Key 3) Groq code 4) gTTS voice 5) Streamlit Cloud deploy! 💻🏔️"

    quick = {
        "muttui mangtha": "Muttui! Mangtha le! Naktukah kan in hmu leh dawn nia! 😴",
        "eng nge chanchin": "Chanchin tha! Ka lawm e! Nang eng nge i chanchin? Chibai! 🏔️",
        "i dam em": "Chibai! Ka dam e! Nang i dam em? 🏔️",
        "chibai": "Chibai! Eng nge chanchin? Ka tha e! 🏔️",
    }
    for k in sorted(quick.keys(), key=len, reverse=True):
        if k in low:
            return quick[k]
    if "mitela" in low: return "Mitela! Maikai? Anga tha! 😊🏔️"
    if "khublei" in low: return "Khublei! Kumno long? 😊🏔️"

    creator_keywords = ["who made you","kisne banaya","owner kaun","tumhe kisne banaya"]
    if any(k in low for k in creator_keywords):
        return f"Hello! I am Northeast AI! Created by {CREATOR_NAME} from {CREATOR_PLACE}! 🏔️"

    api_key = get_api_key()
    if GROQ_AVAILABLE and api_key and len(api_key) > 20 and api_key.startswith("gsk_"):
        try:
            client = Groq(api_key=api_key)
            for model_name in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "gemma2-9b-it"]:
                try:
                    target_lang = "Mizo" if is_mizo else ("Hindi" if is_hindi else language)
                    comp = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": f"You are Northeast AI by {CREATOR_NAME} from {CREATOR_PLACE}. Reply in {target_lang} Roman only. Max 4 lines."},
                            {"role": "user", "content": text}
                        ],
                        model=model_name,
                        max_tokens=700,
                        temperature=0.7
                    )
                    content = comp.choices[0].message.content
                    if content and content.strip():
                        return content
                except:
                    continue
        except:
            pass

    return f"Hello! About '{text}' - CM of Meghalaya is Conrad Sangma, capital Shillong! Ask me anything! 🏔️"

def transcribe_voice(audio_file):
    api_key = get_api_key()
    if GROQ_AVAILABLE and api_key and audio_file:
        try:
            client = Groq(api_key=api_key)
            tr = client.audio.transcriptions.create(
                file=("voice.wav", audio_file.getvalue()),
                model="whisper-large-v3"
            )
            return tr.text
        except:
            return None
    return None

def speak_clear(text):
    try:
        tts = gTTS(text=text[:400], lang='en', tld='co.in', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except:
        try:
            tts = gTTS(text=text[:400], lang='en', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            return fp.getvalue()
        except:
            return None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg["content"].strip():
            audio = speak_clear(msg["content"])
            if audio:
                st.audio(audio, format="audio/mp3")

st.divider()
st.markdown(f"**{LANGUAGES[lang]}! Type karo ya Mic dabao**")
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
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)
    reply = get_reply(user_text, lang)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
        audio = speak_clear(reply)
        if audio:
            st.audio(audio, format="audio/mp3", autoplay=True)
