import streamlit as st
from gtts import gTTS
import io, os, re
from groq import Groq

st.set_page_config(page_title="Northeast AI - Meghalaya", page_icon="🏔️", layout="centered")

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
    key = ""
    try:
        key = st.secrets["GROQ_API_KEY"]
    except:
        key = os.getenv("GROQ_API_KEY", "")
    # Fix: Remove spaces, quotes, newlines
    key = str(key).strip().replace('"','').replace("'","").replace(" ","").replace("\n","")
    return key

def is_looping(text):
    t = text.lower()
    for phrase in ["thil chu hmu", "hmu chu thil", "thil hmu chu", "beng beng"]:
        if t.count(phrase) >= 2:
            return True
    words = t.split()
    for i in range(len(words)-2):
        if words[i]==words[i+1]==words[i+2]:
            return True
    return False

def remove_loop_and_fix(text):
    parts = text.split('.')
    seen, out = [], []
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
    
    # Debug info if key missing
    if not api_key.startswith("gsk_"):
        return f"API Key Error: Secrets me GROQ_API_KEY nahi mila! Key len={len(api_key)} Start={api_key[:4]}. Secrets me gsk_ se start hone wala naya key dalo."
    
    try:
        client = Groq(api_key=api_key)
        system_prompt = f"You are Northeast AI by Samewan from Meghalaya. CRITICAL RULE: Answer ONLY in Roman English letters. NEVER use native script. Hindi must be Roman like: Kala chhidra ek aisa sthan hai. Mizo GOOD example: Black hole chu vana thil chak tak a ni a. User language: {language}. Answer in {language} Roman only. MAX 2 sentences. BANNED PHRASES: thil chu hmu, hmu chu thil."
        
        last_err = "No error captured"
        for model_name in ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]:
            try:
                comp = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    model=model_name,
                    max_tokens=300,
                    temperature=0.6,
                    top_p=0.9
                )
                content = comp.choices[0].message.content
                if content and content.strip():
                    if is_looping(content):
                        content = remove_loop_and_fix(content)
                        if is_looping(content):
                            last_err = f"Loop detected in {model_name}, trying next"
                            continue
                    return remove_loop_and_fix(content)
                else:
                    last_err = f"{model_name} returned empty"
            except Exception as e:
                last_err = str(e)
                continue
        
        return f"REAL GROQ ERROR: {last_err[:500]}"
        
    except Exception as e:
        return f"Connect Error: {str(e)[:500]}"

def transcribe_voice(audio_file):
    api_key = get_api_key()
    if api_key.startswith("gsk_") and audio_file:
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
        clean = re.sub(r"[^A-Za-z0-9 ,.]", " ", clean)[:350].strip()
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
