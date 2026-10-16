import streamlit as st
from gtts import gTTS
import io, os
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

# FIRST TEXT - GARO + MIZO MIX NA HO, HAR BHASA KE LIYE ALAG
def get_welcome_text(lang):
    greets = {
        "Garo": "Mitela! Meghalaya a·songni Northeast AI-na welcome! 🏔️ Anga Northeast ni gita 10-language voice AI! Nangni kusik gita bhasa se·na aro aganbo!",
        "Mizo": "Chibai! Meghalaya atanga Northeast AI-ah kan lo lawm a che! 🏔️ Kei Northeast hmasa ber 10-language voice AI ka ni!",
        "Khasi": "Khublei! Welcome to our AI from Meghalaya! 🏔️ Nga dei Northeast ka AI ba nyngkong eh ba 10 tylli ki ktien!",
        "Kokborok": "Hamjakma! Meghalaya ni Northeast AI-o welcome! 🏔️ Ang Northeast ni 10-language voice AI!",
    }
    return greets.get(lang, "Welcome to our AI from Meghalaya! 🏔️ Main Northeast ka pehla 10-language voice AI hu. Apni bhasa chuno aur bolo!")

if "messages" not in st.session_state:
    st.session_state.messages=[{"role":"assistant","content": get_welcome_text("Garo")}]

st.title("🏔️ Northeast AI")
st.markdown("""
**🌟 Meghalaya's First 10-Language Voice AI | Northeast India**
🎙️ **Bolke puchho, sunke samjho** - Apni bhasa me baat karo!
💬 Garo | Khasi | Mizo | Kokborok | Assamese | Bengali | Hindi | English | Nagamese | Nepali
""")
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
    return k.strip()

def get_reply(text, language):
    low=text.lower()
    # ALL 10 LANGUAGE CREATOR KEYWORDS - FIXED
    creator_keywords = [
        "who made you","kisne banaya","tumhe kisne","creator","banaya kisne","who created","kaun bana","kon banaya","kisne bnaya","tumko kaun","tujhe kisne","tumhe kaun","tum ko kaun","bana ia","kaun banaya",
        "nangni biming","nang biming","biming ra","bimung ra","bimung","chusokna","na·a chusokna","angko chusokna",
        "i hming eng nge","eng nge i hming","tuin siam","tu nge siam","min siam","nang siam","i hming","hming eng",
        "ka kyrteng","ei kyrteng","phi kyrteng","who created you","ka kyrteng eh","boh kyrteng",
        "nini mung","mung borok","sa kha","mung uan",
        "your name","tera naam","tumhara naam","apka naam","tumar nam"
    ]

    if any(k in low for k in creator_keywords):
        CREATOR_REPLIES = {
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
        return CREATOR_REPLIES.get(language, f"Mujhe banaya hai {CREATOR_NAME} ne, {CREATOR_PLACE} se! 🏔️")

    # MIZORAM FAMOUS QUESTION - DIRECT ANSWER TO AVOID LOOP
    if "mizoram hi eng nge lar" in low or ("mizoram" in low and "lar" in low):
        return "Chibai! Mizoram is famous for Aizawl city, blue mountains (Mizo Hills), Chapchar Kut festival, bamboo dance (Cheraw), and beautiful churches! Very peaceful state! 🏔️"
    if "garo hills" in low or "meghalaya" in low and "famous" in low:
        return f"{LANGUAGES[language]}! Meghalaya is famous for Cherrapunji, living root bridges, Dawki river, Shillong hills and Garo, Khasi culture! 🏔️"

    api_key=get_api_key()
    if GROQ_AVAILABLE and api_key:
        try:
            client=Groq(api_key=api_key)
            # TRIBAL LANGUAGE = QWEN MODEL (NO LOOP) - MAIN FIX
            if language in ["Mizo", "Garo", "Khasi", "Kokborok", "Nagamese"]:
                model_to_use = "qwen/qwen3-32b"
                prompt = f"You are Northeast AI from Meghalaya created by {CREATOR_NAME}. User language is {language}. User says: {text}. Reply in simple {language} + English mix, max 3-4 lines, clear, no repeating same word more than twice. If {language} is hard, reply mostly in simple English. Never say OpenAI. Never repeat 'chhuak a chhuak' or 'a hmu a ni'."
            else:
                model_to_use = "openai/gpt-oss-20b"
                prompt = f"You are Northeast AI from Meghalaya. Never say OpenAI. Reply in Roman {language} only A-Z. Language={language}. User: {text}. Max 4 lines."

            comp=client.chat.completions.create(
                messages=[
                    {"role":"system","content":f"You are Northeast AI from Meghalaya. Made by {CREATOR_NAME}. Reply in Roman only, no loops, no OpenAI, no repeat words."},
                    {"role":"user","content":prompt}
                ],
                model=model_to_use,
                max_tokens=700,
                temperature=0.7
            )
            content = comp.choices[0].message.content
            if content and content.strip():
                # LOOP DETECTION - AGAR LOOP KARE TO FALLBACK
                lower_c = content.lower()
                if lower_c.count("chhuak") > 3 or lower_c.count("a hmu a ni") > 1 or "chhuak a, a chhuak" in lower_c:
                    if language == "Mizo":
                        return "Chibai! Mizoram is famous for hills, festivals and culture! Aizawl is capital! 🏔️"
                    else:
                        return f"{LANGUAGES[language]}! Mizoram/Garo Hills is very beautiful with hills and culture! 🏔️"
                if "openai" in lower_c:
                    return f"{LANGUAGES[language]}! Bolo kya help chahiye? 🏔️"
                return content
            else:
                raise Exception("Empty")
        except Exception as e:
            try:
                comp=client.chat.com
