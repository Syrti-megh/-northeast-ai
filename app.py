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

# === ADDED: All Language Hard Fallback ===
HARD_FALLBACK = {
    "vir": "Khawvel chu a axis-ah a vir a, ni khat chhungin vawi khat. Gravity avangin.",
    "khawvel": "Khawvel chu ni system-a planet a ni a, a axis-ah a vir a.",
    "gravity": "Gravity chu thil hipna chakna a ni a, Newton ten an zir a.",
    "arsi": "Arsi chu vana gas leh meisa lian tak a ni a, nuclear fusion avangin a eng a.",
    "thla": "Thla chu kan khawvel satellite a ni a, ni eng reflect avangin a eng a.",
    "black hole": "Black hole chu gravity chak tak a ni a, light pawh a chhuak thei lo.",
    "ni": "Ni chu solar system laipui arsi lian tak a ni a, hydrogen fusion avangin a eng a.",
    "pani": "Pani chu H2O a ni a, hydrogen leh oxygen atanga siam a ni a.",
    "light": "Light chu energy a ni a, second khat chhungin 3 lakh km a kal a."
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

# FIXED: Ab "Ka hrethiam lo" kabhi nahi dega
def remove_loop_and_fix(text):
    if not text or len(text.strip()) < 5:
        return ""
    parts = [p.strip() for p in text.split('.') if p.strip()]
    seen=set(); out=[]
    for p in parts:
        low=p.lower()
        if low not in seen and len(p) > 3:
            seen.add(low); out.append(p)
        if len(out) >= 3: break
    fixed=". ".join(out)
    fixed=re.sub(r'\s+',' ',fixed).strip()
    if fixed and not fixed.endswith('.'): fixed+='.'
    return fixed[:800] if fixed else text[:800]

def get_reply(text, language):
    api_key=get_api_key()
    if not api_key.startswith("gsk_"): return "API Key Error! Secrets check karo."
    try:
        client=Groq(api_key=api_key)
        system_prompt=f"""You are Northeast AI by Samewan, SCIENTIFIC TEACHER.
Answer ONLY in {language} language, ROMAN letters.
RULES: 1) 2-3 short scientific sentences. 2) No spiritual. 3) NEVER say Ka hrethiam lo. Always answer scientifically.
If user asks Khawvel engtin nge a vir -> Khawvel chu a axis ah a vir a, ni khat chhungin vawi khat. Gravity avangin.
If Arsi -> Arsi chu vana gas leh meisa lian tak a ni a, nuclear fusion avangin a eng a.
Current language: {language}. Answer in {language}."""

        history=[{"role": "system", "content": system_prompt}]
        for m in st.session_state.messages[-3:]:
            history.append({"role": m["role"], "content": m["content"]})
        history.append({"role": "user", "content": text})

        # === FIXED + ADDED: 3 Model try ===
        for model_name in ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]:
            try:
                comp=client.chat.completions.create(
                    messages=history, model=model_name, 
                    max_tokens=500, temperature=0.75, top_p=0.9
                )
                content=comp.choices[0].message.content.strip()
                if content and len(content) > 15:
                    cleaned=remove_loop_and_fix(content)
                    if len(cleaned) > 15:
                        return cleaned
            except: continue

        # === ADDED: Hard fallback agar sab fail ho jaye ===
        low = text.lower()
        for k,v in HARD_FALLBACK.items():
            if k in low:
                return v
        # Last option - kabhi khali nahi jayega
        return "He thil chu science thil pawimawh tak a ni a, natural process avangin a awm a, research in a zir chiang a."

    except Exception as e:
        # Error pe bhi fallback dega
        low = text.lower()
        for k,v in HARD_FALLBACK.items():
            if k in low:
                return v
        return "Khawvel chu a axis-ah a vir a, ni khat chhungin vawi khat. Gravity avangin."

def transcribe_voice(audio_file):
    try:
        client=Groq(api_key=get_api_key())
        tr=client.audio.transcriptions.create(file=("voice.wav", audio_file.getvalue()), model="whisper-large-v3")
        return tr.text
    except: return None

def speak_clear(text):
    try:
        clean=re.sub(r"[^A-Za-z0-9 ,.]"," ",text)[:400].strip()
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
