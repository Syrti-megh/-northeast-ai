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
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to Northeast AI - Scientific Edition from Meghalaya! 🏔️🔬"}]

st.title("🏔️ Northeast AI")
st.markdown("**🌟 Meghalaya's First 10-Language Scientific Voice AI**")

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
    return fixed[:500]

def get_reply(text, language):
    api_key = get_api_key()
    if not api_key.startswith("gsk_"):
        return f"API Key Error: Secrets me GROQ_API_KEY nahi mila! Key len={len(api_key)}"
    try:
        client = Groq(api_key=api_key)
        # === SCIENTIFIC UPGRADE FOR ALL LANGUAGES ===
        system_prompt = f"""You are Northeast AI by Samewan, a SCIENTIFIC TEACHER from Meghalaya.
YOUR JOB: Give 100% scientific, educational, factual answer.

STRICT RULES:
1. NEVER use spiritual/religious words like thlarau, atma, soul, bhagwan. Only science.
2. ALL output MUST be in Roman letters only (English alphabet). No native script.
3. User language: {language}. You MUST answer in {language} but using Roman letters.
4. Explain with science terms: gravity, light, energy, space, mass, etc.
5. MAX 2-3 short scientific sentences.

SCIENTIFIC EXAMPLES:
- For "Black hole eng nge" in Mizo Roman: Black hole chu vana hmun a ni a, a gravity chak lutuk avangin engkim a hip lut a, eng pawh a chhuak thei lo, eng light pawh.
- For "black hole kya hai" in Hindi Roman: Kala chhidra aakash me aisa sthan hai jaha gurutvakarshan itna shaktishali hota hai ki prakash bhi bahar nahi nikal pata, iska nirmaan bade tare ke samapt hone par hota hai.

Now give scientific answer in {language} Roman."""

        last_err = "No error"
        for model_name in ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]:
            try:
                comp = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    model=model_name,
                    max_tokens=350,
                    temperature=0.5,
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
        return f"Groq Error: {last_err[:400]}"
    except Exception as e:
        return f"Error: {str(e)[:400]}"

def transcribe_voice(audio_file):
    api_key = get_api_key()
    if api_key.startswith("gsk_") and audio_file:
        try:
            client = Groq(api_key=api_key)
            tr = client.audio.transcriptions.create(file=("voice.wav", audio_file.getvalue()), model="whisper-large-v3")
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
