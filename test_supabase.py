#!/usr/bin/env python3
"""
Test script for Supabase integration
Run this to verify that the Supabase connection and operations work correctly
"""

import uuid
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_supabase_connection():
    """Test the Supabase connection and basic operations"""
    print("🧪 Testing Supabase Integration...")
    
    try:
        from supabase_client import supabase_client
        from models import conversation_service, session_service
        
        print("✅ Successfully imported Supabase client and services")
        
        # Test connection
        print("\n📡 Testing connection...")
        if supabase_client.test_connection():
            print("✅ Supabase connection successful")
        else:
            print("❌ Supabase connection failed")
            return False
        
        # Test session creation
        print("\n👤 Testing session creation...")
        test_session_id = str(uuid.uuid4())
        test_user_id = "test_user_" + str(uuid.uuid4())[:8]
        
        session_result = session_service.create_user_session(test_session_id, test_user_id)
        if session_result:
            print(f"✅ Session created: {session_result['session_id']}")
        else:
            print("❌ Failed to create session")
            return False
        
        # Test conversation record creation
        print("\n💬 Testing conversation record creation...")
        test_record = conversation_service.create_conversation_record(
            user_id=test_user_id,
            session_id=test_session_id,
            audio_input=b"test audio data",
            text_input="Hello, this is a test message",
            text_response="This is a test response from the assistant",
            audio_response=b"test response audio data"
        )
        
        if test_record:
            print(f"✅ Conversation record created: {test_record['id']}")
            record_id = test_record['id']
        else:
            print("❌ Failed to create conversation record")
            return False
        
        # Test retrieving conversation record
        print("\n📖 Testing conversation record retrieval...")
        retrieved_record = conversation_service.get_conversation_record(record_id)
        if retrieved_record:
            print(f"✅ Retrieved record: {retrieved_record['text_input']}")
        else:
            print("❌ Failed to retrieve conversation record")
            return False
        
        # Test conversation history
        print("\n📚 Testing conversation history...")
        history = conversation_service.get_conversation_history(test_user_id, limit=10)
        if history:
            print(f"✅ Retrieved {len(history)} conversation(s) from history")
        else:
            print("⚠️ No conversation history found (this might be expected)")
        
        # Test session retrieval
        print("\n🔍 Testing session retrieval...")
        retrieved_session = session_service.get_user_session(test_session_id)
        if retrieved_session:
            print(f"✅ Retrieved session: {retrieved_session['user_id']}")
        else:
            print("❌ Failed to retrieve session")
            return False
        
        # Test session activity update
        print("\n⏰ Testing session activity update...")
        updated_session = session_service.update_session_activity(test_session_id)
        if updated_session:
            print(f"✅ Updated session activity: {updated_session['last_activity']}")
        else:
            print("❌ Failed to update session activity")
            return False
        
        print("\n🎉 All tests passed! Supabase integration is working correctly.")
        print(f"\n📊 Test Summary:")
        print(f"   - User ID: {test_user_id}")
        print(f"   - Session ID: {test_session_id}")
        print(f"   - Record ID: {record_id}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed the supabase package: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
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
    print("🚀 Voice Assistant Supabase Integration Test")
    print("=" * 50)
    
    # Test environment first
    if not test_environment():
        print("\n❌ Environment test failed. Please check your .env file.")
        sys.exit(1)
    
    # Test Supabase integration
    if test_supabase_connection():
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)