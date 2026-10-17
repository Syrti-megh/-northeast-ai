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
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to Northeast AI! 🏔️🔬"}]

st.title("🏔️ Northeast AI")
st.markdown("**🌟 Meghalaya's First 10-Language Scientific Voice AI**")

col1, col2 = st.columns([2, 1])
with col1:
    lang = st.selectbox("🌐 Language Chuno:", list(LANGUAGES.keys()), index=0)
with col2:
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        st.rerun()

def get_api_key():
    key = ""
    try: key = st.secrets["GROQ_API_KEY"]
    except: key = os.getenv("GROQ_API_KEY", "")
    return str(key).strip().replace('"','').replace("'","").replace(" ","").replace("\n","")

def is_looping(text):
    t = text.lower()
    if t.count("a hman a") >= 2: return True
    if t.count("a mass") >= 2 or t.count("a energy") >= 2: return True
    sentences = [s.strip() for s in text.split('.') if len(s.strip())>5]
    lower = [s.lower() for s in sentences]
    if len(lower) != len(set(lower)): return True
    return False

def remove_loop_and_fix(text):
    parts = [p.strip() for p in text.split('.') if p.strip()]
    seen=set(); out=[]
    for p in parts:
        low=p.lower()
        if "a hman a" in low and any("a hman a" in o.lower() for o in out): continue
        if low not in seen and len(p) > 10:
            seen.add(low); out.append(p)
        if len(out) >= 2: break
    fixed=". ".join(out)
    fixed=re.sub(r'\s+',' ',fixed).strip()
    if fixed and not fixed.endswith('.'): fixed+='.'
    return fixed[:400] if fixed else "Ka hrethiam lo."

def get_reply(text, language):
    api_key=get_api_key()
    if not api_key.startswith("gsk_"): return "API Key Error!"
    try:
        client=Groq(api_key=api_key)
        system_prompt=f"""You are Northeast AI by Samewan, SCIENTIFIC TEACHER.
Answer ONLY current question in {language} Roman letters.
RULES: 1) 2 short scientific sentences max. 2) No spiritual words. 3) NEVER repeat 'A hman a, a mass a'.
If user asks Arsi, explain Arsi. If Thla, explain Thla. If Black hole, explain Black hole."""

        # === HISTORY ADDED - AB HAR SAWAL KA SAHI JAWAB DEGA ===
        history=[{"role": "system", "content": system_prompt}]
        for m in st.session_state.messages[-3:]:
            history.append({"role": m["role"], "content": m["content"]})
        history.append({"role": "user", "content": text})

        for model_name in ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]:
            try:
                comp=client.chat.completions.create(messages=history, model=model_name, max_tokens=180, temperature=0.3, top_p=0.8)
                content=comp.choices[0].message.content.strip()
                if content:
                    cleaned=remove_loop_and_fix(content)
                    if not is_looping(cleaned) and len(cleaned)>15:
                        return cleaned
            except: continue
        return "Ka hrethiam lo, min han zawt tha leh rawh."
    except Exception as e:
        return f"Error: {str(e)[:200]}"

def transcribe_voice(audio_file):
    try:
        client=Groq(api_key=get_api_key())
        tr=client.audio.transcriptions.create(file=("voice.wav", audio_file.getvalue()), model="whisper-large-v3")
        return tr.text
    except: return None

def speak_clear(text):
    try:
        clean=re.sub(r"[^A-Za-z0-9 ,.]"," ",text)[:350].strip()
        if len(clean)<5: return None
        tts=gTTS(text=clean, lang='en', tld='co.in', slow=False)
        fp=io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()
    except: return None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

st.divider()
voice_input=st.audio_input("🎤 " + lang + " me Bolo")
user_text=None
if voice_input:
    with st.spinner("Sun raha hu..."):
        trans=transcribe_voice(voice_input)
        if trans: user_text=trans; st.success("Suna: "+trans)

text_input=st.chat_input(LANGUAGES[lang]+"! Yahan likho...")
if text_input: user_text=text_input

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"): st.write(user_text)
    reply=get_reply(user_text, lang)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
        audio=speak_clear(reply)
        if audio: st.audio(audio, format="audio/mp3", autoplay=True)
