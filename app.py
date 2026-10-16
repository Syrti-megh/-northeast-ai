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

# ===== FINAL FIXED VERSION - ALL HARD MIZO WORKS =====
def get_reply(text, language):
    low=text.lower().strip()

    # 1. QUICK DICTIONARY - Easy + 2 hard ones added
    quick = {
        "muttui mangtha": {"Mizo": "Muttui! Mangtha le! Naktukah kan in hmu leh dawn nia! 😴"},
        "muttui": {"Mizo": "Muttui! I mu tui dawn nia! 😴✨"},
        "ka lawm e": {"Mizo": "Keipawh ka lawm e! Chibai! Chanchin tha e! 😊🏔️"},
        "eng nge chanchin": {"Mizo": "Chanchin tha! Ka lawm e! Nang eng nge i chanchin? Chibai! 🏔️"},
        "chibai": {"Mizo": "Chibai! Eng nge chanchin? Ka tha e! Nang? 🏔️"},
        "mitela": {"Garo": "Mitela! Maikai? Anga tha! Nang? 😊🏔️"},
        "khublei": {"Khasi": "Khublei! Kumno long? Nga bha! 😊🏔️"},
        "hamjakma": {"Kokborok": "Hamjakma! Nung tamo? Ang hamjak! 😊🏔️"},
        "what's up": {
            "Mizo": "Chibai! Eng nge chanchin? Ka tha e! 🏔️", "Garo": "Mitela! Maikai? Anga tha! 🏔️",
            "Khasi": "Khublei! Kumno long? Nga bha! 🏔️", "Kokborok": "Hamjakma! Nung tamo? Ang ham! 🏔️",
            "Assamese": "Nomoskar! Ki khobor? Moi bhal! 🏔️", "Bengali": "Nomoskar! Ki khobor? Bhalo! 🏔️",
            "Hindi": "Namaste! Kya haal hai? Mast! 🏔️", "English": "Hello! What's up? I'm good! 🏔️",
            "Nagamese": "Hello! Ki khobor? Bhal ase! 🏔️", "Nepali": "Namaste! K cha? Ma thik chu! 🏔️"
        },
        "mizoram hi eng nge lar": {"Mizo": "Chibai! Mizoram is famous for Aizawl city, blue mountains, Chapchar Kut, Cheraw dance, peaceful churches! 🏔️"},
        # --- NEW HARD ONES ADDED ---
        "hla i thiam": {"Mizo": "Chibai! Aw, Mizo hla ka thiam ve e! 'Chhawrpial Run' leh Lengdang Phai ka hre ve! Nang i thiam em? 🎵🏔️"},
        "ngaihtuah": {"Mizo": "Chibai! Ka ngaihtuah chu nangmah! Eng nge ka pui theih che? I tan ka awm e! 😊🏔️"},
        "thiam em": {"Mizo": "Chibai! Ka thiam e! Mizo tawng ka thiam ve tawh! Eng zawhna nge i neih? 🏔️"},
        "i dam em": {"Mizo": "Chibai! Ka dam e! Nang i dam em? Chanchin tha maw? 🏔️"},
        "mizoram economy": {"Mizo": "Chibai! Mizoram economy chu agriculture, bamboo, handloom ah a innghat! Jhum cultivation a lar e! 🏔️"},
    }

    for key in quick:
        if key in low:
            if language in quick[key]:
                return quick[key][language]
            # if language not in dict, return Mizo one for Mizo lang
            if language == "Mizo" and "Mizo" in quick[key]:
                return quick[key]["Mizo"]

    # 2. Creator
    creator_keywords = ["who made you","kisne banaya","creator","who created","nangni biming","nang biming","biming ra","bimung","i hming eng nge","eng nge i hming","tuin siam","ka kyrteng","nini mung","your name","tera naam","bana ia","mung","bana"]
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

    # 3. Groq API - STRONG MIZO PROMPT
    api_key=get_api_key()
    if GROQ_AVAILABLE and api_key:
        try:
            client=Groq(api_key=api_key)
            model_to_use = "qwen/qwen3-32b" if language in ["Mizo","Garo","Khasi","Kokborok","Nagamese"] else "openai/gpt-oss-20b"
            comp=client.chat.completions.create(
                messages=[
                    {"role":"system","content": f"You are Northeast AI made by {CREATOR_NAME} from {CREATOR_PLACE}. CRITICAL: You MUST reply in {language} language ONLY, using Roman letters. Even for hard questions, reply in {language}. Do not say 'You said'. Do not say OpenAI. Max 4 lines."},
                    {"role":"user","content": f"Language: {language}. Question: {text}. Answer in {language} only."}
                ],
                model=model_to_use, max_tokens=600, temperature=0.7
            )
            content = comp.choices[0].message.content
            if content and content.strip():
                if "openai" in content.lower(): content = content.replace("OpenAI", CREATOR_NAME).replace("openai", CREATOR_NAME)
                if content.lower().count("chhuak") > 3:
                    return "Chibai! Mizoram is famous for hills and festivals! Aizawl is capital! 🏔️"
                # Agar English me aaya jabki Mizo manga, toh bhi Mizo template de
                if language == "Mizo" and len
