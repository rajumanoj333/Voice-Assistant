import os
import logging
from typing import Optional, Tuple, Dict, Any
import io
import json
from datetime import datetime

# Import database services
try:
    from models import voice_interaction_service, conversation_service, session_service
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    logger.warning("Database services not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleCloudServicesError(Exception):
    """Custom exception for Google Cloud Services errors"""
    pass

class ConfigurationError(GoogleCloudServicesError):
    """Raised when there's a configuration issue"""
    pass

class ServiceUnavailableError(GoogleCloudServicesError):
    """Raised when a service is unavailable"""
    pass

class GoogleCloudServices:
    """
    Enhanced Google Cloud Services with comprehensive error handling and user-friendly messages
    """
    
    def __init__(self):
        self.speech_client = None
        self.tts_client = None
        self.speech_config = None
        self.tts_voice = None
        self.tts_audio_config = None
        self.is_configured = False
        self.config_errors = []
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google Cloud services with proper error handling"""
        try:
            # Check if Google Cloud credentials are configured
            self._validate_credentials()
            
            # Initialize Speech-to-Text client
            from google.cloud import speech
            self.speech_client = speech.SpeechClient()
            
            # Initialize Text-to-Speech client
            from google.cloud import texttospeech
            self.tts_client = texttospeech.TextToSpeechClient()
            
            # Configure speech recognition
            self.speech_config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
                enable_automatic_punctuation=True,
                enable_word_confidence=True,
                enable_word_time_offsets=True,
                model="latest_long",  # Better for longer audio
                use_enhanced=True,    # Use enhanced models
            )
            
            # Configure text-to-speech
            self.tts_voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                ssml_gender=texttospeech.SsmlVoiceGender.MALE,
                name="en-US-Neural2-D"  # High quality neural voice
            )
            
            self.tts_audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                speaking_rate=1.0,  # Normal speed
                pitch=0.0,          # Normal pitch
                volume_gain_db=0.0  # Normal volume
            )
            
            self.is_configured = True
            logger.info("✅ Google Cloud Services initialized successfully")
            
        except ImportError as e:
            error_msg = "Google Cloud Speech libraries not installed. Please run: pip install google-cloud-speech google-cloud-texttospeech"
            logger.error(f"❌ {error_msg}")
            self.config_errors.append(error_msg)
            raise ConfigurationError(error_msg)
            
        except Exception as e:
            error_msg = f"Failed to initialize Google Cloud Services: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.config_errors.append(error_msg)
            raise ConfigurationError(error_msg)
    
    def _validate_credentials(self):
        """Validate Google Cloud credentials"""
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not creds_path:
            error_msg = """
🔐 Google Cloud credentials not configured!

To fix this:
1. Create a Google Cloud project at https://console.cloud.google.com/
2. Enable Speech-to-Text and Text-to-Speech APIs
3. Create a service account and download the JSON key file
4. Set the environment variable:
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
5. Or add to your .env file:
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

For testing without Google Cloud, the app will use fallback text-only mode.
"""
            logger.warning(error_msg)
            self.config_errors.append("Google Cloud credentials not configured")
            raise ConfigurationError(error_msg)
        
        if not os.path.exists(creds_path):
            error_msg = f"❌ Google Cloud credentials file not found: {creds_path}"
            logger.error(error_msg)
            self.config_errors.append(f"Credentials file not found: {creds_path}")
            raise ConfigurationError(error_msg)
        
        # Validate JSON format
        try:
            with open(creds_path, 'r') as f:
                json.load(f)
            logger.info(f"✅ Google Cloud credentials validated: {creds_path}")
        except json.JSONDecodeError:
            error_msg = f"❌ Invalid JSON format in credentials file: {creds_path}"
            logger.error(error_msg)
            self.config_errors.append("Invalid credentials file format")
            raise ConfigurationError(error_msg)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status information"""
        status = {
            "configured": self.is_configured,
            "errors": self.config_errors,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "speech_to_text": "available" if self.speech_client else "unavailable",
                "text_to_speech": "available" if self.tts_client else "unavailable"
            }
        }
        
        if self.is_configured:
            status["message"] = "✅ Google Cloud Services are ready to use"
        else:
            status["message"] = "❌ Google Cloud Services are not properly configured"
            status["help"] = """
To enable Google Cloud Services:
1. Set up Google Cloud project and enable APIs
2. Configure service account credentials
3. Set GOOGLE_APPLICATION_CREDENTIALS environment variable
4. Restart the application
"""
        
        return status
    
    def speech_to_text(self, audio_bytes: bytes, language_code: str = "en-US") -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Convert audio bytes to text using Google Cloud Speech-to-Text
        
        Returns:
            Tuple of (transcript, metadata) where metadata contains confidence, timing, etc.
        """
        if not self.is_configured:
            error_msg = "Speech-to-Text service not available - Google Cloud not configured"
            logger.error(f"❌ {error_msg}")
            return None, {"error": error_msg, "service": "unavailable"}
        
        try:
            from google.cloud import speech
            
            # Validate audio data
            if not audio_bytes or len(audio_bytes) == 0:
                error_msg = "No audio data provided"
                logger.error(f"❌ {error_msg}")
                return None, {"error": error_msg, "audio": "empty"}
            
            # Create audio object
            audio = speech.RecognitionAudio(content=audio_bytes)
            
            # Update language code if different
            config = self.speech_config
            if language_code != "en-US":
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code=language_code,
                    enable_automatic_punctuation=True,
                    model="latest_long",
                    use_enhanced=True,
                )
            
            logger.info(f"🎤 Processing speech-to-text (language: {language_code}, audio size: {len(audio_bytes)} bytes)")
            
            # Perform the transcription
            response = self.speech_client.recognize(config=config, audio=audio)
            
            if response.results:
                # Get the first result with highest confidence
                result = response.results[0]
                
                # Safely access alternatives and confidence
                if not result.alternatives:
                    error_msg = "No transcription alternatives available"
                    logger.error(f"❌ {error_msg}")
                    return None, {"error": error_msg, "alternatives": "empty"}
                
                transcript = result.alternatives[0].transcript
                # Confidence might not always be available, so we check for it
                confidence = getattr(result.alternatives[0], 'confidence', None)
                
                metadata = {
                    "confidence": confidence,
                    "language_code": language_code,
                    "audio_size_bytes": len(audio_bytes),
                    "processing_time": datetime.now().isoformat(),
                    "is_final": True,  # Regular recognize() results are always final
                    "alternatives": len(result.alternatives)
                }
                
                confidence_str = f"{confidence:.2f}" if confidence is not None else "unknown"
                logger.info(f"✅ Transcription successful (confidence: {confidence_str}): {transcript}")
                return transcript.strip(), metadata
            
            else:
                error_msg = "No speech detected in audio"
                logger.warning(f"⚠️ {error_msg}")
                return None, {"error": error_msg, "detection": "no_speech"}
            
        except Exception as e:
            error_msg = f"Speech-to-Text processing failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return None, {"error": error_msg, "exception": str(e)}
    
    def text_to_speech(self, text: str, voice_name: str = None, language_code: str = "en-US") -> Tuple[Optional[bytes], Dict[str, Any]]:
        """
        Convert text to speech using Google Cloud Text-to-Speech
        
        Returns:
            Tuple of (audio_bytes, metadata) where metadata contains voice info, timing, etc.
        """
        if not self.is_configured:
            error_msg = "Text-to-Speech service not available - Google Cloud not configured"
            logger.error(f"❌ {error_msg}")
            return None, {"error": error_msg, "service": "unavailable"}
        
        try:
            from google.cloud import texttospeech
            
            # Validate text input
            if not text or not text.strip():
                error_msg = "No text provided for speech synthesis"
                logger.error(f"❌ {error_msg}")
                return None, {"error": error_msg, "text": "empty"}
            
            # Prepare the text input
            synthesis_input = texttospeech.SynthesisInput(text=text.strip())
            
            # Configure voice if specified
            voice = self.tts_voice
            if voice_name or language_code != "en-US":
                default_voice_name = f"{language_code}-Neural2-F" if language_code.startswith("en") else f"{language_code}-Neural2-D"
                voice = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
                    name=voice_name or default_voice_name
                )
            
            logger.info(f"🔊 Synthesizing speech (language: {language_code}, text length: {len(text)} chars)")
            
            # Perform the text-to-speech request
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=self.tts_audio_config
            )
            
            metadata = {
                "text_length": len(text),
                "language_code": language_code,
                "voice_name": voice.name,
                "audio_size_bytes": len(response.audio_content),
                "processing_time": datetime.now().isoformat(),
                "audio_format": "LINEAR16",
                "sample_rate": 16000
            }
            
            logger.info(f"✅ Speech synthesis successful (audio size: {len(response.audio_content)} bytes)")
            return response.audio_content, metadata
            
        except Exception as e:
            error_msg = f"Text-to-Speech synthesis failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return None, {"error": error_msg, "exception": str(e)}
    
    def streaming_speech_to_text(self, audio_stream):
        """
        Stream audio and get real-time transcription with enhanced error handling
        """
        if not self.is_configured:
            error_msg = "Streaming Speech-to-Text service not available - Google Cloud not configured"
            logger.error(f"❌ {error_msg}")
            yield None, True, {"error": error_msg, "service": "unavailable"}
            return
        
        try:
            from google.cloud import speech
            
            config = speech.StreamingRecognitionConfig(
                config=self.speech_config,
                interim_results=True,
            )
            
            audio_generator = (speech.StreamingRecognizeRequest(audio_content=chunk)
                             for chunk in audio_stream)
            
            requests = (speech.StreamingRecognizeRequest(streaming_config=config),
                       *audio_generator)
            
            logger.info("🎤 Starting streaming speech recognition...")
            
            responses = self.speech_client.streaming_recognize(requests)
            
            for response in responses:
                for result in response.results:
                    # Safely access alternatives
                    if not result.alternatives:
                        continue
                    
                    transcript = result.alternatives[0].transcript
                    # Confidence might not always be available in streaming
                    confidence = getattr(result.alternatives[0], 'confidence', None)
                    
                    metadata = {
                        "confidence": confidence,
                        "is_final": result.is_final,
                        "processing_time": datetime.now().isoformat()
                    }
                    
                    yield transcript, result.is_final, metadata
                    
        except Exception as e:
            error_msg = f"Streaming speech-to-text failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            yield None, True, {"error": error_msg, "exception": str(e)}
    
    def test_services(self) -> Dict[str, Any]:
        """Test both speech services with sample data"""
        test_results = {
            "speech_to_text": {"status": "not_tested", "error": None},
            "text_to_speech": {"status": "not_tested", "error": None},
            "overall_status": "unknown"
        }
        
        if not self.is_configured:
            test_results["overall_status"] = "not_configured"
            return test_results
        
        # Test Speech-to-Text
        try:
            # Create a simple test audio (silence)
            import numpy as np
            sample_rate = 16000
            duration = 1.0
            audio_data = np.zeros(int(sample_rate * duration), dtype=np.int16)
            
            # Convert to bytes
            audio_bytes = audio_data.tobytes()
            
            transcript, metadata = self.speech_to_text(audio_bytes)
            if "error" in metadata:
                test_results["speech_to_text"] = {"status": "failed", "error": metadata["error"]}
            else:
                test_results["speech_to_text"] = {"status": "working", "metadata": metadata}
                
        except Exception as e:
            test_results["speech_to_text"] = {"status": "failed", "error": str(e)}
        
        # Test Text-to-Speech
        try:
            test_text = "Hello, this is a test of the text-to-speech service."
            audio_response, metadata = self.text_to_speech(test_text)
            if "error" in metadata:
                test_results["text_to_speech"] = {"status": "failed", "error": metadata["error"]}
            else:
                test_results["text_to_speech"] = {"status": "working", "metadata": metadata}
                
        except Exception as e:
            test_results["text_to_speech"] = {"status": "failed", "error": str(e)}
        
        # Determine overall status
        stt_status = test_results["speech_to_text"]["status"]
        tts_status = test_results["text_to_speech"]["status"]
        
        if stt_status == "working" and tts_status == "working":
            test_results["overall_status"] = "all_working"
        elif stt_status == "working" or tts_status == "working":
            test_results["overall_status"] = "partial"
        else:
            test_results["overall_status"] = "failed"
        
        return test_results
    
    def save_voice_interaction(self, audio_file_url: str, transcript: str, llm_response: str) -> Dict[str, Any]:
        """Save voice interaction to database"""
        if not DATABASE_AVAILABLE:
            logger.warning("Database not available - cannot save voice interaction")
            return {"success": False, "error": "Database not available"}
        
        try:
            interaction = voice_interaction_service.create_voice_interaction(
                audio_file_url=audio_file_url,
                transcript=transcript,
                llm_response=llm_response
            )
            
            if interaction:
                logger.info(f"✅ Voice interaction saved successfully: {interaction['id']}")
                return {"success": True, "interaction": interaction}
            else:
                logger.error("❌ Failed to save voice interaction")
                return {"success": False, "error": "Failed to create interaction"}
                
        except Exception as e:
            logger.error(f"❌ Error saving voice interaction: {e}")
            return {"success": False, "error": str(e)}
    
    def save_conversation_record(self, user_id: str, session_id: str, 
                                audio_input: bytes, text_input: str, 
                                text_response: str, audio_response: bytes,
                                sample_rate: int = 16000, audio_format: str = 'wav') -> Dict[str, Any]:
        """Save conversation record to database"""
        if not DATABASE_AVAILABLE:
            logger.warning("Database not available - cannot save conversation record")
            return {"success": False, "error": "Database not available"}
        
        try:
            record = conversation_service.create_conversation_record(
                user_id=user_id,
                session_id=session_id,
                audio_input=audio_input,
                text_input=text_input,
                text_response=text_response,
                audio_response=audio_response,
                sample_rate=sample_rate,
                audio_format=audio_format
            )
            
            if record:
                logger.info(f"✅ Conversation record saved successfully: {record['id']}")
                return {"success": True, "record": record}
            else:
                logger.error("❌ Failed to save conversation record")
                return {"success": False, "error": "Failed to create record"}
                
        except Exception as e:
            logger.error(f"❌ Error saving conversation record: {e}")
            return {"success": False, "error": str(e)}
    
    def create_user_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Create or update user session"""
        if not DATABASE_AVAILABLE:
            logger.warning("Database not available - cannot create session")
            return {"success": False, "error": "Database not available"}
        
        try:
            session = session_service.create_user_session(session_id, user_id)
            
            if session:
                logger.info(f"✅ User session created/updated: {session_id}")
                return {"success": True, "session": session}
            else:
                logger.error("❌ Failed to create user session")
                return {"success": False, "error": "Failed to create session"}
                
        except Exception as e:
            logger.error(f"❌ Error creating user session: {e}")
            return {"success": False, "error": str(e)}
    
    def get_conversation_history(self, user_id: str, session_id: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get conversation history from database"""
        if not DATABASE_AVAILABLE:
            logger.warning("Database not available - cannot get conversation history")
            return {"success": False, "error": "Database not available", "history": []}
        
        try:
            history = conversation_service.get_conversation_history(user_id, session_id, limit)
            logger.info(f"✅ Retrieved {len(history)} conversation records")
            return {"success": True, "history": history}
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation history: {e}")
            return {"success": False, "error": str(e), "history": []}
    
    def get_voice_interactions(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get voice interactions from database"""
        if not DATABASE_AVAILABLE:
            logger.warning("Database not available - cannot get voice interactions")
            return {"success": False, "error": "Database not available", "interactions": []}
        
        try:
            interactions = voice_interaction_service.get_voice_interactions(limit, offset)
            logger.info(f"✅ Retrieved {len(interactions)} voice interactions")
            return {"success": True, "interactions": interactions}
            
        except Exception as e:
            logger.error(f"❌ Error getting voice interactions: {e}")
            return {"success": False, "error": str(e), "interactions": []}

# Singleton instance with enhanced error handling
try:
    google_services = GoogleCloudServices()
except Exception as e:
    logger.error(f"Failed to initialize Google Cloud Services: {e}")
    google_services = None
