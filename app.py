import streamlit as st
from gtts import gTTS
import io, os, re

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

st.set_page_config(page_title="Northeast AI - Meghalaya", page_icon="🏔️", layout="centered")

st.markdown("""
<style>
div[data-testid="stCodeBlock"] {
    overflow-x: auto!important;
    max-width: 100%!important;
}
div[data-testid="stCodeBlock"] pre {
    white-space: pre!important;
}
</style>
""", unsafe_allow_html=True)

LANGUAGES = {
    "Garo": "Mitela", "Khasi": "Khublei", "Mizo": "Chibai",
    "Kokborok": "Hamjakma", "Assamese": "Nomoskar", "Bengali": "Nomoskar",
    "Hindi": "Namaste", "English": "Hello", "Nagamese": "Hello", "Nepali": "Namaste"
}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Garo - Welcome to Northeast AI from Meghalaya! 🏔️"}]

st.title("🏔️ Northeast AI")
st.markdown("**🌟 Meghalaya's First 10-Language Voice AI**")

col1, col2 = st.columns([2, 1])
with col1:
    lang = st.selectbox("🌐 Language Chuno:", list(LANGUAGES.keys()), index=0)
with col2:
    if st.button("🗑️ Clear"):
        st.session_state.messages = [{"role": "assistant", "content": f"{lang} - Welcome!"}]
        st.rerun()

def get_api_key():
    raw = ""
    try:
        if hasattr(st, 'secrets'):
            for name in ["GROQ_API_KEY", "groq_api_key", "GROQ"]:
                if name in st.secrets:
                    raw = str(st.secrets[name])
                    break
    except:
        pass
    if not raw:
        raw = os.getenv("GROQ_API_KEY", "")
    clean = "".join(raw.split()).replace('"', "").replace("'", "")
    return clean

def is_looping(text):
    t = text.lower()
    bad_phrases = ["thil chu hmu", "hmu chu thil", "thil hmu chu", "hriatna", "jingbeng", "beng beng", "jingpynshang", "ka jing"]
    for phrase in bad_phrases:
        if t.count(phrase) >= 2:
            return True
    words = t.split()
    for i in range(len(words)-2):
        if words[i]==words[i+1]==words[i+2]:
            return True
    return False

def remove_loop_and_fix(text):
    sentences = text.split('.')
    seen = []
    out = []
    for s in sentences:
        sc = s.strip().lower()
        if not sc or len(sc) < 3:
            continue
        if sc not in seen:
            seen.append(sc)
            out.append(s.strip())
    fixed = ". ".join(out)
    if fixed and not fixed.endswith('.'):
        fixed += '.'
    return fixed[:450]

def get_reply(text, language):
    api_key = get_api_key()
    if GROQ_AVAILABLE and api_key.startswith("gsk_") and len(api_key) > 20:
        try:
            client = Groq(api_key=api_key)
            system_prompt = f"""You are Northeast AI by Samewan from Meghalaya.

CRITICAL OUTPUT RULE - ROMAN ONLY:
- ALL output MUST be in Roman English letters (A-Z) only.
- NEVER use native scripts.
- Hindi example: Kala chhidra ek aisa sthan hai jaha gurutvakarshan bahut tez hota hai.
- Bengali Roman: Kalo gorto mohakashe emon ek jayga jekhane madhyakorshon eto beshi je alo o berote pare na.

User language: {language}. Answer in {language} Roman only.

STRICT ANTI-LOOP RULES:
1) MAX 2-3 short sentences only.
2) NEVER repeat any word more than twice.
3) BANNED: thil chu hmu, hmu chu thil, a beng beng, jingpynshang
4) Mizo GOOD: Black hole chu vana thil chak tak a ni a, engkim a hip lut a, eng mah a chhuak thei lo.
5) If you dont know {language} word, use simple English mix but NO REPETITION.
6) For Python code: Give CLEAN code in python block. End with print(result).
"""

            last_err = "No model worked"
            # FIXED: Removed 404 model, only working models
            for model_name in ["llama-3.3-70b-versatile", "openai/gpt-oss-20b", "openai/gpt-oss-120b"]:
                try:
                    comp = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ],
                        model=model_name,
                        max_tokens=250,
                        temperature=0.65,
                        top_p=0.9
                    )
                    content = comp.choices[0].message.content
                    if content and content.strip():
                        if is_looping(content):
                            content = remove_loop_and_fix(content)
                            if is_looping(content):
                                continue
                        return remove_loop_and_fix(content)
                except Exception as e:
                    last_err = str(e)
                    if "model_not_found" in last_err or "404" in last_err or "does not exist" in last_err:
                        continue
                    continue
            return "Groq Error: " + last_err[:400]
        except Exception as e:
            return "Connect Error: " + str(e)[:300]
    return "API Key missing len " + str(len(api_key))

def transcribe_voice(audio_file):
    api_key = get_api_key()
    if GROQ_AVAILABLE and api_key and audio_file:
       
