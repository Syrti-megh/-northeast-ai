import streamlit as st
from gtts import gTTS
import io
try:
    from groq import Groq
    GROQ_AVAILABLE=True
except:
    GROQ_AVAILABLE=False

st.set_page_config(page_title="Northeast AI - Meghalaya", page_icon="🏔️", layout="centered")

CREATOR_NAME="Samewan"
CREATOR_PLACE="Meghalaya"

LANGUAGES = {
    "Garo": "Mitela", "Khasi": "Khublei", "Mizo": "Chibai",
    "Kokborok": "Hamjakma", "Assamese": "Nomoskar", "Bengali": "Nomoskar",
    "Hindi": "Namaste", "English": "Hello", "Nagamese": "Hello", "Nepali": "Namaste"
}

def get_welcome_text(lang):
    greets = {
        "Garo": "Mitela! Meghalaya a·songni Northeast AI-na welcome! 🏔️ Anga 10-language voice AI!",
        "Mizo": "Chibai! Meghalaya atanga Northeast AI-ah kan lo lawm a che! 🏔️ Kei 10-language voice AI ka ni!",
        "Khasi": "Khublei! Welcome from Meghalaya Northeast AI! 🏔️ Nga dei 10-language voice AI!",
        "Kokborok": "Hamjakma! Meghalaya ni Northeast AI-o welcome! 🏔️",
    }
    return greets.get(lang, "Welcome to our AI from Meghalaya! 🏔️ Main Northeast ka pehla 10-language voice AI hu!")

if "messages" not in st.session_state:
    st.session_state.messages=[{"role":"assistant","content": get_welcome_text("Garo")}]

st.title("🏔️ Northeast AI")
st.markdown("**🌟 Meghalaya's First 10-Language Voice AI**\n🎙️ Garo | Khasi | Mizo | Kokborok | Assamese | Bengali | Hindi | English | Nagamese | Nepali")
st.info("👇 Bhasa chuno, phir Type karo ya 🎤 Mic se Bolo!")

col1, col2 = st.columns([2,1])
with col1:
    lang = st.selectbox("🌐 Language Chuno:", list(LANGUAGES.keys()), index=0)
with col2:
    if st.button("🗑️ Clear"):
        st.session_state.messages=[{"role":"assistant","content": get_welcome_text(lang)}]
        st.rerun()

def get_api_key():
    k = st.secrets.get("GROQ_API_KEY","") if hasattr(st, 'secrets') else ""
    return k.strip() if k else ""

