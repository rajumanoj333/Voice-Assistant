#!/usr/bin/env python3
"""
Voice Assistant gRPC Client Example
Demonstrates how to use the voice assistant service
"""

import grpc
import uuid
import io
import wave
import time
from typing import Generator

# Import generated protobuf classes
import voice_assistant_pb2
import voice_assistant_pb2_grpc

class VoiceAssistantClient:
    """
    Client for the Voice Assistant gRPC service
    """
    
    def __init__(self, server_address='localhost:50051'):
        self.server_address = server_address
        self.channel = grpc.insecure_channel(server_address)
        self.stub = voice_assistant_pb2_grpc.VoiceAssistantStub(self.channel)
        
    def close(self):
        """Close the gRPC channel"""
        self.channel.close()
    
    def create_sample_audio(self, text_content: str = "Hello, how are you today?") -> bytes:
        """
        Create a sample WAV audio file for testing
        In a real implementation, this would be actual recorded audio
        """
        # Create a simple sine wave as placeholder audio
        import numpy as np
        
        sample_rate = 16000
        duration = 2.0  # 2 seconds
        frequency = 440  # A4 note
        
        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Convert to 16-bit PCM
        audio_16bit = (audio_data * 32767).astype(np.int16)
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_16bit.tobytes())
        
        wav_buffer.seek(0)
        return wav_buffer.read()
    
    def process_voice_request(self, audio_data: bytes, user_id: str = None, session_id: str = None) -> voice_assistant_pb2.AudioResponse:
        """
        Send a single voice processing request
        """
        if not user_id:
            user_id = "test_user"
        if not session_id:
            session_id = str(uuid.uuid4())
        
        request = voice_assistant_pb2.AudioRequest(
            audio_data=audio_data,
            session_id=session_id,
            format=voice_assistant_pb2.AudioFormat.WAV,
            sample_rate=16000,
            user_id=user_id
        )
        
        try:
            print(f"Sending voice request for session: {session_id}")
            response = self.stub.ProcessVoice(request)
            return response
        except grpc.RpcError as e:
            print(f"gRPC error: {e.code()} - {e.details()}")
            return None
    
    def stream_voice_chunks(self, audio_data: bytes, session_id: str = None, chunk_size: int = 4096) -> Generator:
        """
        Create audio chunks for streaming
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Split audio into chunks
        for i in range(0, len(audio_data), chunk_size):
            chunk_data = audio_data[i:i + chunk_size]
            is_final = (i + chunk_size) >= len(audio_data)
            
            yield voice_assistant_pb2.AudioChunk(
                chunk_data=chunk_data,
                session_id=session_id,
                is_final=is_final,
                sequence_number=i // chunk_size
            )
    
    def stream_voice_request(self, audio_data: bytes, session_id: str = None):
        """
        Send a streaming voice request
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        print(f"Starting voice stream for session: {session_id}")
        
        try:
            # Create request generator
            requests = self.stream_voice_chunks(audio_data, session_id)
            
            # Send streaming request and get responses
            responses = self.stub.StreamVoice(requests)
            
            # Collect response chunks
            response_audio = io.BytesIO()
            for response_chunk in responses:
                if response_chunk.sequence_number == -1:
                    print("Error in streaming response")
                    return None
                
                response_audio.write(response_chunk.chunk_data)
                
                if response_chunk.is_final:
                    print("Streaming response completed")
                    break
            
            response_audio.seek(0)
            return response_audio.read()
            
        except grpc.RpcError as e:
            print(f"gRPC streaming error: {e.code()} - {e.details()}")
            return None
    
    def get_conversation_history(self, user_id: str = None, session_id: str = None, limit: int = 10):
        """
        Get conversation history
        """
        request = voice_assistant_pb2.HistoryRequest(
            user_id=user_id or "test_user",
            session_id=session_id or "",
            limit=limit
        )
        
        try:
            print("Fetching conversation history...")
            response = self.stub.GetConversationHistory(request)
            return response.records
        except grpc.RpcError as e:
            print(f"gRPC error getting history: {e.code()} - {e.details()}")
            return []
    
    def save_audio_to_file(self, audio_data: bytes, filename: str):
        """
        Save audio data to a WAV file
        """
        with open(filename, 'wb') as f:
            f.write(audio_data)
        print(f"Audio saved to {filename}")


def main():
    """
    Main demonstration of the Voice Assistant client
    """
    print("🎤 Voice Assistant gRPC Client Demo")
    print("=" * 50)
    
    # Create client
    client = VoiceAssistantClient()
    
    try:
        # Test 1: Single voice request
        print("\n📞 Test 1: Single Voice Request")
        print("-" * 30)
        
        # Create sample audio
        sample_audio = client.create_sample_audio("Hello, this is a test message")
        
        # Process the request
        response = client.process_voice_request(
            audio_data=sample_audio,
            user_id="demo_user",
            session_id="demo_session_1"
        )
        
        if response and response.success:
            print(f"✅ Success!")
            print(f"📝 Transcribed: {response.transcribed_text}")
            print(f"🤖 Response: {response.text_response}")
            print(f"🔊 Audio response length: {len(response.audio_data)} bytes")
            
            # Save response audio
            if response.audio_data:
                client.save_audio_to_file(response.audio_data, "response_audio.wav")
        else:
            print(f"❌ Failed: {response.error_message if response else 'No response'}")
        
        # Test 2: Streaming voice request
        print("\n📡 Test 2: Streaming Voice Request")
        print("-" * 30)
        
        # Create another sample audio
        sample_audio_2 = client.create_sample_audio("This is a streaming test message")
        
        # Process streaming request
        streaming_response = client.stream_voice_request(
            audio_data=sample_audio_2,
            session_id="demo_session_2"
        )
        
        if streaming_response:
            print(f"✅ Streaming success!")
            print(f"🔊 Streaming response length: {len(streaming_response)} bytes")
            client.save_audio_to_file(streaming_response, "streaming_response_audio.wav")
        else:
            print("❌ Streaming failed")
        
        # Test 3: Get conversation history
        print("\n📚 Test 3: Conversation History")
        print("-" * 30)
        
        history = client.get_conversation_history(
            user_id="demo_user",
            limit=5
        )
        
        if history:
            print(f"✅ Found {len(history)} conversation records:")
            for i, record in enumerate(history, 1):
                print(f"  {i}. Session: {record.session_id}")
                print(f"     Input: {record.text_input}")
                print(f"     Response: {record.text_response}")
                print(f"     Timestamp: {record.timestamp}")
                print()
        else:
            print("📭 No conversation history found")
        
        # Test 4: Multiple requests in same session
        print("\n🔄 Test 4: Multiple Requests (Same Session)")
        print("-" * 30)
        
        session_id = "demo_session_continuous"
        
        for i in range(3):
            print(f"Request {i+1}/3...")
            test_audio = client.create_sample_audio(f"This is message number {i+1}")
            
            response = client.process_voice_request(
                audio_data=test_audio,
                user_id="demo_user",
                session_id=session_id
            )
            
            if response and response.success:
                print(f"  ✅ Transcribed: {response.transcribed_text}")
                print(f"  🤖 Response: {response.text_response}")
            else:
                print(f"  ❌ Failed: {response.error_message if response else 'No response'}")
            
            time.sleep(1)  # Brief pause between requests
        
        print("\n🎉 Demo completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Clean up
        client.close()
        print("🔌 Client connection closed")


if __name__ == "__main__":
    main()