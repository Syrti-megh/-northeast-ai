import streamlit as st
from gtts import gTTS
import tempfile

st.set_page_config(page_title="Northeast 9 Language AI", page_icon="🏔️")

st.title("🏔️ Northeast AI - 9 Bhasa")
st.markdown("**Garo | English | Hindi | Khasi | Mizo | Tripura | Nagaland | Assamese | Bengali**")

lang_info = {
    "Garo": {"greet": "Mitela", "lang_code": "en"},
    "English": {"greet": "Hello", "lang_code": "en"},
    "Hindi": {"greet": "Namaste", "lang_code": "hi"},
    "Khasi": {"greet": "Khublei", "lang_code": "en"},
    "Mizo": {"greet": "Chibai", "lang_code": "en"},
    "Tripura-Kokborok": {"greet": "Khamma", "lang_code": "en"},
    "Nagaland-Nagamese": {"greet": "Moi laga dost", "lang_code": "en"},
    "Assamese": {"greet": "Nomoskar", "lang_code": "bn"},
    "Bengali": {"greet": "Nomoshkar", "lang_code": "bn"}
}

choice = st.selectbox("👇 Bhasa Chuno / Choose Language:", list(lang_info.keys()))
greet = lang_info[choice]["greet"]
code = lang_info[choice]["lang_code"]

st.write(f"### {greet}! 🙏")

text_input = st.text_input("Yahan likho / Type here:")
voice_input = st.audio_input("🎤 Bolke batao (Voice):")

user_text = text_input
if voice_input:
    st.success("Voice mil gaya! (Text se reply de raha hu)")

if st.button("🚀 Jawab Do"):
    if not user_text:
        user_text = "Mitela"

    # Simple smart reply for each language
    if choice == "Garo":
        reply = f"Mitela! Nanga {user_text} ko aganenga. Ia Garo AI nisim."
    elif choice == "Hindi":
        reply = f"Namaste! Aapne kaha {user_text}. Ye hai Northeast ka AI."
    elif choice == "Khasi":
        reply = f"Khublei! Phi ong {user_text}. Kane ka Northeast AI."
    elif choice == "Mizo":
        reply = f"Chibai! Nangin {user_text} i ti. Hei hi Northeast AI a ni."
    elif choice == "Tripura-Kokborok":
        reply = f"Khamma! Nwng {user_text} sakha. O kokborok AI se."
    elif choice == "Nagaland-Nagamese":
        reply = f"Moi laga dost! Apni koise {user_text}. Etu Northeast AI ase."
    elif choice == "Assamese":
        reply = f"Nomoskar! Apuni koise {user_text}. Eitu Northeast AI hoi."
    elif choice == "Bengali":
        reply = f"Nomoshkar! Apni bolechen {user_text}. Eta Northeast AI."
    else:
        reply = f"Hello! You said {user_text}. This is Northeast 9 Language AI."

    st.success(reply)

    # Bolke sunayega
    try:
        tts = gTTS(text=reply, lang=code)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            st.audio(fp.name)
    except:
        st.warning("Voice abhi nahi baj raha, par text ready hai!")

st.markdown("---")
st.caption("Made with ❤️ by Syrti-megh | Northeast 9 Language AI")
