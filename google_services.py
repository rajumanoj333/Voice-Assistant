import os
from google.cloud import speech
from google.cloud import texttospeech
from typing import Optional
import io

class GoogleCloudServices:
    def __init__(self):
        # Initialize Speech-to-Text client
        self.speech_client = speech.SpeechClient()
        
        # Initialize Text-to-Speech client
        self.tts_client = texttospeech.TextToSpeechClient()
        
        # Configure speech recognition
        self.speech_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_automatic_punctuation=True,
            enable_word_confidence=True,
            enable_word_time_offsets=True,
        )
        
        # Configure text-to-speech
        self.tts_voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
            name="en-US-Neural2-D"  # High quality neural voice
        )
        
        self.tts_audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000
        )
    
    def speech_to_text(self, audio_bytes: bytes, language_code: str = "en-US") -> Optional[str]:
        """
        Convert audio bytes to text using Google Cloud Speech-to-Text
        """
        try:
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
                )
            
            # Perform the transcription
            response = self.speech_client.recognize(config=config, audio=audio)
            
            if response.results:
                # Get the first result with highest confidence
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                
                print(f"Transcription confidence: {confidence}")
                return transcript.strip()
            
            return None
            
        except Exception as e:
            print(f"Error in speech-to-text: {e}")
            return None
    
    def text_to_speech(self, text: str, voice_name: str = None, language_code: str = "en-US") -> Optional[bytes]:
        """
        Convert text to speech using Google Cloud Text-to-Speech
        """
        try:
            # Prepare the text input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice if specified
            voice = self.tts_voice
            if voice_name or language_code != "en-US":
                voice = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
                    name=voice_name or f"{language_code}-Neural2-D"
                )
            
            # Perform the text-to-speech request
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=self.tts_audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            return None
    
    def streaming_speech_to_text(self, audio_stream):
        """
        Stream audio and get real-time transcription
        """
        try:
            config = speech.StreamingRecognitionConfig(
                config=self.speech_config,
                interim_results=True,
            )
            
            audio_generator = (speech.StreamingRecognizeRequest(audio_content=chunk)
                             for chunk in audio_stream)
            
            requests = (speech.StreamingRecognizeRequest(streaming_config=config),
                       *audio_generator)
            
            responses = self.speech_client.streaming_recognize(requests)
            
            for response in responses:
                for result in response.results:
                    yield result.alternatives[0].transcript, result.is_final
                    
        except Exception as e:
            print(f"Error in streaming speech-to-text: {e}")
            yield None, True

# Singleton instance
google_services = GoogleCloudServices()
