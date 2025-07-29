import streamlit as st
import soundfile as sf
import io
from google_services import google_services
from llm_processor import llm_processor

st.set_page_config(page_title="Voice Assistant", page_icon="🗣️")
st.title("🗣️ Voice Assistant (Google Cloud + OpenAI)")
st.write("Upload or record your voice, or type a message. The assistant will reply with text and audio.")

# Session state for conversation
if "history" not in st.session_state:
    st.session_state["history"] = []

# Audio input
st.header("🎤 Speak or Upload Audio")
audio_file = st.file_uploader("Upload a WAV file (16kHz mono)", type=["wav"])

# Text input
st.header("💬 Or Type a Message")
user_text = st.text_input("Type your message:")

submit_audio = st.button("Send Audio")
submit_text = st.button("Send Text")

user_id = "streamlit_user"
session_id = "streamlit_session"

# Helper to play audio
def play_audio(audio_bytes):
    try:
        st.audio(audio_bytes, format="audio/wav")
    except Exception as e:
        st.error(f"Audio playback error: {e}")

# Process audio input
if submit_audio and audio_file is not None:
    audio_bytes = audio_file.read()
    st.info("Transcribing audio with Google Cloud...")
    transcript = google_services.speech_to_text(audio_bytes)
    if transcript:
        st.success(f"Transcript: {transcript}")
        st.session_state["history"].append(("user", transcript))
        st.info("Generating response with LLM...")
        response = llm_processor.process_text(transcript, user_id, session_id)
        if response:
            st.success(f"Assistant: {response}")
            st.session_state["history"].append(("assistant", response))
            st.info("Synthesizing response audio...")
            audio_response = google_services.text_to_speech(response)
            if audio_response:
                play_audio(audio_response)
            else:
                st.error("Failed to synthesize response audio.")
        else:
            st.error("LLM failed to generate a response.")
    else:
        st.error("Failed to transcribe audio.")
elif submit_audio and audio_file is None:
    st.warning("Please upload a WAV file.")

# Process text input
if submit_text and user_text.strip():
    st.session_state["history"].append(("user", user_text))
    st.info("Generating response with LLM...")
    response = llm_processor.process_text(user_text, user_id, session_id)
    if response:
        st.success(f"Assistant: {response}")
        st.session_state["history"].append(("assistant", response))
        st.info("Synthesizing response audio...")
        audio_response = google_services.text_to_speech(response)
        if audio_response:
            play_audio(audio_response)
        else:
            st.error("Failed to synthesize response audio.")
    else:
        st.error("LLM failed to generate a response.")

# Show conversation history
st.header("📝 Conversation History")
for role, msg in st.session_state["history"]:
    if role == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Assistant:** {msg}")