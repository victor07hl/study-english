import streamlit as st
import os
import base64
import hashlib
from dotenv import load_dotenv

from scraper import get_content_from_link
from llm_engine import get_llm_provider, TUTOR_SYSTEM_PROMPT
from speech_engine import text_to_speech, transcribe_audio

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="English Practice Tutor", layout="wide")

# Custom CSS for modern UI
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    /* Modern audio input styling */
    [data-testid="stAudioInput"] { border-radius: 20px; }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "content" not in st.session_state:
    st.session_state.content = ""
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None
if "processed_audio_hash" not in st.session_state:
    st.session_state.processed_audio_hash = None

def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Use a nice header/branding instead of "Settings"
    st.markdown("<h2 style='text-align: center;'>🎓 Study English</h2>", unsafe_allow_html=True)
    
    # Attractive Status Indicator
    if os.getenv("ANTHROPIC_API_KEY"):
        st.markdown("<div style='text-align: center; color: #28a745; font-size: 40px;'>🤖</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Tutor Online</p>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center; color: #dc3545; font-size: 40px;'>⚠️</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Key Missing in .env</p>", unsafe_allow_html=True)
    
    st.divider()
    
    input_type = st.radio("Choose Practice Source", ["Pre-defined Topic", "Custom Topic", "URL (Blog/YouTube)"])
    
    if input_type == "Pre-defined Topic":
        topic_files = sorted([f for f in os.listdir("topics") if f.endswith(".md")])
        topic_names = [f.replace(".md", "").replace("_", " ").title() for f in topic_files]
        selected_topic_name = st.selectbox("Select a topic", topic_names)
        
        if st.button("Start Pre-defined Practice"):
            filename = selected_topic_name.lower().replace(" ", "_") + ".md"
            with open(os.path.join("topics", filename), "r") as f:
                st.session_state.content = f.read()
            st.session_state.messages = []
            st.session_state.last_audio = None
            st.rerun()

    elif input_type == "Custom Topic":
        practice_topic = st.text_input("What would you like to talk about?", placeholder="e.g., Music")
        if st.button("Start Custom Practice"):
            st.session_state.content = f"The user wants to practice English by talking about: {practice_topic}"
            st.session_state.messages = []
            st.session_state.last_audio = None
            st.rerun()
            
    else:
        url = st.text_input("Enter Link (Blog or YouTube)", placeholder="https://...")
        if st.button("Extract & Start"):
            with st.spinner("Extracting..."):
                content = get_content_from_link(url)
                if content:
                    st.session_state.content = content
                    st.session_state.messages = []
                    st.session_state.last_audio = None
                    st.rerun()
                else:
                    st.error("Could not extract content.")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()

# Main Interface
st.title("🗣️ English Practice Tutor")

# Interaction Logic & Cold Start
if st.session_state.content and len(st.session_state.messages) == 0:
    with st.spinner("Preparing first question..."):
        provider = get_llm_provider("claude")
        system_prompt = f"{TUTOR_SYSTEM_PROMPT}\n\nCONTENT TO DISCUSS:\n{st.session_state.content[:2000]}"
        initial_messages = [{"role": "user", "content": "Hello! I'm ready. Introduce the topic and ask the first question."}]
        agent_response = provider.get_response(initial_messages, system_prompt)
        st.session_state.messages.append({"role": "assistant", "content": agent_response})
        audio_path = text_to_speech(agent_response)
        st.session_state.last_audio = audio_path
        st.rerun()

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Bottom Interaction Area
st.divider()

if not st.session_state.content:
    st.info("Please enter a topic or link in the sidebar to start.")
else:
    # Modern Microphone UI
    st.write("Click the microphone below to start your answer:")
    audio_input = st.audio_input("Record your answer", label_visibility="collapsed")

    if audio_input:
        audio_bytes = audio_input.read()
        audio_hash = hashlib.md5(audio_bytes).hexdigest()
        
        if st.session_state.processed_audio_hash != audio_hash:
            st.session_state.processed_audio_hash = audio_hash
            
            with st.spinner("Transcribing..."):
                user_text = transcribe_audio(audio_bytes)
                if user_text:
                    st.session_state.messages.append({"role": "user", "content": user_text})
                    provider = get_llm_provider("claude")
                    system_prompt = f"{TUTOR_SYSTEM_PROMPT}\n\nCONTENT TO DISCUSS:\n{st.session_state.content[:2000]}"
                    
                    with st.spinner("Agent is thinking..."):
                        agent_response = provider.get_response(st.session_state.messages, system_prompt)
                        st.session_state.messages.append({"role": "assistant", "content": agent_response})
                        audio_path = text_to_speech(agent_response)
                        st.session_state.last_audio = audio_path
                        st.rerun()

# Trigger Audio Autoplay
if st.session_state.last_audio and os.path.exists(st.session_state.last_audio):
    autoplay_audio(st.session_state.last_audio)
    st.session_state.last_audio = None
