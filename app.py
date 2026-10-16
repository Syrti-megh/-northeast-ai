import streamlit as st
from gtts import gTTS
import io, os, re

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

st.set_page_config(page_title="Northeast AI - Meghalaya", page_icon="🏔️", layout="centered")

# --- CODE CUT FIX CSS ---
st.markdown("""
<style>
div[data-testid="stCodeBlock"] pre {
    white-space: pre-wrap!important;
    word-wrap: break-word!important;
}
code {
    white-space: pre-wrap!important;
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
    if t.count("hriatna") > 3: return True
    if t.count("thlawnna") > 3: return True
    if t.count("chhuak a") > 3: return True
    if t.count("phur chhuak") > 2: return True
    if t.count("jingbeng") > 3: return True
    if t.count("ka shaba") > 4: return True
    return False

def get_reply(text, language):
    api_key = get_api_key()
    if GROQ_AVAILABLE and api_key.startswith("gsk_") and len(api_key) > 20:
        try:
            client = Groq(api_key=api_key)
            system_prompt = f"You are Northeast AI by Samewan from Meghalaya. User language is {language}. Reply in simple Roman. If {language} is Mizo, Khasi, Garo, Kokborok and you are not fluent, reply in simple Hindi+English mix but never repeat same phrase like a chhuak a or hriatna. If user asks for code, give SHORT variable names like a,b,op and keep lines <40 chars. Use ```python block."
            for model_name in ["meta-llama/llama-4-scout-17b-16e-instruct", "openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.1-8b-instant"]:
                try:
                    comp = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ],
                        model=model_name,
                        max_tokens=1200,
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
            return "Groq Error: " + last_err[:300]
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
        clean = clean[:400]
        tts = gTTS(text=clean, lang='en', tld='co.in', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except:
        return None

def render_message(content):
    # Simple and stable
    if "```" in content:
        # text + code alag
        text_part = re.sub(r"```.*?```", "", content, flags=re.DOTALL).strip()
        if text_part:
            st.write(text_part)
        codes = re.findall(r"```(?:python)?(.*?)```", content, re.DOTALL)
        for c in codes:
            st.code(c.strip(), language="python")
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
