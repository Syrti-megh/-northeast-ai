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

# === FIXED 1: Filter halka kiya ===
def is_looping(text):
    t = text.lower()
    # Sirf bahut dangerous loop ko rokega
    if t.count("a hman a") >= 4: return True
    if "a hman a, a mass a, a energy a, a thil a" in t: return True
    return False

def remove_loop_and_fix(text):
    if not text: return "Ka hrethiam lo."
    parts = [p.strip() for p in text.split('.') if p.strip()]
    seen=set(); out=[]
    for p in parts:
        low=p.lower()
        if low not in seen and len(p) > 4:
            seen.add(low); out.append(p)
        if len(out) >= 3: break
    fixed=". ".join(out)
    fixed=re.sub(r'\s+',' ',fixed).strip()
    if fixed and not fixed.endswith('.'): fixed+='.'
    # Agar khali bhi ho to original text de do, "Ka hrethiam lo" mat do
    return fixed[:800] if fixed else text[:800]

def get_reply(text, language):
    api_key=get_api_key()
    if not api_key.startswith("gsk_"): return "API Key Error! Secrets check karo."
    try:
        client=Groq(api_key=api_key)
        system_prompt=f"""You are Northeast AI by Samewan, SCIENTIFIC TEACHER.
User asked in {language} language. Answer in {language} ROMAN letters only.

Examples:
If Arsi eng nge -> Arsi chu vana gas leh meisa lian tak a ni a, nuclear fusion avangin a eng a. A eng avangin kan hmu thei a.
If Thla eng nge -> Thla chu kan khawvel satellite a ni a, ni eng a reflect avangin a eng a.
If Black hole eng nge -> Black hole chu gravity chak tak a ni a, light pawh a chhuak thei lo.

RULES: 2-3 short scientific sentences. No spiritual. No loop.
Answer CURRENT question only."""

        history=[{"role": "system", "content": system_prompt}]
        for m in st.session_state.messages[-3:]:
            history.append({"role": m["role"], "content": m["content"]})
        history.append({"role": "user", "content": text})

        # FIXED 2: Temperature + tokens badhaye
        comp=client.chat.completions.create(
            messages=history, 
            model="openai/gpt-oss-20b", 
            max_tokens=400, 
            temperature=0.7,
            top_p=0.9
        )
        content=comp.choices[0].message.content.strip()
        if content:
            cleaned=remove_loop_and_fix(content)
            return cleaned
        return "Min han zawt tha leh rawh, ka hria ang."
    except Exception as e:
        return f"Error: {str(e)[:300]}"

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
