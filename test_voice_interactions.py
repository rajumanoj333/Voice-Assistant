#!/usr/bin/env python3
"""
Test script for voice_interactions table functionality
Demonstrates how to create, read, update, and delete voice interactions
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_voice_interactions():
    """Test voice interactions functionality"""
    
    print("🧪 Testing Voice Interactions Functionality")
    print("=" * 50)
    
    try:
        from models import voice_interaction_service
        from supabase_client import supabase_client
        
        # Test connection
        if not supabase_client.test_connection():
            print("❌ Cannot connect to Supabase. Please check your credentials.")
            return False
        
        print("✅ Connected to Supabase successfully")
        
        # Test creating a voice interaction
        print("\n📝 Creating a test voice interaction...")
        test_interaction = voice_interaction_service.create_voice_interaction(
            audio_file_url="https://supabase.com/storage/v1/object/public/audio/test_audio.wav",
            transcript="Hello, this is a test transcript",
            llm_response="This is a test LLM response to the voice input."
        )
        
        if test_interaction:
            print("✅ Voice interaction created successfully")
            interaction_id = test_interaction['id']
            print(f"   ID: {interaction_id}")
            print(f"   Audio URL: {test_interaction['audio_file_url']}")
            print(f"   Transcript: {test_interaction['transcript']}")
            print(f"   LLM Response: {test_interaction['llm_response']}")
            print(f"   Created At: {test_interaction['created_at']}")
        else:
            print("❌ Failed to create voice interaction")
            return False
        
        # Test retrieving the voice interaction
        print("\n🔍 Retrieving the voice interaction...")
        retrieved_interaction = voice_interaction_service.get_voice_interaction(interaction_id)
        
        if retrieved_interaction:
            print("✅ Voice interaction retrieved successfully")
            print(f"   ID: {retrieved_interaction['id']}")
            print(f"   Audio URL: {retrieved_interaction['audio_file_url']}")
            print(f"   Transcript: {retrieved_interaction['transcript']}")
            print(f"   LLM Response: {retrieved_interaction['llm_response']}")
        else:
            print("❌ Failed to retrieve voice interaction")
            return False
        
        # Test updating the voice interaction
        print("\n✏️  Updating the voice interaction...")
        updated_interaction = voice_interaction_service.update_voice_interaction(
            interaction_id,
            {
                'transcript': 'Updated transcript with more details',
                'llm_response': 'Updated LLM response with additional information.'
            }
        )
        
        if updated_interaction:
            print("✅ Voice interaction updated successfully")
            print(f"   Updated Transcript: {updated_interaction['transcript']}")
            print(f"   Updated LLM Response: {updated_interaction['llm_response']}")
        else:
            print("❌ Failed to update voice interaction")
            return False
        
        # Test getting all voice interactions
        print("\n📋 Getting all voice interactions...")
        all_interactions = voice_interaction_service.get_voice_interactions(limit=10)
        
        if all_interactions:
            print(f"✅ Retrieved {len(all_interactions)} voice interactions")
            for i, interaction in enumerate(all_interactions[:3], 1):  # Show first 3
                print(f"   {i}. ID: {interaction['id']}")
                print(f"      Transcript: {interaction['transcript'][:50]}...")
                print(f"      Created: {interaction['created_at']}")
        else:
            print("✅ No voice interactions found (or empty list returned)")
        
        # Test deleting the voice interaction
        print(f"\n🗑️  Deleting the test voice interaction...")
        if voice_interaction_service.delete_voice_interaction(interaction_id):
            print("✅ Voice interaction deleted successfully")
        else:
            print("❌ Failed to delete voice interaction")
            return False
        
        print("\n🎉 All voice interaction tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def show_usage_examples():
    """Show usage examples for voice interactions"""
    
    print("\n📚 Voice Interactions Usage Examples")
    print("=" * 50)
    
    print("\n1. Creating a voice interaction:")
    print("""
    from models import voice_interaction_service
    
    # Create a new voice interaction
    interaction = voice_interaction_service.create_voice_interaction(
        audio_file_url="https://supabase.com/storage/v1/object/public/audio/recording.wav",
        transcript="User said: Hello, how are you?",
        llm_response="I'm doing well, thank you for asking! How can I help you today?"
    )
    """)
    
    print("\n2. Retrieving a voice interaction:")
    print("""
    # Get a specific interaction by ID
    interaction = voice_interaction_service.get_voice_interaction("interaction-id-here")
    if interaction:
        print(f"Transcript: {interaction['transcript']}")
        print(f"LLM Response: {interaction['llm_response']}")
    """)
    
    print("\n3. Getting all voice interactions:")
    print("""
    # Get all interactions with pagination
    interactions = voice_interaction_service.get_voice_interactions(limit=20, offset=0)
    for interaction in interactions:
        print(f"ID: {interaction['id']}")
        print(f"Transcript: {interaction['transcript']}")
        print(f"Created: {interaction['created_at']}")
    """)
    
    print("\n4. Updating a voice interaction:")
    print("""
    # Update specific fields
    updated = voice_interaction_service.update_voice_interaction(
        "interaction-id-here",
        {
            'transcript': 'Updated transcript text',
            'llm_response': 'Updated response text'
        }
    )
    """)
    
    print("\n5. Deleting a voice interaction:")
    print("""
    # Delete an interaction
    success = voice_interaction_service.delete_voice_interaction("interaction-id-here")
    if success:
        print("Interaction deleted successfully")
    """)

def main():
    """Main function"""
    print("🚀 Voice Interactions Test Suite")
    print("=" * 50)
    
    # Run tests
    success = test_voice_interactions()
    
    if success:
        print("\n✅ All tests completed successfully!")
        show_usage_examples()
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure Supabase credentials are set in .env file")
        print("   2. Ensure the voice_interactions table exists in your Supabase database")
        print("   3. Run the schema setup: python3 setup_supabase_schema.py")
        print("   4. Check your internet connection")

if __name__ == "__main__":
    main()