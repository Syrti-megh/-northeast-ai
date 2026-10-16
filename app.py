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
    low=text.lower()
    creator_keywords = ["who made you","kisne banaya","creator","who created","nangni biming","nang biming","biming ra","bimung","i hming eng nge","eng nge i hming","tuin siam","ka kyrteng","nini mung","your name","tera naam","bana ia"]

    if any(k in low for k in creator_keywords):
        replies = {
            "Garo": f"Mitela! Anga Northeast AI! Angko {CREATOR_NAME} ne {CREATOR_PLACE} ni a·song se chon·a! 🏔️",
            "Mizo": f"Chibai! Kei Northeast AI ka ni! Min siamtu chu {CREATOR_NAME} a ni, {CREATOR_PLACE} atangin! 🏔️",
            "Khasi": f"Khublei! Nga dei Northeast AI! Ia shna da {CREATOR_NAME} na {CREATOR_PLACE}! 🏔️",
            "Kokborok": f"Hamjakma! Ang Northeast AI! Ano {CREATOR_NAME} {CREATOR_PLACE} ni! 🏔️",
            "Assamese": f"Nomoskar! Moi Northeast AI! Muk {CREATOR_NAME} e {CREATOR_PLACE} r pora banaisa! 🏔️",
            "Bengali": f"Nomoskar! Ami Northeast AI! Amake {CREATOR_NAME} {CREATOR_PLACE} theke baniyeche! 🏔️",
            "Hindi": f"Namaste! Main Northeast AI hu! Mujhe {CREATOR_NAME} ne {CREATOR_PLACE} se banaya hai! 🏔️",
            "English": f"Hello! I am Northeast AI! I was created by {CREATOR_NAME} from {CREATOR_PLACE}! 🏔️",
            "Nagamese": f"Hello! Moi Northeast AI! Moi ke {CREATOR_NAME} {CREATOR_PLACE} para bonaise! 🏔️",
            "Nepali": f"Namaste! Ma Northeast AI hu! Malai {CREATOR_NAME} le {CREATOR_PLACE} bata banayeko ho! 🏔️"
        }
        return replies.get(language, f"Mujhe {CREATOR_NAME} ne {CREATOR_PLACE} se banaya hai! 🏔️")

    if "mizoram hi eng nge lar" in low or ("mizoram" in low and "lar" in low):
        return "Chibai! Mizoram is famous for Aizawl city, blue mountains, Chapchar Kut festival, bamboo dance Cheraw, and beautiful churches! Very peaceful state! 🏔️"

    api_key=get_api_key()
    if GROQ_AVAILABLE and api_key:
        client=Groq(api_key=api_key)
        try:
            if language in ["Mizo", "Garo", "Khasi", "Kokborok", "Nagamese"]:
                model_to_use = "qwen/qwen3-32b"
                prompt = f"You are Northeast AI from Meghalaya made by {CREATOR_NAME}. User language {language}. User says: {text}. Reply in simple {language}+English mix, max 4 lines, clear, no repeating same word. Never say OpenAI."
            else:
                model_to_use = "openai/gpt-oss-20b"
                prompt = f"You are Northeast AI from Meghalaya. Never say OpenAI. Reply Roman {language} only. User: {text}. Max 4 lines."

            comp=client.chat.completions.create(
                messages=[
                    {"role":"system","content":f"You are Northeast AI. Made by {CREATOR_NAME}. No loop, no OpenAI."},
                    {"role":"user","content":prompt}
                ],
                model=model_to_use,
                max_tokens=600,
                temperature=0.7
            )
            content = comp.choices[0].message.content
            if content and content.strip():
                if "openai" in content.lower():
                    return f"{LANGUAGES[language]}! Bolo kya help chahiye? 🏔️"
                if content.lower().count("chhuak") > 3:
                    return "Chibai! Mizoram is famous for hills and festivals! Aizawl is capital! 🏔️"
                return content
        except Exception as e:
            try:
                comp2=client.chat.completions.create(
                    messages=[{"role":"user","content":f"Reply simple Roman English for: {text}"}],
                    model="qwen/qwen3-32b",
                    max_tokens=400
                )
                if comp2.choices[0].message.content:
                    return comp2.choices[0].message.content
            except:
                pass
            return f"{LANGUAGES[language]}! Bolo kya puchna hai? 🏔️"

    return f"{LANGUAGES[language]}! You said: {text} in {language}."

def transcribe_voice(audio_file):
    api_key=get_api_key()
    if GROQ_AVAILABLE and api_key and audio_file:
        try:
            client=Groq(api_key=api_key)
            tr=client.audio.transcriptions.create(
                file=("voice.wav", audio_file.getvalue()),
                model="whisper-large-v3"
            )
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
