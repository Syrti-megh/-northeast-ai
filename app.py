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

# === ALL 10 LANGUAGE FALLBACK - SAB ROMAN ME ===
FALLBACK_ALL = {
    "Garo": {
        "gravity": "Gravity mingsa bostu-ko rikna shakti ong·a. Prithivi-ni bostu-ko rikna.",
        "prithivi": "Prithivi a·axis-o dongtokenga, ge·sa sani gisik ra·enggipa.",
        "porgido": "Prithivi a·axis-o dongtokenga, ge·sa sani gisik ra·enggipa.",
        "salrang": "Salrang gas aro wal·a gital dingtang ong·a, nuclear fusion-ni a·sel jekchaka.",
        "jawal": "Jawal Prithivi-ni satellite ong·a, sal-ni jekgipa-ko reflect ka·a.",
        "black hole": "Black hole gravity gita ong·a, jekgipa wa·al chakatna man·ja.",
        "vir": "Prithivi a·axis-o dongtokenga.",
        "star": "Salrang gas aro wal·a gital ong·a."
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
        "pyrthei": "Ka pyrthei ka iaid shaphang la ka axis, shisien ha ka sngi.",
        "gravity": "Ka gravity ka dei ka bor ba ring jingiasyllok.",
        "khlor": "U khlor u dei u gas ba heh ha bneng, u shat da ka fusion.",
        "bnai": "U bnai u dei u satellite jong ka pyrthei.",
        "black hole": "U black hole u dei ka gravity kaba khraw."
    },
    "Kokborok": {
        "ha": "Ha a axis-o wngwi tonggo, salnisa kaisa tongwi.",
        "gravity": "Gravity bono nokhorokno buthuknani bisingo.",
        "atal": "Atal gas aro hor gwnang tonggo, fusion bai kwrwi tonggo.",
        "tal": "Tal bono ha-ni satellite.",
        "black hole": "Black hole gravity gwnang tonggo."
    },
    "English": {
        "earth": "Earth rotates on its axis once in 24 hours due to gravity.",
        "gravity": "Gravity is the force that pulls objects towards Earth.",
        "star": "A star is a giant ball of gas shining due to nuclear fusion.",
        "moon": "Moon is Earth's satellite, it reflects sunlight.",
        "black hole": "A black hole is extreme gravity where even light cannot escape."
    },
    "Hindi": {
        "prithvi": "Prithvi apni dhuri par 24 ghante me ek baar ghoomti hai, gravity ke karan.",
        "gravity": "Gravity wo shakti hai jo cheezo ko Prithvi ki taraf kheenchti hai, Newton ne khoja.",
        "tara": "Tara gas ka bada gola hai jo nuclear fusion se chamakta hai.",
        "chand": "Chand Prithvi ka satellite hai, suraj ki roshni reflect karta hai.",
        "black hole": "Black hole bahut tez gravity hai, roshni bhi bahar nahi aa sakti."
    },
    "Assamese": {
        "prithvi": "Prithvi nijor axisot 24 ghontat ekbar ghure, gravityr karone.",
        "gravity": "Gravity bostu bur Prithivi loi tana shakti hoi, Newton e aabiskar korise.",
        "tora": "Tora gasor dangor gola hoi, nuclear fusionor babe jilike.",
        "jun": "Jun Prithvir satellite hoi, belire pohar reflect kore.",
        "black hole": "Black hole otit koboi gravity hoi, poharo olabo nuware."
    },
    "Bengali": {
        "prithvi": "Prithvi nijer okkher upor 24 ghontay ekbar ghore, gravityr karone.",
        "gravity": "Gravity holo sei shakti ja bostu ke Prithibir dike tane, Newton abishkar korechen.",
        "tara": "Tara gaser boro gola, nuclear fusione jole.",
        "chand": "Chand Prithvir satellite, surjer alo reflect kore.",
        "black hole": "Black hole prochondo gravity, alo berote pare na."
    },
    "Nagamese": {
        "prithvi": "Prithivi nijor axis te 24 ghonta te ekbar ghure, gravity karone.",
        "gravity": "Gravity to bostu ke niche tanibo laga shakti ase, Newton pora dikhise.",
        "tara": "Tara gas laga dangor gola ase, fusion pora jole.",
        "jun": "Jun Prithvi laga satellite ase, suraj laga light reflect kore.",
        "black hole": "Black hole to besi gravity ase, light bhi bahar ahibo nware."
    },
    "Nepali": {
        "prithvi": "Prithvi afno akshama 24 ghanta ma ek patak ghumchha, gravity le garda.",
        "gravity": "Gravity le bosta haru lai Prithvi tira tanchha, Newton le patta lagaye.",
        "tara": "Tara gas ko thulo gola ho, nuclear fusion le chamkinchha.",
        "jun": "Jun Prithvi ko satellite ho, surya ko prakash reflect garchha.",
        "black hole": "Black hole dherai thulo gravity ho, prakash pani bahira auna sakdaina."
    }
}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to Northeast AI by Samewan! 🏔️🔬"}]