def get_reply(text, language):
    low = text.lower().strip()

    # 1. QUICK DICTIONARY - Sorted longest first to avoid overlap
    quick = {
        "muttui mangtha": {"Mizo": "Muttui! Mangtha le! Naktukah kan in hmu leh dawn nia! 😴"},
        "mizoram hi eng nge lar": {"Mizo": "Chibai! Mizoram is famous for Aizawl city, blue mountains, Chapchar Kut, Cheraw dance, peaceful churches! 🏔️"},
        "mizoram economy": {"Mizo": "Chibai! Mizoram economy chu agriculture, bamboo, handloom ah a innghat! Jhum cultivation a lar e! 🏔️"},
        "eng nge chanchin": {"Mizo": "Chanchin tha! Ka lawm e! Nang eng nge i chanchin? Chibai! 🏔️"},
        "hla i thiam": {"Mizo": "Chibai! Aw, Mizo hla ka thiam ve e! Chhawrpial Run leh Lengdang Phai ka hre ve! Nang i thiam em? 🎵🏔️"},
        "ka lawm e": {"Mizo": "Keipawh ka lawm e! Chibai! Chanchin tha e! 😊🏔️"},
        "ngaihtuah": {"Mizo": "Chibai! Ka ngaihtuah chu nangmah! Eng nge ka pui theih che? I tan ka awm e! 😊🏔️"},
        "thiam em": {"Mizo": "Chibai! Ka thiam e! Mizo tawng ka thiam ve tawh! Eng zawhna nge i neih? 🏔️"},
        "i dam em": {"Mizo": "Chibai! Ka dam e! Nang i dam em? Chanchin tha maw? 🏔️"},
        "muttui": {"Mizo": "Muttui! I mu tui dawn nia! 😴✨"},
        "chibai": {"Mizo": "Chibai! Eng nge chanchin? Ka tha e! Nang? 🏔️"},
        "mitela": {"Garo": "Mitela! Maikai? Anga tha! Nang? 😊🏔️"},
        "khublei": {"Khasi": "Khublei! Kumno long? Nga bha! 😊🏔️"},
        "hamjakma": {"Kokborok": "Hamjakma! Nung tamo? Ang hamjak! 😊🏔️"},
    }

    # Check longest keys first
    for key in sorted(quick.keys(), key=len, reverse=True):
        if key in low:
            if language in quick[key]:
                return quick[key][language]
            if language == "Mizo" and "Mizo" in quick[key]:
                return quick[key]["Mizo"]

    # 2. Creator
    creator_keywords = ["who made you","kisne banaya","creator","i hming eng nge","eng nge i hming","tuin siam","your name"]
    if any(k in low for k in creator_keywords):
        return f"Chibai! Kei Northeast AI ka ni! Min siamtu chu {CREATOR_NAME} a ni, {CREATOR_PLACE} atangin! 🏔️"

    # 3. Groq API
    api_key = get_api_key()
    if GROQ_AVAILABLE and api_key:
        try:
            client = Groq(api_key=api_key)
            model_to_use = "qwen/qwen3-32b"
            comp = client.chat.completions.create(
                messages=[
                    {"role":"system","content": f"You are Northeast AI made by {CREATOR_NAME} from {CREATOR_PLACE}. You MUST reply in {language} only, Roman letters. No English if language is Mizo. Max 3 lines."},
                    {"role":"user","content": f"Reply in {language}: {text}"}
                ],
                model=model_to_use, max_tokens=500, temperature=0.6
            )
            content = comp.choices[0].message.content
            if content and content.strip():
                if "openai" in content.lower():
                    content = content.replace("OpenAI", CREATOR_NAME)
                return content
        except:
            pass

    # 4. FINAL FALLBACK - PURE MIZO, NO "You said" EVER
    if language == "Mizo":
        return "Chibai! Ka ngaihtuah chu nangmah! Eng nge ka pui theih che? I tan ka awm e! 😊🏔️"
    if language == "Garo":
        return f"Mitela! Anga Northeast AI! Angko {CREATOR_NAME} ne {CREATOR_PLACE} ni a·song se chon·a! 🏔️"
    if language == "Khasi":
        return f"Khublei! Nga dei Northeast AI! Ia shna da {CREATOR_NAME} na {CREATOR_PLACE}! 🏔️"
    if language == "Kokborok":
        return f"Hamjakma! Ang Northeast AI! Ano {CREATOR_NAME} {CREATOR_PLACE} ni! 🏔️"
    return f"{LANGUAGES.get(language,'Hello')}! I am Northeast AI made by {CREATOR_NAME} from {CREATOR_PLACE}! 🏔️"

def transcribe_voice(audio_file):
    api_key=get_api_key()
    if GROQ_AVAILABLE and api_key and audio_file:
        try:
            client=Groq(api_key=api_key)
            tr=client.audio.transcriptions.create(file=("voice.wav", audio_file.getvalue()), model="whisper-large-v3")
            return tr.text
        except:
            return None
    return None

def speak_clear(text):
    try:
        tts=gTTS(text=text[:400], lang='en', tld='co.in', slow=False)
        fp=io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except:
        try:
            tts=gTTS(text=text[:400], lang='en', slow=False)
            fp=io.BytesIO()
            tts.write_to_fp(fp)
            return fp.getvalue()
        except:
            return None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"]=="assistant" and msg["content"].strip():
            audio = speak_clear(msg["content"])
            if audio:
                st.audio(audio, format="audio/mp3")

st.divider()
st.markdown(f"**{LANGUAGES[lang]}! Type karo ya Mic dabao**")
voice_input = st.audio_input(f"🎤 {lang} me Bolo")
user_text = None
if voice_input:
    with st.spinner("Sun raha hu..."):
        transcribed = transcribe_voice(voice_input)
        if transcribed:
            user_text = transcribed
            st.success(f"🎤 Suna: {transcribed}")
        else:
            user_text = f"Voice message in {lang}"

text_input = st.chat_input(f"{LANGUAGES[lang]}! Yahan likho...")
if text_input:
    user_text = text_input

if user_text:
    st.session_state.messages.append({"role":"user","content":user_text})
    with st.chat_message("user"):
        st.write(user_text)
    reply=get_reply(user_text, lang)
    st.session_state.messages.append({"role":"assistant","content":reply})
    with st.chat_message("assistant"):
        st.write(reply)
        audio = speak_clear(reply)
        if audio:
            st.audio(audio, format="audio/mp3", autoplay=True)
