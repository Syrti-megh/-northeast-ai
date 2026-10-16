import streamlit as st
from gtts import gTTS
import io, os, re

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

st.set_page_config(page_title="Northeast AI - Meghalaya", page_icon="🏔️", layout="centered")

st.markdown("""
<style>
div[data-testid="stCodeBlock"] {
    overflow-x: auto!important;
    max-width: 100%!important;
}
div[data-testid="stCodeBlock"] pre {
    white-space: pre!important;
}
</style>
""", unsafe_allow_html=True)

CREATOR_NAME = "Samewan"
CREATOR_PLACE = "Meghalaya"

LANGUAGES = {
    "Garo": "Mitela", "Khasi": "Khublei", "Mizo": "Chibai",
    "Kokborok": "Hamjakma", "Assamese": "Nomoskar", "Bengali": "Nomoskar",
    "Hindi": "Namaste", "English": "Hello", "Nagamese": "Hello", "Nepali": "Namaste"
}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Garo - Welcome to Northeast AI from Meghalaya! 🏔️"}]

st.title("🏔️ Northeast AI")
st.markdown("**🌟 Meghalaya's First 10-Language Voice AI**")

col1, col2 = st.columns([2, 1])
with col1:
    lang = st.selectbox("🌐 Language Chuno:", list(LANGUAGES.keys()), index=0)
with col2:
    if st.button("🗑️ Clear"):
        st.session_state.messages = [{"role": "assistant", "content": f"{lang} - Welcome!"}]
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
        raw = os.getenv("GROQ_API_KEY", "")
    clean = "".join(raw.split()).replace('"', "").replace("'", "")
    return clean

def is_looping(text):
    t = text.lower()
    bad_phrases = ["hriatna", "thlawnna", "chhuak a", "phur chhuak", "jingbeng", "ka shaba", "beng beng", "a beng", "gipa", "jingpynshang", "jingpyrkhat", "jingmut", "ka jing"]
    for phrase in bad_phrases:
        if t.count(phrase) >= 3:
            return True
    words = t.split()
    for i in range(len(words)-2):
        if words[i]==words[i+1]==words[i+2]:
            return True
        if i < len(words)-4 and words[i]=="ka" and words[i+2]=="ka" and words[i+4]=="ka":
            if words[i+1]==words[i+3]:
                return True
    return False

def get_reply(text, language):
    api_key = get_api_key()
    if GROQ_AVAILABLE and api_key.startswith("gsk_") and len(api_key) > 20:
        try:
            client = Groq(api_key=api_key)
            system_prompt = f"You are Northeast AI by Samewan from Meghalaya. User language: {language}. CRITICAL RULES: 1) Answer in {language} only. 2) NEVER repeat any word more than twice. 3) BANNED PHRASES: 'a beng beng', 'jingpynshang', 'jingpyrkhat', 'hriatna'. 4) Max 2 short sentences, simple words. 5) For Python code: Give CLEAN multiline code in ```python block. Use short vars Num1, Num2, Op, result. Format: Num1 = float(input('Num1: ')) NEWLINE Num2 = float(input('Num2: ')) etc. Always end with print(result)."

            last_err = "No model worked"
            for model_name in ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]:
                try:
                    comp = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ],
                        model=model_name,
                        max_tokens=2000,
                        temperature=0.2
                    )
                    content = comp.choices[0].message.content
                    if content and content.strip():
                        if is_looping(content):
                            continue
                        return content
                except Exception as e:
                    last_err = str(e)
                    continue
            return "Groq Error: " + last_err[:400]
        except Exception as e:
            return "Connect Error: " + str(e)[:300]
    return "API Key missing len " + str(len(api_key))

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
        clean = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
        clean = re.sub(r"[^\w\s,.]", " ", clean)
        clean = clean[:350].strip()
        if len(clean) < 5:
            return None
        tts = gTTS(text=clean, lang='en', tld='co.in', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except:
        return None

def render_message(content):
    if "```" in content:
        text_part = re.sub(r"```.*?```", "", content, flags=re.DOTALL).strip()
        if text_part:
            st.write(text_part)
        codes = re.findall(r"```(?:python)?(.*?)```", content, re.DOTALL)
        for c in codes:
            code_clean = c.strip()
            if code_clean.endswith("\n result") or code_clean.endswith("\nresult"):
                code_clean += " = 'Invalid operator'"
            st.code(code_clean, language="python")
    else:
        st.write(content)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        render_message(msg["content"])

st.divider()

voice_input = st.audio_input("🎤 " + lang + " me Bolo")
user_text = None
if voice_input:
    with st.spinner("Sun raha hu..."):
        transcribed = transcribe_voice(voice_input)
        if transcribed:
            user_text = transcribed
            st.success("🎤 Suna: " + transcribed)

text_input = st.chat_input(LANGUAGES[lang] + "! Yahan likho...")
if text_input:
    user_text = text_input

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)
    reply = get_reply(user_text, lang)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        render_message(reply)
        audio = speak_clear(reply)
        if audio:
            st.audio(audio, format="audio/mp3", autoplay=True)
