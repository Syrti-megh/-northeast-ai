import streamlit as st
from gtts import gTTS
import io
import os

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
    return f"{lang} - Welcome to Northeast AI from Meghalaya! 🏔️"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": get_welcome_text("Garo")}]

st.title("🏔️ Northeast AI")
st.markdown("**🌟 Meghalaya's First 10-Language Voice AI**")

col1, col2 = st.columns([2,1])
with col1:
    lang = st.selectbox("🌐 Language Chuno:", list(LANGUAGES.keys()), index=0)
with col2:
    if st.button("🗑️ Clear"):
        st.session_state.messages = [{"role": "assistant", "content": get_welcome_text(lang)}]
        st.rerun()

# --- FIXED - 3 line ko 1 line banayega ---
def get_api_key():
    raw = ""
    try:
        if hasattr(st, 'secrets'):
            for name in ["GROQ_API_KEY", "groq_api_key", "GROQ"]:
                if name in st.secrets:
                    raw = str(st.secrets[name])
                    break
    except:
        pass
    if not raw:
        raw = os.getenv("GROQ_API_KEY","")
    # Saare Enter, Space, Quotes hatao
    clean = "".join(raw.split())
    clean = clean.replace('"','').replace("'","")
    return clean

def get_reply(text, language):
    low = text.lower().strip()
    api_key = get_api_key()

    # Sidebar me status
    with st.sidebar:
        if api_key.startswith("gsk_"):
            st.success(f"✅ Key OK: len {len(api_key)}")
        else:
            st.error(f"❌ Key FAIL len {len(api_key)}")

    # Groq - Sabse pehle try karo (CM wala block hata diya)
    if GROQ_AVAILABLE and api_key.startswith("gsk_") and len(api_key) > 20:
        try:
            client = Groq(api_key=api_key)
            for model_name in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "gemma2-9b-it"]:
                try:
                    comp = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": f"You are Northeast AI by {CREATOR_NAME} from {CREATOR_PLACE}. Reply in {language} Roman only. Max 6 lines, helpful."},
                            {"role": "user", "content": text}
                        ],
                        model=model_name,
                        max_tokens=800,
                        temperature=0.7
                    )
                    content = comp.choices[0].message.content
                    if content and content.strip():
                        return content
                except Exception as e:
                    last_err = str(e)
                    continue
            return f"Groq Error: {last_err[:200]}"
        except Exception as e:
            return f"Groq Connect Error: {str(e)[:200]}"

    # Fallback - sirf tab jab key hi nahi
    if "chief minister" in low and "meghalaya" in low:
        return "CM of Meghalaya is Conrad K. Sangma! 🏔️"
    return f"⚠️ API Key missing/invalid (len {len(api_key)}). Secrets me naya gsk_ key lagao! 🏔️"

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
        return None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

st.divider()
voice_input = st.audio_input(f"🎤 {lang} me Bolo")
user_text = None
if voice_input:
    with st.spinner("Sun raha hu..."):
        transcribed = transcribe_voice(voice_input)
        if transcribed:
            user_text = transcribed
            st.success(f"🎤 Suna: {transcribed}")

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
