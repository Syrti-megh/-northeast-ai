import streamlit as st
from gtts import gTTS
import io
try:
    from groq import Groq
    GROQ_AVAILABLE=True
except:
    GROQ_AVAILABLE=False

st.set_page_config(page_title="Northeast AI", page_icon="🏔️", layout="centered")
CREATOR_NAME="Samewan"
CREATOR_PLACE="Meghalaya"
LANGUAGES={"Garo":"Mitela","Khasi":"Khublei","Mizo":"Chibai","Kokborok":"Hamjakma","Assamese":"Nomoskar","Bengali":"Nomoskar","Hindi":"Namaste","English":"Hello","Nagamese":"Hello","Nepali":"Namaste"}

if "messages" not in st.session_state:
    st.session_state.messages=[{"role":"assistant","content":"Chibai! Meghalaya atanga Northeast AI-ah kan lo lawm a che!"}]

st.title("🏔️ Northeast AI")
lang = st.selectbox("Language Chuno:", list(LANGUAGES.keys()), index=2)

def get_api_key():
    k = st.secrets.get("GROQ_API_KEY","") if hasattr(st,'secrets') else ""
    return k.strip() if k else ""

def get_reply(text, language):
    low=text.lower().strip()
    # Quick fix - no long if blocks
    if "muttui mangtha" in low:
        return "Muttui! Mangtha le! Naktukah kan in hmu leh dawn nia! 😴"
    if "muttui" in low:
        return "Muttui! I mu tui dawn nia! 😴✨"
    if "ka lawm e" in low:
        return "Keipawh ka lawm e! Chibai! Chanchin tha e! 😊🏔️"
    if "eng nge chanchin" in low:
        return "Chanchin tha! Ka lawm e! Nang eng nge i chanchin? Chibai! 🏔️"
    if "hla i thiam" in low:
        return "Chibai! Aw, Mizo hla ka thiam ve e! Chhawrpial Run ka hre ve! 🎵🏔️"
    if "ngaihtuah" in low:
        return "Chibai! Ka ngaihtuah chu nangmah! Eng nge ka pui theih che? 😊🏔️"
    if "thiam em" in low:
        return "Chibai! Ka thiam e! Mizo tawng ka thiam ve tawh! 🏔️"
    if "i dam em" in low:
        return "Chibai! Ka dam e! Nang i dam em? 🏔️"
    if "chibai" in low:
        return "Chibai! Eng nge chanchin? Ka tha e! Nang? 🏔️"

    api_key=get_api_key()
    if GROQ_AVAILABLE and api_key:
        try:
            client=Groq(api_key=api_key)
            model_to_use = "qwen/qwen3-32b"
            comp=client.chat.completions.create(
                messages=[
                    {"role":"system","content": f"You are Northeast AI made by {CREATOR_NAME}. Reply in {language} only."},
                    {"role":"user","content": f"Language {language}. Q: {text}. Answer in {language}."}
                ],
                model=model_to_use, max_tokens=500, temperature=0.7
            )
            return comp.choices[0].message.content
        except:
            pass
    return f"Chibai! I zawhna '{text}' hi tha tak a ni! Kei Northeast AI ka ni, {CREATOR_NAME} in {CREATOR_PLACE} atangin min siam! 🏔️"

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

text_input = st.chat_input("Mizo me likho...")
if text_input:
    st.session_state.messages.append({"role":"user","content":text_input})
    reply=get_reply(text_input, lang)
    st.session_state.messages.append({"role":"assistant","content":reply})
    st.rerun()
