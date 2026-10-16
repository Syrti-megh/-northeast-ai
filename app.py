import streamlit as st
from gtts import gTTS
import io, os
try:
    from groq import Groq
    GROQ_AVAILABLE=True
except:
    GROQ_AVAILABLE=False

st.set_page_config(page_title="Northeast AI", page_icon="🏔️", layout="centered")

CREATOR_NAME="Samewan"
CREATOR_PLACE="Meghalaya"

LANGUAGES=["Garo","Khasi","Mizo","Kokborok","Assamese","Bengali","Hindi","English","Nagamese"]

if "messages" not in st.session_state:
    st.session_state.messages=[]

st.title("🏔️ Northeast AI")
st.caption("9 Bhasa Voice ChatGPT")

with st.sidebar:
    lang=st.selectbox("Bhasa:", LANGUAGES)
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages=[]
        st.rerun()

def get_reply(text):
    low=text.lower()
    if any(k in low for k in ["who made you","kisne banaya","tumhe kisne","creator","banaya kisne","who created"]):
        return f"Mujhe banaya hai {CREATOR_NAME} ne, {CREATOR_PLACE} se! 🏔️"

    api_key=st.secrets.get("GROQ_API_KEY","")
    if GROQ_AVAILABLE and api_key:
        try:
            client=Groq(api_key=api_key)
            comp=client.chat.completions.create(
                messages=[{"role":"user","content":f"You are Northeast AI, creator is {CREATOR_NAME} from {CREATOR_PLACE}. Reply in {lang}. User: {text}"}],
                model="llama-3.1-8b-instant", max_tokens=250)
            return comp.choices[0].message.content
        except:
            pass
    return f"Mitela! You said: {text} - in {lang}. How can I help?"

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"]=="assistant":
            try:
                tts=gTTS(text=msg["content"][:300], lang='en')
                fp=io.BytesIO(); tts.write_to_fp(fp)
                st.audio(fp.getvalue(), format="audio/mp3")
            except: pass

# --- VOICE INPUT + TEXT INPUT ---
st.divider()
col1, col2 = st.columns([3,1])
with col1:
    text_input = st.chat_input(f"Type in {lang}...")
with col2:
    voice = st.audio_input("🎤 Bolo")

user_text = None
if text_input:
    user_text = text_input
elif voice:
    user_text = "Hello (voice message)" # Speech-to-text ke liye Whisper chahiye, abhi text samjho
    st.success("Voice received! Text reply de raha hu")

if user_text:
    st.session_state.messages.append({"role":"user","content":user_text})
    with st.chat_message("user"): st.write(user_text)

    reply=get_reply(user_text)
    st.session_state.messages.append({"role":"assistant","content":reply})
    with st.chat_message("assistant"):
        st.write(reply)
        try:
            tts=gTTS(text=reply[:300], lang='en')
            fp=io.BytesIO(); tts.write_to_fp(fp)
            st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)
        except: pass
    st.rerun()
