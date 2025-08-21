#!/usr/bin/env python3
"""
Example script demonstrating how to use the voice_interactions table
in a real voice assistant application scenario
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def simulate_voice_interaction():
    """Simulate a complete voice interaction workflow"""
    
    print("🎤 Voice Interaction Workflow Example")
    print("=" * 50)
    
    try:
        from models import voice_interaction_service
        from supabase_client import supabase_client
        
        # Test connection
        if not supabase_client.test_connection():
            print("❌ Cannot connect to Supabase. Please check your credentials.")
            return False
        
        print("✅ Connected to Supabase successfully")
        
        # Simulate audio file upload to Supabase Storage
        audio_file_name = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        audio_file_url = f"https://supabase.com/storage/v1/object/public/audio/{audio_file_name}"
        
        print(f"\n📁 Simulating audio file upload...")
        print(f"   File: {audio_file_name}")
        print(f"   URL: {audio_file_url}")
        
        # Simulate speech-to-text transcription
        user_transcript = "Hello, I need help with my project. Can you explain how to use the voice interactions table?"
        
        print(f"\n🎯 Simulating speech-to-text...")
        print(f"   Transcript: {user_transcript}")
        
        # Simulate LLM response generation
        llm_response = """I'd be happy to help you with the voice interactions table! 

The voice_interactions table is designed to store:
- Audio file URLs (pointing to files in Supabase Storage)
- Transcripts of the user's speech
- LLM responses to the user's queries
- Timestamps for when the interaction occurred

To use it in your application:
1. Upload audio files to Supabase Storage
2. Transcribe the audio using a speech-to-text service
3. Process the transcript with your LLM
4. Store the interaction using voice_interaction_service.create_voice_interaction()

This creates a complete record of each voice interaction for analysis and improvement."""
        
        print(f"\n🤖 Simulating LLM response generation...")
        print(f"   Response: {llm_response[:100]}...")
        
        # Store the voice interaction
        print(f"\n💾 Storing voice interaction in database...")
        interaction = voice_interaction_service.create_voice_interaction(
            audio_file_url=audio_file_url,
            transcript=user_transcript,
            llm_response=llm_response
        )
        
        if interaction:
            print("✅ Voice interaction stored successfully!")
            print(f"   Interaction ID: {interaction['id']}")
            print(f"   Created At: {interaction['created_at']}")
            
            # Demonstrate retrieving the interaction
            print(f"\n🔍 Retrieving stored interaction...")
            retrieved = voice_interaction_service.get_voice_interaction(interaction['id'])
            
            if retrieved:
                print("✅ Interaction retrieved successfully!")
                print(f"   Audio URL: {retrieved['audio_file_url']}")
                print(f"   Transcript: {retrieved['transcript']}")
                print(f"   LLM Response: {retrieved['llm_response'][:100]}...")
            
            # Demonstrate getting all interactions
            print(f"\n📋 Getting all voice interactions...")
            all_interactions = voice_interaction_service.get_voice_interactions(limit=5)
            print(f"   Found {len(all_interactions)} interactions")
            
            # Clean up - delete the test interaction
            print(f"\n🧹 Cleaning up test interaction...")
            if voice_interaction_service.delete_voice_interaction(interaction['id']):
                print("✅ Test interaction deleted successfully")
            else:
                print("❌ Failed to delete test interaction")
            
            return True
        else:
            print("❌ Failed to store voice interaction")
            return False
            
    except Exception as e:
        print(f"❌ Error during voice interaction simulation: {e}")
        return False

def show_integration_examples():
    """Show how to integrate voice_interactions into the main application"""
    
    print("\n🔗 Integration Examples")
    print("=" * 50)
    
    print("\n1. Integration with main.py voice processing:")
    print("""
    # In your main voice processing function
    def process_voice_input(audio_data, user_id):
        # 1. Upload audio to Supabase Storage
        audio_url = upload_audio_to_storage(audio_data)
        
        # 2. Transcribe audio
        transcript = transcribe_audio(audio_data)
        
        # 3. Generate LLM response
        llm_response = generate_llm_response(transcript)
        
        # 4. Store interaction
        interaction = voice_interaction_service.create_voice_interaction(
            audio_file_url=audio_url,
            transcript=transcript,
            llm_response=llm_response
        )
        
        return interaction
    """)
    
    print("\n2. Integration with gRPC server:")
    print("""
    # In your gRPC service
    def ProcessVoice(self, request, context):
        # Process the voice request
        audio_url = upload_audio(request.audio_data)
        transcript = transcribe_audio(request.audio_data)
        response = generate_response(transcript)
        
        # Store the interaction
        voice_interaction_service.create_voice_interaction(
            audio_file_url=audio_url,
            transcript=transcript,
            llm_response=response
        )
        
        return VoiceResponse(audio_response=response_audio)
    """)
    
    print("\n3. Analytics and monitoring:")
    print("""
    # Get interaction statistics
    interactions = voice_interaction_service.get_voice_interactions(limit=100)
    
    # Analyze patterns
    total_interactions = len(interactions)
    avg_response_length = sum(len(i['llm_response']) for i in interactions) / total_interactions
    
    print(f"Total interactions: {total_interactions}")
    print(f"Average response length: {avg_response_length:.0f} characters")
    """)

def main():
    """Main function"""
    print("🚀 Voice Interactions Integration Example")
    print("=" * 50)
    
    # Run the simulation
    success = simulate_voice_interaction()
    
    if success:
        print("\n✅ Voice interaction workflow completed successfully!")
        show_integration_examples()
        
        print("\n💡 Next steps:")
        print("   1. Integrate voice_interaction_service into your main application")
        print("   2. Add audio file upload functionality to Supabase Storage")
        print("   3. Connect speech-to-text and LLM services")
        print("   4. Implement analytics and monitoring")
        print("   5. Add user authentication and authorization")
    else:
        print("\n❌ Voice interaction workflow failed.")
        print("Please check your Supabase connection and table setup.")

if __name__ == "__main__":
    main()