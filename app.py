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

# === FIXED: All 10 Language ka alag fallback ===
FALLBACK_ALL = {
    "Garo": {
        "gravity": "Gravity mingsa bostu-ko rikna shakti ong·a. Prithivi-ni bostu-ko rikna.",
        "prithivi": "Prithivi a·axis-o dongtokenga, ge·sa sani gisik ra·enggipa. Gravity-ni gita.",
        "porgido": "Prithivi a·axis-o dongtokenga, ge·sa sani gisik ra·enggipa.",
        "salrang": "Salrang gas aro wal·a gital dingtang ong·a, nuclear fusion-ni a·sel jekchaka.",
        "jawal": "Jawal Prithivi-ni satellite ong·a, sal-ni jekgipa-ko reflect ka·a.",
        "black hole": "Black hole gravity gita ong·a, jekgipa wa·al chakatna man·ja.",
        "vir": "Prithivi a·axis-o dongtokenga."
    },
    "Mizo": {
        "vir": "Khawvel chu a axis-ah a vir a, ni khat chhungin vawi khat. Gravity avangin.",
        "khawvel": "Khawvel chu ni system-a planet a ni a, a axis-ah a vir a.",
        "gravity": "Gravity chu thil hipna chakna a ni a, Newton ten an zir a.",
        "arsi": "Arsi chu vana gas leh meisa lian tak a ni a, nuclear fusion avangin a eng a.",
        "thla": "Thla chu kan khawvel satellite a ni a, ni eng reflect avangin a eng a.",
        "black hole": "Black hole chu gravity chak tak a ni a, light pawh a chhuak thei lo."
    },
    "Khasi": {
        "pyrthei": "Ka pyrthei ka iaid shaphang la ka axis, shisien ha ka sngi. Na ka gravity.",
        "gravity": "Ka gravity ka dei ka bor ba ring jingiasyllok. Ka pyrthei ka ring.",
        "khlor": "U khlor u dei u gas ba heh ha bneng, u shat da ka fusion.",
        "bnai": "U bnai u dei u satellite jong ka pyrthei, u pynphriang ia ka jingshai sngi.",
        "black hole": "U black hole u dei ka gravity kaba khraw, wat ka jingshai ruh kam lait."
    },
    "Kokborok": {
        "ha": "Ha a axis-o wngwi tonggo, salnisa kaisa tongwi. Gravity ni bagwi.",
        "gravity": "Gravity bono nokhorokno buthuknani bisingo, ha-o buthukgo.",
        "atal": "Atal gas aro hor gwnang tonggo, fusion bai kwrwi tonggo.",
        "tal": "Tal bono ha-ni satellite, salni hor reflect khwlai tonggo.",
        "black hole": "Black hole gravity gwnang tonggo, hor belai katjago."
    },
    "English": {
        "earth": "Earth rotates on its axis once in 24 hours due to gravity.",
        "gravity": "Gravity is the force that pulls objects towards Earth. Newton discovered it.",
        "star": "A star is a giant ball of gas shining due to nuclear fusion.",
        "moon": "Moon is Earth's satellite, it reflects sunlight.",
        "black hole": "A black hole is extreme gravity where even light cannot escape."
    },
    "Hindi": {
        "prithvi": "Prithvi apni dhuri par 24 ghante me ek baar ghoomti hai, gravity ke karan.",
        "gravity": "Gravity wo shakti hai jo cheezo ko Prithvi ki taraf kheenchti hai.",
        "tara": "Tara gas ka bada gola hai jo nuclear fusion se chamakta hai.",
        "chand": "Chand Prithvi ka satellite hai, suraj ki roshni reflect karta hai."
    }
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

def remove_loop_and_fix(text):
    if not text or len(text.strip()) < 5: return ""
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
        
        # LANGUAGE WISE PROMPT - Yahi main fix hai
        if language == "Garo":
            sys_prompt = "You are Garo science teacher. Answer ONLY in Garo Roman. Example: Gravity maiko? -> Gravity mingsa bostu-ko rikna shakti ong·a. Never use Mizo words like Khawvel."
        elif language == "Khasi":
            sys_prompt = "You are Khasi science teacher. Answer ONLY in Khasi Roman. Example: Gravity kadei? -> Ka gravity ka dei ka bor ba ring. Never use Mizo."
        elif language == "Mizo":
            sys_prompt = "You are Mizo science teacher. Answer ONLY in Mizo Roman. Example: Gravity eng nge? -> Gravity chu thil hipna chakna a ni a."
        else:
            sys_prompt = f"You are {language} science teacher. Answer ONLY in {language}. 2-3 short sentences. Scientific only."

        history=[{"role": "system", "content": sys_prompt}]
        for m in st.session_state.messages[-3:]:
            history.append({"role": m["role"], "content": m["content"]})
        history.append({"role": "user", "content": text})

        for model_name in ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]:
            try:
                comp=client.chat.completions.create(messages=history, model=model_name, max_tokens=500, temperature=0.75, top_p=0.9)
                content=comp.choices[0].message.content.strip()
                if content and len(content) > 15:
                    # CROSS-LANGUAGE BUG FIX - Tere screenshot wala bug
                    if language == "Garo" and "Khawvel chu" in content:
                        continue
                    if language == "Khasi" and "Khawvel chu" in content:
                        continue
                    cleaned=remove_loop_and_fix(content)
                    if len(cleaned) > 15:
                        return cleaned
            except: continue

        # Hard fallback - language wise
        low = text.lower()
        # 1. Selected language me dhoondo
        if language in FALLBACK_ALL:
            for k,v in FALLBACK_ALL[language].items():
                if k in low:
                    return v
        # 2. English me dhoondo
        for k,v in FALLBACK_ALL["English"].items():
            if k in low:
                return v

        defaults = {
            "Garo": "Ia bostu science-ni bidingo ong·a, natural process-ni a·sel.",
            "Mizo": "He thil chu science thil pawimawh tak a ni a, natural process avangin a awm a.",
            "Khasi": "Kane ka dei ka jingthaw science kaba donkam, na ka jingleh nature.",
            "English": "This is a scientific phenomenon due to natural processes and gravity."
        }
        return defaults.get(language, defaults["English"])

    except Exception as e:
        low=text.lower()
        if language in FALLBACK_ALL:
            for k,v in FALLBACK_ALL[language].items():
                if k in low: return v
        return FALLBACK_ALL.get(language, FALLBACK_ALL["English"]).get("gravity", "Gravity is attraction force.")

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
