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
    # Auto-detect
    is_mizo = any(w in low for w in ["ngaihtuah","i dam em","chibai","ka lawm","muttui","thiam em","chanchin","hla","khawiah","nge lar"])
    is_hindi = any(w in low for w in ["kabre","batao","kaun hai","kya hai","bare me"])

    # === 1. KNOWLEDGE BASE - SHILLONG (MUST BE FIRST) ===
    if "shillong" in low:
        if language == "Hindi" or is_hindi or "kabre" in low or "batao" in low:
            return "Namaste! Shillong Meghalaya ki capital hai! Ise Scotland of the East kehte hain! Umiam Lake, Elephant Falls, Police Bazar, Laitlum Canyon yahan famous hai! Bahut khoobsurat hill station! 🏔️"
        return "Hello! Shillong is the capital of Meghalaya! Called Scotland of the East! Famous for Umiam Lake, Elephant Falls, Police Bazar, Laitlum Canyon! Beautiful hill station! 🏔️"
    if "cherrapunji" in low or "sohra" in low:
        return "Hello! Cherrapunji (Sohra) is famous for heavy rainfall! Living root bridges and Nohkalikai Falls are here! In Meghalaya! 🏔️"
    if "aizawl" in low:
        return "Chibai! Aizawl chu Mizoram capital a ni! Tlang chungah a awm! Mizo culture lar! 🏔️"

    # === 2. QUICK DICTIONARY ===
    quick = {
        "muttui mangtha": "Muttui! Mangtha le! Naktukah kan in hmu leh dawn nia! 😴",
        "mizoram hi eng nge lar": "Chibai! Mizoram is famous for Aizawl city, blue mountains, Chapchar Kut, Cheraw dance, peaceful churches! 🏔️",
        "mizoram economy": "Chibai! Mizoram economy chu agriculture, bamboo, handloom ah a innghat! Jhum cultivation a lar e! 🏔️",
        "eng nge chanchin": "Chanchin tha! Ka lawm e! Nang eng nge i chanchin? Chibai! 🏔️",
        "hla i thiam": "Chibai! Aw, Mizo hla ka thiam ve e! Chhawrpial Run leh Lengdang Phai ka hre ve! Nang i thiam em? 🎵🏔️",
        "ka lawm e": "Keipawh ka lawm e! Chibai! Chanchin tha e! 😊🏔️",
        "ngaihtuah": "Chibai! Ka ngaihtuah chu nangmah! Eng nge ka pui theih che? I tan ka awm e! 😊🏔️",
        "thiam em": "Chibai! Ka thiam e! Mizo tawng ka thiam ve tawh! Eng zawhna nge i neih? 🏔️",
        "i dam em": "Chibai! Ka dam e! Nang i dam em? Chanchin tha maw? 🏔️",
        "muttui": "Muttui! I mu tui dawn nia! 😴✨",
        "chibai": "Chibai! Eng nge chanchin? Ka tha e! Nang? 🏔️",
    }
    for key in sorted(quick.keys(), key=len, reverse=True):
        if key in low:
            return quick[key]

    if "mitela" in low: return "Mitela! Maikai? Anga tha! Nang? 😊🏔️"
    if "khublei" in low: return "Khublei! Kumno long? Nga bha! 😊🏔️"
    if "hamjakma" in low: return "Hamjakma! Nung tamo? Ang hamjak! 😊🏔️"

    # === 3. CREATOR - 100% FIXED FOR OWNER QUESTION ===
    creator_keywords = [
        "who made you","kisne banaya","who created you","creator kaun",
        "tuin siam che","i hming eng nge","who is your creator",
        "owner kaun","tera owner","ter owner","malik kaun","owner kaun hai",
        "kisne banaya tumhe","tumhe kisne banaya","who is your owner",
        "tumhara malik kaun","tumhara owner"
    ]
    if any(k in low for k in creator_keywords):
        if is_mizo or language == "Mizo":
            return f"Chibai! Kei Northeast AI ka ni! Min siamtu chu {CREATOR_NAME} a ni, {CREATOR_PLACE} atangin! 🏔️"
        if language == "Hindi" or is_hindi:
            return f"Namaste! Main Northeast AI hu! Mujhe {CREATOR_NAME} ne {CREATOR_PLACE} se banaya hai! 🏔️"
        return f"Hello! I am Northeast AI! Created by {CREATOR_NAME} from {CREATOR_PLACE}! 🏔️"

    # === 4. GROQ API ===
    api_key = get_api_key()
    if GROQ_AVAILABLE and api_key:
        try:
            client = Groq(api_key=api_key)
            target_lang = "Mizo" if is_mizo else ("Hindi" if is_hindi else language)
            comp = client.chat.completions.create(
                messages=[
                    {"role":"system","content": f"You are Northeast AI made by {CREATOR_NAME} from {CREATOR_PLACE}. You MUST reply in {target_lang} only, Roman letters. Max 3 lines. If asked about Shillong, tell about capital, Scotland of East, Umiam Lake."},
                    {"role":"user","content": f"Reply in {target_lang}: {text}"}
                ],
                model="qwen/qwen3-32b", max_tokens=500, temperature=0.6
            )
            content = comp.choices[0].message.content
            if content and content.strip():
                return content.replace("OpenAI", CREATOR_NAME)
        except:
            pass

    # === 5. SMART FALLBACK ===
    if is_mizo:
        return "Chibai! Ka ngaihtuah chu nangmah! Eng nge ka pui theih che? I tan ka awm e! 😊🏔️"
    if language == "Hindi" or is_hindi:
        return f"Namaste! '{text}' ke baare me - Northeast bahut khoobsurat hai! Shillong, Meghalaya ke baare me pucho! 🏔️"
    return f"Hello! About '{text}' - Northeast is beautiful! Ask me about Shillong, Meghalaya, Mizoram! 🏔️"

def transcribe_voice(audio_file):
    api_key=get_api_key()
    if GROQ_AVAILABLE and api_key and audio_file:
        try:
            client=Groq(api_key=api_key)
            tr=client.audio.transcriptions.create(file=("voice.wav", audio_file.getvalue()), model="whisper-large-v3")
            return tr.text
        except: return None
    return None

def speak_clear(text):
    try:
        tts=gTTS(text=text[:400], lang='en', tld='co.in', slow=False)
        fp=io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()
    except:
        try:
            tts=gTTS(text=text[:400], lang='en', slow=False)
            fp=io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()
        except: return None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"]=="assistant" and msg["content"].strip():
            audio = speak_clear(msg["content"])
            if audio: st.audio(audio, format="audio/mp3")

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
if text_input: user_text = text_input
if user_text:
    st.session_state.messages.append({"role":"user","content":user_text})
    with st.chat_message("user"): st.write(user_text)
    reply=get_reply(user_text, lang)
    st.session_state.messages.append({"role":"assistant","content":reply})
    with st.chat_message("assistant"):
        st.write(reply)
        audio = speak_clear(reply)
        if audio: st.audio(audio, format="audio/mp3", autoplay=True)
