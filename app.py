import streamlit as st
from gtts import gTTS
import io, os, re

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

st.set_page_config(page_title="Northeast AI - Meghalaya", page_icon="🏔️", layout="centered")

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
    bad = ["thil chu hmu", "hmu chu thil", "thil hmu chu", "beng beng", "jingpynshang", "ka jing"]
    for b in bad:
        if t.count(b) >= 2:
            return True
    words = t.split()
    for i in range(len(words)-2):
        if words[i] == words[i+1] == words[i+2]:
            return True
    return False

def remove_loop_and_fix(text):
    parts = text.split('.')
    seen = []
    out = []
    for p in parts:
        s = p.strip().lower()
        if not s or len(s) < 3:
            continue
        if s not in seen:
            seen.append(s)
            out.append(p.strip())
    fixed = ". ".join(out)
    if fixed and not fixed.endswith('.'):
        fixed += '.'
    return fixed[:450]

def get_reply(text, language):
    api_key = get_api_key()
    if GROQ_AVAILABLE and api_key.startswith("gsk_") and len(api_key) > 20:
        try:
            client = Groq(api_key=api_key)
            system_prompt = (
                "You are Northeast AI by Samewan from Meghalaya. "
                "CRITICAL: ALL output MUST be Roman English letters only. "
                "No Devanagari, No Bengali script. "
                "Hindi example: Kala chhidra ek aisa sthan hai jaha gurutvakarshan bahut tez hota hai. "
                "User language: " + language + ". Answer in " + language + " Roman only. "
                "MAX 2-3 short sentences. NEVER repeat words. "
                "Mizo GOOD: Black hole chu vana thil chak tak a ni a, engkim a hip lut a."
            )
            last_err = "No model worked"
            for model_name in ["llama-3.3-70b-versatile", "openai/gpt-oss-20b", "openai/gpt-oss-120b"]:
                try:
                    comp = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ],
                        model=model_name,
                        max_tokens=250,
                        temperature=0.65,
                        top_p=0.9
                    )
                    content = comp.choices[0].message.content
                    if content and content.strip():
                        if is_looping(content):
                            content = remove_loop_and_fix(content)
                            if is_looping(content):
                                continue
                        return remove_loop_and_fix(content)
                except Exception as e:
                    last_err = str(e)
                    continue
            return "Groq Error: " + last_err[:400]
        except Exception as e:
            return "Connect Error: " + str(e)[:300]
    return "API Key missing"

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
        clean = re.sub(r"[^A-Za-z0-9 ,.]", " ", clean)
        clean = clean[:350].strip()
        if len(clean) < 5:
            return None
        tts = gTTS(text=clean, lang='en', tld='co.in', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except Exception:
        return None

def render_message(content):
    if "```" in content:
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
