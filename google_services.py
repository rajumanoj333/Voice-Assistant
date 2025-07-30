import os
import logging
from typing import Optional, Tuple, Dict, Any
import io
import json
from datetime import datetime

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
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
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
                voice = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
                    name=voice_name or f"{language_code}-Neural2-D"
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

# Singleton instance with enhanced error handling
try:
    google_services = GoogleCloudServices()
except Exception as e:
    logger.error(f"Failed to initialize Google Cloud Services: {e}")
    google_services = None
