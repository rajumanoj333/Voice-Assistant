#!/usr/bin/env python3
"""
Test script for Supabase integration (Simple Log Table)
Run this to verify that the Supabase connection and operations work correctly
"""
import uuid
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_supabase_connection():
    print("🧪 Testing Supabase Integration (Simple Log Table)...")
    try:
        from supabase_client import supabase_client
        from models import conversation_log_service
        print("✅ Successfully imported Supabase client and log service")
        # Test connection
        print("\n📡 Testing connection...")
        if supabase_client.get_client():
            print("✅ Supabase connection successful")
        else:
            print("❌ Supabase connection failed")
            return False
        # Test conversation log creation
        print("\n💬 Testing conversation log creation...")
        test_log_id = str(uuid.uuid4())
        test_audio_type = "wav"
        test_audio_transcription = "Hello, this is a test transcription."
        test_llm_response = "This is a test LLM response."
        log_result = conversation_log_service.create_conversation_log(
            audio_type=test_audio_type,
            audio_transcription=test_audio_transcription,
            llm_response=test_llm_response
        )
        if log_result:
            print(f"✅ Conversation log created: {log_result['id']}")
            log_id = log_result['id']
        else:
            print("❌ Failed to create conversation log")
            return False
        # Test retrieving conversation log
        print("\n📖 Testing conversation log retrieval...")
        retrieved_log = conversation_log_service.get_conversation_log(log_id)
        if retrieved_log:
            print(f"✅ Retrieved log: {retrieved_log['audio_transcription']}")
        else:
            print("❌ Failed to retrieve conversation log")
            return False
        # Test listing logs
        print("\n📚 Testing conversation log listing...")
        logs = conversation_log_service.get_conversation_logs(limit=5)
        if logs:
            print(f"✅ Retrieved {len(logs)} log(s) from listing")
        else:
            print("⚠️ No logs found (this might be expected if database is empty)")
        print("\n🎉 All tests passed! Supabase integration is working correctly.")
        print(f"\n📊 Test Summary:")
        print(f"   - Log ID: {log_id}")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed the supabase package: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_environment():
    print("\n🔧 Testing environment configuration...")
    from dotenv import load_dotenv
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    if supabase_url:
        print(f"✅ SUPABASE_URL is set: {supabase_url}")
    else:
        print("❌ SUPABASE_URL is not set in environment")
        return False
    if supabase_key:
        print(f"✅ SUPABASE_KEY is set: {supabase_key[:20]}...")
    else:
        print("❌ SUPABASE_KEY is not set in environment")
        return False
    return True

if __name__ == "__main__":
    print("🚀 Voice Assistant Supabase Integration Test (Simple Log Table)")
    print("=" * 50)
    if not test_environment():
        print("\n❌ Environment test failed. Please check your .env file.")
        sys.exit(1)
    if test_supabase_connection():
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)