st.title("🏔️ Northeast AI")
st.markdown("**🌟 Meghalaya's First 10-Language Scientific Voice AI by Samewan**")

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

def is_loop(text):
    if not text: return True
    t = text.lower()
    if t.count("a·kha") >= 3: return True
    if t.count("a·bong·a") >= 3: return True
    if t.count("a·beng·a") >= 3: return True
    if t.count("daka·deng") >= 3: return True
    words = t.split()
    if len(words) > 12 and len(set(words)) < 6: return True
    return False

def remove_loop_and_fix(text):
    if not text or len(text.strip()) < 5: return ""
    if is_loop(text): return ""
    parts = [p.strip() for p in text.split('.') if p.strip()]
    seen=set(); out=[]
    for p in parts:
        low=p.lower()
        if low not in seen and len(p) > 3:
            seen.add(low); out.append(p)
        if len(out) >= 2: break
    fixed=". ".join(out)
    fixed=re.sub(r'\s+',' ',fixed).strip()
    if fixed and not fixed.endswith('.'): fixed+='.'
    return fixed[:400] if fixed else ""

def get_reply(text, language):
    low = text.lower()
    # === IDENTITY FIX - SAB LANGUAGE ROMAN ME ===
    if any(x in low for x in ["kaun bana", "kisne bana", "kisne banaya", "who made you", "who created you", "tumhe kisne", "aapko kisne", "tujhe kaun"]):
        identity = {
            "Garo": "Anga-ko Samewan, Meghalaya-ni Northeast AI ong·a.",
            "Mizo": "Samewan, Meghalaya atanga min siam a, Northeast AI ka ni.",
            "Khasi": "Ma nga u Samewan na Meghalaya, nga u Northeast AI.",
            "Hindi": "Mujhe Samewan ne banaya hai, main Meghalaya ka Northeast AI hoon.",
            "Assamese": "Mok Samewan e banise, moi Meghalaya r Northeast AI hoi.",
            "Bengali": "Amake Samewan baniyeche, ami Meghalaya r Northeast AI.",
            "Nagamese": "Moi ke Samewan pora banaise, moi Meghalaya laga Northeast AI ase.",
            "Nepali": "Malai Samewan le banayeko ho, ma Meghalaya ko Northeast AI ho.",
            "Kokborok": "Bono Samewan bai tongphano, bono Northeast AI tonggo.",
            "English": "I am Northeast AI made by Samewan from Meghalaya."
        }
        return identity.get(language, identity["English"])

    api_key=get_api_key()
    if not api_key.startswith("gsk_"): return "API Key Error! Secrets check karo."
    try:
        client=Groq(api_key=api_key)
        
        # === SAB LANGUAGE KO ROMAN ME FORCE KARNA ===
        if language == "Garo":
            sys_prompt = "You are Northeast AI made by Samewan from Meghalaya. You are Garo science teacher. Answer ONLY in Garo ROMAN letters (English alphabet). Never use native script. 2 short sentences. Don't repeat a·kha."
        elif language == "Mizo":
            sys_prompt = "You are Northeast AI made by Samewan. Mizo teacher. Answer ONLY in Mizo ROMAN (English letters). 2 short sentences."
        elif language == "Khasi":
            sys_prompt = "You are Northeast AI made by Samewan. Khasi teacher. Answer ONLY in Khasi ROMAN (English letters). 2 short sentences."
        elif language == "Hindi":
            sys_prompt = "You are Northeast AI made by Samewan. Hindi science teacher. Answer ONLY in Hindi ROMAN (English letters, like 'Prithvi apni dhuri par ghoomti hai'), NEVER Devanagari. 2 short sentences."
        elif language == "Assamese":
            sys_prompt = "You are Northeast AI made by Samewan. Assamese teacher. Answer ONLY in Assamese ROMAN (English letters, like 'Prithvi nijor axisot ghure'), NEVER Assamese script. 2 short sentences."
        elif language == "Bengali":
            sys_prompt = "You are Northeast AI made by Samewan. Bengali teacher. Answer ONLY in Bengali ROMAN (English letters, like 'Prithvi nijer okkher upor ghore'), NEVER Bengali script. 2 short sentences."
        elif language == "Nagamese":
            sys_prompt = "You are Northeast AI made by Samewan. Nagamese teacher. Answer ONLY in Nagamese ROMAN (English letters). 2 short sentences."
        elif language == "Nepali":
            sys_prompt = "You are Northeast AI made by Samewan. Nepali teacher. Answer ONLY in Nepali ROMAN (English letters, like 'Prithvi afno akshama ghumchha'), NEVER Devanagari. 2 short sentences."
        elif language == "Kokborok":
            sys_prompt = "You are Northeast AI made by Samewan. Kokborok teacher. Answer ONLY in Kokborok ROMAN (English letters). 2 short sentences."
        else:
            sys_prompt = f"You are Northeast AI made by Samewan from Meghalaya. You are {language} science teacher. Answer ONLY in {language} ROMAN English letters, 2 short sentences."

        history=[{"role": "system", "content": sys_prompt}]
        for m in st.session_state.messages[-3:]:
            history.append({"role": m["role"], "content": m["content"]})
        history.append({"role": "user", "content": text})

        for model_name in ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
            try:
                comp=client.chat.completions.create(messages=history, model=model_name, max_tokens=300, temperature=0.6)
                content=comp.choices[0].message.content.strip()
                if not content or len(content) < 10: continue
                if is_loop(content): continue
                if "Khawvel chu" in content and language == "Garo": continue
                if "kritrim neural" in content.lower(): continue
                if "artificial neural" in content.lower(): continue
                cleaned=remove_loop_and_fix(content)
                if cleaned and len(cleaned) > 10:
                    return cleaned
            except: continue

        # Fallback - SAB ROMAN
        if language in FALLBACK_ALL:
            for k,v in FALLBACK_ALL[language].items():
                if k in low:
                    return v
        for k,v in FALLBACK_ALL["English"].items():
            if k in low:
                return v

        defaults = {
            "Garo": "Ia bostu science-ni bidingo ong·a, natural process-ni a·sel.",
            "Hindi": "Ye ek vaigyanik ghatna hai jo prakritik prakriya se hoti hai.",
            "Assamese": "Eitu ek scientific ghatana hoi, prakritik prakriyar karone hoi.",
            "Bengali": "Eta ek bigganik ghatona, prakritik prokriyar karone hoy.",
            "English": "This is a scientific phenomenon due to natural processes."
        }
        return defaults.get(language, defaults["English"])

    except:
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
