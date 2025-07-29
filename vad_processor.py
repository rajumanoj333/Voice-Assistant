import torch
import numpy as np
import io
import wave
from typing import List, Tuple
import torchaudio

class SileroVADProcessor:
    def __init__(self, model_name: str = 'silero_vad'):
        self.model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model=model_name,
            force_reload=False,
            onnx=False
        )
        
        self.get_speech_timestamps, self.save_audio, self.read_audio, self.VADIterator, self.collect_chunks = self.utils
        self.sampling_rate = 16000
        
    def detect_speech_segments(self, audio_bytes: bytes) -> List[Tuple[float, float]]:
        """
        Detect speech segments in audio data
        Returns list of (start_time, end_time) tuples in seconds
        """
        try:
            # Convert bytes to tensor
            audio_tensor = self._bytes_to_tensor(audio_bytes)
            
            # Get speech timestamps
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor, 
                self.model, 
                sampling_rate=self.sampling_rate
            )
            
            # Convert to seconds
            segments = []
            for timestamp in speech_timestamps:
                start_sec = timestamp['start'] / self.sampling_rate
                end_sec = timestamp['end'] / self.sampling_rate
                segments.append((start_sec, end_sec))
                
            return segments
            
        except Exception as e:
            print(f"Error in speech detection: {e}")
            return []
    
    def is_speech_present(self, audio_bytes: bytes, threshold: float = 0.5) -> bool:
        """
        Check if speech is present in the audio
        """
        try:
            audio_tensor = self._bytes_to_tensor(audio_bytes)
            speech_prob = self.model(audio_tensor, self.sampling_rate).item()
            return speech_prob > threshold
        except Exception as e:
            print(f"Error checking speech presence: {e}")
            return False
    
    def extract_speech_segments(self, audio_bytes: bytes) -> List[bytes]:
        """
        Extract only the speech segments from audio
        """
        try:
            audio_tensor = self._bytes_to_tensor(audio_bytes)
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor, 
                self.model, 
                sampling_rate=self.sampling_rate
            )
            
            speech_segments = []
            for timestamp in speech_timestamps:
                start_sample = timestamp['start']
                end_sample = timestamp['end']
                segment = audio_tensor[start_sample:end_sample]
                segment_bytes = self._tensor_to_bytes(segment)
                speech_segments.append(segment_bytes)
                
            return speech_segments
            
        except Exception as e:
            print(f"Error extracting speech segments: {e}")
            return [audio_bytes]  # Return original if extraction fails
    
    def _bytes_to_tensor(self, audio_bytes: bytes) -> torch.Tensor:
        """Convert audio bytes to tensor"""
        try:
            # Try to load as WAV first
            audio_io = io.BytesIO(audio_bytes)
            waveform, sample_rate = torchaudio.load(audio_io)
            
            # Resample if necessary
            if sample_rate != self.sampling_rate:
                resampler = torchaudio.transforms.Resample(sample_rate, self.sampling_rate)
                waveform = resampler(waveform)
            
            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            return waveform.squeeze()
            
        except Exception as e:
            # Fallback: assume raw PCM data
            print(f"Failed to load as audio file, treating as raw PCM: {e}")
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_tensor = torch.from_numpy(audio_array).float() / 32768.0
            return audio_tensor
    
    def _tensor_to_bytes(self, tensor: torch.Tensor) -> bytes:
        """Convert tensor back to bytes"""
        try:
            # Convert to numpy and scale to int16
            audio_array = (tensor.numpy() * 32767).astype(np.int16)
            
            # Create WAV file in memory
            output_io = io.BytesIO()
            with wave.open(output_io, 'wb') as wav_file:
                wav_file.setnchannels(1)  # mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sampling_rate)
                wav_file.writeframes(audio_array.tobytes())
            
            output_io.seek(0)
            return output_io.read()
            
        except Exception as e:
            print(f"Error converting tensor to bytes: {e}")
            return b""

# Singleton instance
vad_processor = SileroVADProcessor()
