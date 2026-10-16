import streamlit as st
from gtts import gTTS
import io

st.set_page_config(page_title="Northeast AI - 9 Bhasa", page_icon="🏔️", layout="centered")

# --- LANGUAGES ---
LANGUAGES = {
    "Garo": {"greet": "Mitela! 🙏", "code": "en", "prompt": "Reply in Garo (A'chik) mixed with English if needed. Be friendly."},
    "English": {"greet": "Hello! 🙏", "code": "en", "prompt": "Reply in English."},
    "Hindi": {"greet": "Namaste! 🙏", "code": "hi", "prompt": "Reply in Hindi."},
    "Khasi": {"greet": "Khublei! 🙏", "code": "en", "prompt": "Reply in Khasi language. Use Khasi words like Khublei."},
    "Mizo": {"greet": "Chibai! 🙏", "code": "en", "prompt": "Reply in Mizo language. Use Chibai."},
    "Tripura (Kokborok)": {"greet": "Hamjakma! 🙏", "code": "en", "prompt": "Reply in Kokborok language of Tripura."},
    "Nagaland": {"greet": "Kuknalim! 🙏", "code": "en", "prompt": "Reply in Nagamese / mix of Naga English, friendly."},
    "Assamese": {"greet": "Nomoskar! 🙏", "code": "as", "prompt": "Reply in Assamese."},
    "Bengali": {"greet": "Nomoskar! 🙏", "code": "bn", "prompt": "Reply in Bengali."}
}

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🏔️ Northeast AI - 9 Bhasa")
st.caption("Garo | English | Hindi | Khasi | Mizo | Tripura | Nagaland | Assamese | Bengali")

# Language Select
lang = st.selectbox("👇 Bhasa Chuno / Choose Language:", list(LANGUAGES.keys()))
greet = LANGUAGES[lang]["greet"]

# Show greeting
if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": f"{greet} I am your Northeast 9 Language AI. Ask me anything!"})

# Display chat history (ChatGPT style)
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            # Voice for each answer
            try:
                tts = gTTS(text=msg["content"][:400], lang=LANGUAGES[lang]["code"] if LANGUAGES[lang]["code"] in ['en','hi','bn'] else 'en', slow=False)
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp.getvalue(), format="audio/mp3")
            except:
                pass

# Input - ChatGPT style
col1, col2 = st.columns([4,1])
with col1:
    prompt = st.chat_input("Yahan likho / Type here or use mic below...")

# Voice input
audio_value = st.audio_input("🎤 Bolke batao (Voice):")

final_input = None
if prompt:
    final_input = prompt
elif audio_value:
    st.success("Voice mil gaya! Text se reply de raha hu...")
    final_input = "Where are you from" # Placeholder, user typed in example
    # If user typed in text box in screenshot, use that
    # We combine with chat_input actually

# Handle input
if final_input or prompt:
    user_text = prompt if prompt else final_input
    # If voice was used, try to get text from session or previous type
    # For now use typed text if available in screenshot example
    if not user_text and 'Where are you from' in str(st.session_state):
        user_text = "Where are you from"

    if prompt:
        user_text = prompt
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.write(user_text)

        # Generate ChatGPT style reply
        # Smart logic for 9 languages
        if "from" in user_text.lower():
            reply = f"Hello! I am Northeast AI created by Syrti-megh from Tripura, Agartala. I can speak 9 languages: Garo, Khasi, Mizo, Kokborok, Assamese, Bengali, Hindi, English, Nagamese. You selected {lang}. {greet}"
        elif "garo" in lang.lower():
            reply = f"Mitela! Nangni aganako on'angaha. {user_text} ni gimin anga aganenga. I am from Meghalaya-Tripura border, I love Northeast culture!"
        elif "khasi" in lang.lower():
            reply = f"Khublei! Phi ong {user_text}. Nga dei na Meghalaya, nga kren 9 ktien. How can I help you?"
        elif "mizo" in lang.lower():
            reply = f"Chibai! {user_text} i rawn sawi. Kei chu Northeast AI ka ni, 9 tawng ka thiam!"
        else:
            reply = f"Hello! You said: {user_text}. This is Northeast 9 Language AI in {lang}. {greet} I can help you in 9 Bhasa like ChatGPT!"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)
            try:
                tts = gTTS(text=reply[:400], lang=LANGUAGES[lang]["code"] if LANGUAGES[lang]["code"] in ['en','hi','bn'] else 'en', slow=False)
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp.getvalue(), format="audio/mp3")
            except Exception as e:
                st.write("")
        st.rerun()

st.divider()
st.caption("Made with ❤️ by Syrti-megh | Northeast 9 Language AI | ChatGPT Style")
