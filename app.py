import streamlit as st
from gtts import gTTS
import io, os, re
from groq import Groq

st.set_page_config(page_title="Northeast AI - Meghalaya", page_icon="🏔️", layout="centered")

LANGUAGES = {
    "Garo": "Mitela", "Khasi": "Khublei", "Mizo": "Chibai",
    "Kokborok": "Hamjakma", "Assamese": "Nomoskar", "Bengali": "Nomoskar",
    "Hindi": "Namaste", "English": "Hello", "Nagamese": "Hello", "Nepali": "Namaste"
}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to Northeast AI - Scientific Edition! 🏔️🔬"}]

st.title("🏔️ Northeast AI")
st.markdown("**🌟 Meghalaya's First 10-Language Scientific Voice AI**")

col1, col2 = st.columns([2, 1])
with col1:
    lang = st.selectbox("🌐 Language Chuno:", list(LANGUAGES.keys()), index=0)
with col2:
    if st.button("🗑️ Clear"):
        st.session_state.messages = [{"role": "assistant", "content": f"{lang} - Welcome!"}]
        st.rerun()

def get_api_key():
    key = ""
    try:
        key = st.secrets["GROQ_API_KEY"]
    except:
        key = os.getenv("GROQ_API_KEY", "")
    key = str(key).strip().replace('"','').replace("'","").replace(" ","").replace("\n","")
    return key

def is_looping(text):
    t = text.lower()
    # Mizo specific loops
    if t.count("a hman a") >= 2: return True
    if t.count("a mass") >= 2 or t.count("a energy") >= 2: return True
    for phrase in ["thil chu hmu", "hmu chu thil", "beng beng"]:
        if t.count(phrase) >= 2: return True
    # Duplicate sentences
    sentences = [s.strip() for s in text.split('.') if len(s.strip())>5]
    lower = [s.lower() for s in sentences]
    if len(lower) != len(set(lower)): return True
    return False

def remove_loop_and_fix(text):
    # 1. Split
    parts = [p.strip() for p in text.split('.') if p.strip()]
    # 2. Deduplicate + filter short repetitive fragments
    seen = set()
    out = []
    for p in parts:
        low = p.lower()
        # Skip if contains repetitive pattern "a hman a" already used
        if "a hman a" in low and any("a hman a" in o.lower() for o in out):
            continue
        # Skip if very similar to previous (first 12 chars same)
        if any(low[:12] == s[:12] for s in seen if len(low)>12):
            continue
        if low not in seen and len(p) > 10:
            seen.add(low)
            out.append(p)
        if len(out) >= 2: # MAX 2 sentences - loop khatam
            break
    
    fixed = ". ".join(out)
    # Final cleanup: remove double "A hman a, a mass a" type list
    fixed = re.sub(r'A hman a,\s*a mass a,\s*a energy a.*?\.', '', fixed, flags=re.IGNORECASE)
    fixed = re.sub(r'\s+', ' ', fixed).strip()
    if fixed and not fixed.endswith('.'):
        fixed += '.'
    return fixed[:400] if fixed else "Black hole chu vana thil chak tak a ni a, a gravity avangin light pawh a chhuak thei lo."

def get_reply(text, language):
    api_key = get_api_key()
    if not api_key.startswith("gsk_"):
        return f"API Key Error: Secrets me GROQ_API_KEY nahi mila!"
    try:
        client = Groq(api_key=api_key)
        system_prompt = f"""You are Northeast AI, SCIENTIFIC TEACHER by Samewan.
CRITICAL ANTI-LOOP RULES:
1. Give ONLY 1-2 DIFFERENT sentences. NEVER repeat pattern "A hman a".
2. Scientific only, no spiritual.
3. Language: {language} in Roman letters only.
4. Structure: Sentence 1 = What it is. Sentence 2 = Why it happens (gravity/light).
5. FORBIDDEN to repeat "A hman a, a mass a, a energy a".

PERFECT EXAMPLE Mizo: Black hole chu vana hmun a ni a, a gravity chak lutuk avangin engkim a hip lut vek a. A chak lutuk avangin light pawh a chhuak thei lo.

Now answer in {language} Roman, 2 sentences max."""

        for model_name in ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]:
            try:
                comp = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    model=model_name,
                    max_tokens=180,
                    temperature=0.3,
                    top_p=0.8
                )
                content = comp.choices[0].message.content.strip()
                if content:
                    cleaned = remove_loop_and_fix(content)
                    if not is_looping(cleaned) and len(cleaned) > 15:
                        return cleaned
            except Exception as e:
                continue
        return "Black hole chu vana hmun chak tak a ni a, a gravity chak avangin light pawh a chhuak thei lo."
    except Exception as e:
        return f"Error: {str(e)[:300]}"

def transcribe_voice(audio_file):
    api_key = get_api_key()
    if api_key.startswith("gsk_") and audio_file:
        try:
            client = Groq(api_key=api_key)
            tr = client.audio.transcriptions.create(file=("voice.wav", audio_file.getvalue()), model="whisper-large-v3")
            return tr.text
        except:
            return None
    return None

def speak_clear(text):
    try:
        clean = re.sub(r"[^A-Za-z0-9 ,.]", " ", text)[:350].strip()
        if len(clean) < 5: return None
        tts = gTTS(text=clean, lang='en', tld='co.in', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except:
        return None

def render_message(content):
    st.write(content)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        render_message(msg["content"])

st.divider()
voice_input = st.audio_input("🎤 " + lang + " me Bolo")
user_text = None
if voice_input:
    with st.spinner("Sun raha hu..."):
        transcribed = transcribe_voice(voice_input)
        if transcribed:
            user_text = transcribed
            st.success("🎤 Suna: " + transcribed)

text_input = st.chat_input(LANGUAGES[lang] + "! Yahan likho...")
if text_input:
    user_text = text_input

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)
    reply = get_reply(user_text, lang)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        render_message(reply)
        audio = speak_clear(reply)
        if audio:
            st.audio(audio, format="audio/mp3", autoplay=True)
