import streamlit as st
from gtts import gTTS
import io, os
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False
st.set_page_config(page_title="Northeast AI - Meghalaya", page_icon="🏔️", layout="centered")
CREATOR_NAME = "Samewan"
CREATOR_PLACE = "Meghalaya"
LANGUAGES = {"Garo": "Mitela", "Khasi": "Khublei", "Mizo": "Chibai","Kokborok": "Hamjakma", "Assamese": "Nomoskar", "Bengali": "Nomoskar","Hindi": "Namaste", "English": "Hello", "Nagamese": "Hello", "Nepali": "Namaste"}
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
    clean = "".join(raw.split()).replace('"','').replace("'","")
    return clean

def is_looping(text):
    t = text.lower()
    # Mizo aur Khasi loop detection
    if t.count("chhuak a") > 3: return True
    if t.count("a chhuak") > 4: return True
    if t.count("phur chhuak") > 2: return True
    if t.count("jingbeng") > 3: return True
    if t.count("ka shaba") > 4: return True
    if t.count("a, a") > 6: return True
    return False

def get_reply(text, language):
    api_key = get_api_key()
    if GROQ_AVAILABLE and api_key.startswith("gsk_") and len(api_key) > 20:
        try:
            client = Groq(api_key=api_key)
            for model_name in ["llama-3.1-8b-instant", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "meta-llama/llama-4-scout-17b-16e-instruct"]:
                try:
                    comp = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": f"You are Northeast AI by {CREATOR_NAME} from {CREATOR_PLACE}. User language: {language}. CRITICAL: Reply in simple Roman. If {language} is Mizo/Khasi/Garo and you don't know fluent translation, reply in simple English or Hindi mixed, but NEVER repeat same phrase like 'a chhuak a' or 'phur chhuak'. Explain black hole clearly if asked. Max 6 lines, no looping."},
                            {"role": "user", "content": text}
                        ],
                        model=model_name,
                        max_tokens=800,
                        temperature=0.5,
                        frequency_penalty=1.8,
                        presence_penalty=0.8
                    )
                    content = comp.choices[0].message.content
                    if content and content.strip():
                        if is_looping(content):
                            continue
                        return content
                except Exception as e:
                    last_err = str(e)
                    continue
            return f"Groq Error: {last_err[:400]}"
        except Exception as e:
            return f"Connect Error: {str(e)[:300]}"
    return f"⚠️ API Key missing len {len(api_key)}"
def transcribe_voice(audio_file):
    api_key = get_api_key()
    if GROQ_AVAILABLE and api_key and audio_file:
        try:
            client = Groq(api_key=api_key)
            tr = client.audio.transcriptions.create(file=("voice.wav", audio_file.getvalue()),model="whisper-large-v3")
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
    with st.chat_message
