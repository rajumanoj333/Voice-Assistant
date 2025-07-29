import streamlit as st
import soundfile as sf
import io
import json
from datetime import datetime

# Import services with error handling
try:
    from google_services import google_services
    GOOGLE_SERVICES_AVAILABLE = True
except Exception as e:
    st.error(f"❌ Failed to load Google Cloud Services: {e}")
    GOOGLE_SERVICES_AVAILABLE = False
    google_services = None

try:
    from llm_processor import llm_processor
    LLM_AVAILABLE = True
except Exception as e:
    st.error(f"❌ Failed to load LLM processor: {e}")
    LLM_AVAILABLE = False
    llm_processor = None

# Page configuration
st.set_page_config(
    page_title="Voice Assistant", 
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .error-card {
        background: #ffe6e6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff4444;
        margin: 1rem 0;
    }
    .success-card {
        background: #e6ffe6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #44ff44;
        margin: 1rem 0;
    }
    .info-card {
        background: #e6f3ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4488ff;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🗣️ Voice Assistant</h1>
    <p>Powered by Google Cloud Speech & OpenAI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for status and configuration
with st.sidebar:
    st.header("🔧 System Status")
    
    # Google Cloud Services Status
    if GOOGLE_SERVICES_AVAILABLE and google_services:
        status = google_services.get_service_status()
        
        if status["configured"]:
            st.success("✅ Google Cloud Services")
            st.info(f"Speech-to-Text: {status['services']['speech_to_text']}")
            st.info(f"Text-to-Speech: {status['services']['text_to_speech']}")
        else:
            st.error("❌ Google Cloud Services")
            st.error("Not configured")
            
            # Show configuration help
            with st.expander("🔧 How to configure Google Cloud"):
                st.markdown("""
                1. **Create Google Cloud Project**
                   - Go to [Google Cloud Console](https://console.cloud.google.com/)
                   - Create a new project or select existing
                
                2. **Enable APIs**
                   - Enable Speech-to-Text API
                   - Enable Text-to-Speech API
                
                3. **Create Service Account**
                   - Go to IAM & Admin > Service Accounts
                   - Create new service account
                   - Download JSON key file
                
                4. **Set Environment Variable**
                   ```bash
                   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/key.json
                   ```
                
                5. **Restart the application**
                """)
    else:
        st.error("❌ Google Cloud Services")
        st.error("Not available")
    
    # LLM Status
    if LLM_AVAILABLE:
        st.success("✅ LLM Processor")
    else:
        st.error("❌ LLM Processor")
        st.error("Not available")
    
    # Test Services Button
    if st.button("🧪 Test Services"):
        if GOOGLE_SERVICES_AVAILABLE and google_services:
            with st.spinner("Testing Google Cloud Services..."):
                test_results = google_services.test_services()
                st.json(test_results)
        else:
            st.error("Google Cloud Services not available for testing")

# Session state initialization
if "history" not in st.session_state:
    st.session_state["history"] = []

if "processing_status" not in st.session_state:
    st.session_state["processing_status"] = "idle"

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎤 Voice Input")
    
    # Audio file upload
    audio_file = st.file_uploader(
        "Upload a WAV file (16kHz mono recommended)", 
        type=["wav", "mp3", "m4a"],
        help="For best results, use 16kHz mono WAV files. Other formats will be converted."
    )
    
    # Audio recording (if supported)
    try:
        import streamlit_audio_recorder as audio_recorder
        recorded_audio = audio_recorder.audio_recorder(
            text="Or record audio directly:",
            recording_color="#e74c3c",
            neutral_color="#6c757d",
            icon_name="microphone",
            icon_size="2x"
        )
    except ImportError:
        st.info("💡 Install 'streamlit-audio-recorder' for direct recording: `pip install streamlit-audio-recorder`")
        recorded_audio = None

with col2:
    st.header("💬 Text Input")
    user_text = st.text_area(
        "Type your message:",
        height=100,
        placeholder="Enter your message here..."
    )

# Action buttons
col1, col2, col3 = st.columns(3)

with col1:
    submit_audio = st.button("🎤 Send Audio", type="primary", use_container_width=True)

with col2:
    submit_text = st.button("💬 Send Text", type="primary", use_container_width=True)

with col3:
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state["history"] = []
        st.rerun()

# Helper function to play audio
def play_audio(audio_bytes, format="audio/wav"):
    """Enhanced audio playback with error handling"""
    try:
        st.audio(audio_bytes, format=format)
        return True
    except Exception as e:
        st.error(f"❌ Audio playback error: {e}")
        return False

# Helper function to display processing status
def show_processing_status(status, message):
    """Display processing status with appropriate styling"""
    if status == "processing":
        st.info(f"⏳ {message}")
    elif status == "success":
        st.success(f"✅ {message}")
    elif status == "error":
        st.error(f"❌ {message}")
    elif status == "warning":
        st.warning(f"⚠️ {message}")

# Process audio input
if submit_audio:
    audio_data = None
    
    # Determine audio source
    if audio_file is not None:
        audio_data = audio_file.read()
        source_name = f"uploaded file: {audio_file.name}"
    elif recorded_audio is not None:
        audio_data = recorded_audio
        source_name = "recorded audio"
    else:
        st.error("❌ Please upload an audio file or record audio")
        st.stop()
    
    if audio_data:
        st.session_state["processing_status"] = "processing"
        
        # Display processing status
        with st.status("Processing audio...", expanded=True) as status:
            st.write("🎤 Transcribing audio...")
            
            if GOOGLE_SERVICES_AVAILABLE and google_services:
                transcript, metadata = google_services.speech_to_text(audio_data)
                
                if transcript:
                    st.write(f"✅ Transcription successful (confidence: {metadata.get('confidence', 'N/A'):.2f})")
                    st.write(f"📝 **Transcript:** {transcript}")
                    
                    # Add to history
                    st.session_state["history"].append(("user", transcript, metadata))
                    
                    # Process with LLM
                    st.write("🤖 Generating response...")
                    if LLM_AVAILABLE:
                        response = llm_processor.process_text(transcript, "streamlit_user", "streamlit_session")
                        if response:
                            st.write(f"✅ Response generated")
                            st.write(f"💬 **Assistant:** {response}")
                            
                            # Add to history
                            st.session_state["history"].append(("assistant", response, {}))
                            
                            # Generate audio response
                            st.write("🔊 Synthesizing speech...")
                            audio_response, tts_metadata = google_services.text_to_speech(response)
                            
                            if audio_response:
                                st.write("✅ Audio synthesis successful")
                                play_audio(audio_response)
                                
                                # Add audio metadata to history
                                if st.session_state["history"]:
                                    st.session_state["history"][-1] = (st.session_state["history"][-1][0], 
                                                                     st.session_state["history"][-1][1], 
                                                                     tts_metadata)
                            else:
                                st.error("❌ Failed to synthesize response audio")
                                if "error" in tts_metadata:
                                    st.error(f"Error: {tts_metadata['error']}")
                        else:
                            st.error("❌ LLM failed to generate response")
                    else:
                        st.error("❌ LLM processor not available")
                else:
                    st.error("❌ Failed to transcribe audio")
                    if "error" in metadata:
                        st.error(f"Error: {metadata['error']}")
                    elif "detection" in metadata and metadata["detection"] == "no_speech":
                        st.warning("⚠️ No speech detected in audio")
                    else:
                        st.error("Unknown transcription error")
            else:
                st.error("❌ Google Cloud Services not available")
                st.error("Please configure Google Cloud credentials to use speech services")
            
            status.update(label="Processing complete!", state="complete")

# Process text input
if submit_text and user_text.strip():
    st.session_state["processing_status"] = "processing"
    
    with st.status("Processing text...", expanded=True) as status:
        st.write("💬 Processing text input...")
        
        # Add to history
        st.session_state["history"].append(("user", user_text, {}))
        
        # Process with LLM
        st.write("🤖 Generating response...")
        if LLM_AVAILABLE:
            response = llm_processor.process_text(user_text, "streamlit_user", "streamlit_session")
            if response:
                st.write(f"✅ Response generated")
                st.write(f"💬 **Assistant:** {response}")
                
                # Add to history
                st.session_state["history"].append(("assistant", response, {}))
                
                # Generate audio response
                st.write("🔊 Synthesizing speech...")
                if GOOGLE_SERVICES_AVAILABLE and google_services:
                    audio_response, tts_metadata = google_services.text_to_speech(response)
                    
                    if audio_response:
                        st.write("✅ Audio synthesis successful")
                        play_audio(audio_response)
                        
                        # Add audio metadata to history
                        if st.session_state["history"]:
                            st.session_state["history"][-1] = (st.session_state["history"][-1][0], 
                                                             st.session_state["history"][-1][1], 
                                                             tts_metadata)
                    else:
                        st.error("❌ Failed to synthesize response audio")
                        if "error" in tts_metadata:
                            st.error(f"Error: {tts_metadata['error']}")
                else:
                    st.warning("⚠️ Google Cloud Services not available - text response only")
            else:
                st.error("❌ LLM failed to generate response")
        else:
            st.error("❌ LLM processor not available")
        
        status.update(label="Processing complete!", state="complete")

# Display conversation history
st.header("📝 Conversation History")

if not st.session_state["history"]:
    st.info("💡 Start a conversation by uploading audio or typing a message!")
else:
    for i, (role, message, metadata) in enumerate(st.session_state["history"]):
        if role == "user":
            with st.chat_message("user"):
                st.write(message)
                if metadata and "confidence" in metadata:
                    st.caption(f"Confidence: {metadata['confidence']:.2f}")
        else:
            with st.chat_message("assistant"):
                st.write(message)
                if metadata and "audio_size_bytes" in metadata:
                    st.caption(f"Audio: {metadata['audio_size_bytes']} bytes")

# Footer with additional information
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🎯 <strong>Tips for best results:</strong></p>
    <ul style="list-style: none; padding: 0;">
        <li>🎤 Use clear speech and minimize background noise</li>
        <li>📁 Upload 16kHz mono WAV files for best transcription</li>
        <li>🔧 Ensure Google Cloud credentials are properly configured</li>
        <li>🌐 Check your internet connection for cloud services</li>
    </ul>
</div>
""", unsafe_allow_html=True)