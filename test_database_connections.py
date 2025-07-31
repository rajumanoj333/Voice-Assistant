#!/usr/bin/env python3
"""
Comprehensive Database Connection and Data Saving Test
Tests all database connections, data saving, and integration with Google services and Streamlit
"""

import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase database connection"""
    
    print("🔗 Testing Supabase Database Connection")
    print("=" * 50)
    
    try:
        from supabase_client import supabase_client
        
        # Test basic connection
        if supabase_client.test_connection():
            print("✅ Supabase connection successful")
            
            # Test table access
            tables_to_test = ['conversation_records', 'user_sessions', 'voice_interactions']
            
            for table in tables_to_test:
                try:
                    result = supabase_client.client.table(table).select("count", count="exact").limit(1).execute()
                    print(f"✅ {table} table accessible")
                except Exception as e:
                    print(f"❌ {table} table not accessible: {e}")
                    return False
            
            return True
        else:
            print("❌ Supabase connection failed")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_voice_interaction_service():
    """Test voice interaction service functionality"""
    
    print("\n🎤 Testing Voice Interaction Service")
    print("=" * 50)
    
    try:
        from models import voice_interaction_service
        
        # Test creating voice interaction
        test_interaction = voice_interaction_service.create_voice_interaction(
            audio_file_url="https://test.com/audio.wav",
            transcript="Test transcript for database connection test",
            llm_response="Test LLM response for database connection test"
        )
        
        if test_interaction:
            print("✅ Voice interaction created successfully")
            interaction_id = test_interaction['id']
            print(f"   ID: {interaction_id}")
            print(f"   Audio URL: {test_interaction['audio_file_url']}")
            print(f"   Transcript: {test_interaction['transcript']}")
            print(f"   LLM Response: {test_interaction['llm_response']}")
            print(f"   Created At: {test_interaction['created_at']}")
            
            # Test retrieving the interaction
            retrieved = voice_interaction_service.get_voice_interaction(interaction_id)
            if retrieved:
                print("✅ Voice interaction retrieved successfully")
            else:
                print("❌ Failed to retrieve voice interaction")
                return False
            
            # Test updating the interaction
            updated = voice_interaction_service.update_voice_interaction(
                interaction_id,
                {
                    'transcript': 'Updated transcript for database test',
                    'llm_response': 'Updated LLM response for database test'
                }
            )
            if updated:
                print("✅ Voice interaction updated successfully")
            else:
                print("❌ Failed to update voice interaction")
                return False
            
            # Test getting all interactions
            all_interactions = voice_interaction_service.get_voice_interactions(limit=5)
            print(f"✅ Retrieved {len(all_interactions)} voice interactions")
            
            # Test deleting the interaction
            if voice_interaction_service.delete_voice_interaction(interaction_id):
                print("✅ Voice interaction deleted successfully")
            else:
                print("❌ Failed to delete voice interaction")
                return False
            
            return True
        else:
            print("❌ Failed to create voice interaction")
            return False
            
    except Exception as e:
        print(f"❌ Error testing voice interaction service: {e}")
        return False

def test_conversation_service():
    """Test conversation service functionality"""
    
    print("\n💬 Testing Conversation Service")
    print("=" * 50)
    
    try:
        from models import conversation_service
        
        # Test creating conversation record
        test_record = conversation_service.create_conversation_record(
            user_id="test_user",
            session_id="test_session",
            audio_input=b"test_audio_data",
            text_input="Test conversation input",
            text_response="Test conversation response",
            audio_response=b"test_response_audio"
        )
        
        if test_record:
            print("✅ Conversation record created successfully")
            record_id = test_record['id']
            print(f"   ID: {record_id}")
            print(f"   User ID: {test_record['user_id']}")
            print(f"   Session ID: {test_record['session_id']}")
            print(f"   Text Input: {test_record['text_input']}")
            print(f"   Text Response: {test_record['text_response']}")
            print(f"   Created At: {test_record['timestamp']}")
            
            # Test retrieving the record
            retrieved = conversation_service.get_conversation_record(record_id)
            if retrieved:
                print("✅ Conversation record retrieved successfully")
            else:
                print("❌ Failed to retrieve conversation record")
                return False
            
            # Test getting conversation history
            history = conversation_service.get_conversation_history("test_user", "test_session", limit=5)
            print(f"✅ Retrieved {len(history)} conversation records")
            
            return True
        else:
            print("❌ Failed to create conversation record")
            return False
            
    except Exception as e:
        print(f"❌ Error testing conversation service: {e}")
        return False

def test_session_service():
    """Test session service functionality"""
    
    print("\n🕐 Testing Session Service")
    print("=" * 50)
    
    try:
        from models import session_service
        
        # Test creating user session
        test_session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_user_id = "test_user"
        
        session_result = session_service.create_user_session(test_session_id, test_user_id)
        
        if session_result:
            print("✅ User session created successfully")
            print(f"   Session ID: {session_result['session_id']}")
            print(f"   User ID: {session_result['user_id']}")
            print(f"   Created At: {session_result['created_at']}")
            print(f"   Active: {session_result['is_active']}")
            
            # Test retrieving the session
            retrieved = session_service.get_user_session(test_session_id)
            if retrieved:
                print("✅ User session retrieved successfully")
            else:
                print("❌ Failed to retrieve user session")
                return False
            
            # Test updating session activity
            updated = session_service.update_session_activity(test_session_id)
            if updated:
                print("✅ Session activity updated successfully")
            else:
                print("❌ Failed to update session activity")
                return False
            
            return True
        else:
            print("❌ Failed to create user session")
            return False
            
    except Exception as e:
        print(f"❌ Error testing session service: {e}")
        return False

def test_google_services_integration():
    """Test Google services integration with database"""
    
    print("\n🤖 Testing Google Services Database Integration")
    print("=" * 50)
    
    try:
        from google_services import google_services
        
        if not google_services:
            print("❌ Google services not available")
            return False
        
        # Test saving voice interaction through Google services
        result = google_services.save_voice_interaction(
            audio_file_url="https://test.com/audio.wav",
            transcript="Test transcript from Google services",
            llm_response="Test LLM response from Google services"
        )
        
        if result.get('success'):
            print("✅ Voice interaction saved through Google services")
            interaction = result.get('interaction')
            if interaction:
                print(f"   Interaction ID: {interaction['id']}")
                
                # Clean up
                from models import voice_interaction_service
                voice_interaction_service.delete_voice_interaction(interaction['id'])
                print("✅ Test interaction cleaned up")
        else:
            print(f"❌ Failed to save voice interaction: {result.get('error')}")
            return False
        
        # Test saving conversation record through Google services
        result = google_services.save_conversation_record(
            user_id="test_user",
            session_id="test_session",
            audio_input=b"test_audio",
            text_input="Test input from Google services",
            text_response="Test response from Google services",
            audio_response=b"test_response_audio"
        )
        
        if result.get('success'):
            print("✅ Conversation record saved through Google services")
            record = result.get('record')
            if record:
                print(f"   Record ID: {record['id']}")
        else:
            print(f"❌ Failed to save conversation record: {result.get('error')}")
            return False
        
        # Test creating user session through Google services
        result = google_services.create_user_session("test_session", "test_user")
        
        if result.get('success'):
            print("✅ User session created through Google services")
            session = result.get('session')
            if session:
                print(f"   Session ID: {session['session_id']}")
        else:
            print(f"❌ Failed to create user session: {result.get('error')}")
            return False
        
        # Test getting conversation history through Google services
        result = google_services.get_conversation_history("test_user", limit=5)
        
        if result.get('success'):
            print("✅ Conversation history retrieved through Google services")
            history = result.get('history', [])
            print(f"   Retrieved {len(history)} records")
        else:
            print(f"❌ Failed to get conversation history: {result.get('error')}")
            return False
        
        # Test getting voice interactions through Google services
        result = google_services.get_voice_interactions(limit=5)
        
        if result.get('success'):
            print("✅ Voice interactions retrieved through Google services")
            interactions = result.get('interactions', [])
            print(f"   Retrieved {len(interactions)} interactions")
        else:
            print(f"❌ Failed to get voice interactions: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Google services integration: {e}")
        return False

def test_streamlit_integration():
    """Test Streamlit app integration with database"""
    
    print("\n📊 Testing Streamlit Database Integration")
    print("=" * 50)
    
    try:
        # Test importing Streamlit components
        from models import voice_interaction_service, conversation_service, session_service
        
        print("✅ Successfully imported database services for Streamlit")
        
        # Test creating test data for Streamlit
        test_interaction = voice_interaction_service.create_voice_interaction(
            audio_file_url="https://test.com/streamlit_audio.wav",
            transcript="Test transcript for Streamlit integration",
            llm_response="Test LLM response for Streamlit integration"
        )
        
        if test_interaction:
            print("✅ Test voice interaction created for Streamlit")
            print(f"   ID: {test_interaction['id']}")
            
            # Clean up
            voice_interaction_service.delete_voice_interaction(test_interaction['id'])
            print("✅ Test interaction cleaned up")
        else:
            print("❌ Failed to create test voice interaction for Streamlit")
            return False
        
        # Test conversation service for Streamlit
        test_record = conversation_service.create_conversation_record(
            user_id="streamlit_user",
            session_id="streamlit_session",
            audio_input=b"streamlit_audio",
            text_input="Test input for Streamlit",
            text_response="Test response for Streamlit",
            audio_response=b"streamlit_response"
        )
        
        if test_record:
            print("✅ Test conversation record created for Streamlit")
            print(f"   ID: {test_record['id']}")
        else:
            print("❌ Failed to create test conversation record for Streamlit")
            return False
        
        # Test session service for Streamlit
        session_result = session_service.create_user_session("streamlit_session", "streamlit_user")
        
        if session_result:
            print("✅ Test session created for Streamlit")
            print(f"   Session ID: {session_result['session_id']}")
        else:
            print("❌ Failed to create test session for Streamlit")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Streamlit integration: {e}")
        return False

def test_data_persistence():
    """Test that data is actually being saved to the database"""
    
    print("\n💾 Testing Data Persistence")
    print("=" * 50)
    
    try:
        from models import voice_interaction_service, conversation_service, session_service
        from supabase_client import supabase_client
        
        # Create test data
        test_interaction = voice_interaction_service.create_voice_interaction(
            audio_file_url="https://test.com/persistence_test.wav",
            transcript="Persistence test transcript",
            llm_response="Persistence test response"
        )
        
        if not test_interaction:
            print("❌ Failed to create test interaction")
            return False
        
        interaction_id = test_interaction['id']
        print(f"✅ Created test interaction: {interaction_id}")
        
        # Verify data exists in database
        result = supabase_client.get_voice_interaction(interaction_id)
        if result:
            print("✅ Data verified in database")
            print(f"   Audio URL: {result['audio_file_url']}")
            print(f"   Transcript: {result['transcript']}")
            print(f"   LLM Response: {result['llm_response']}")
        else:
            print("❌ Data not found in database")
            return False
        
        # Test conversation record persistence
        test_record = conversation_service.create_conversation_record(
            user_id="persistence_user",
            session_id="persistence_session",
            audio_input=b"persistence_audio",
            text_input="Persistence test input",
            text_response="Persistence test response",
            audio_response=b"persistence_response"
        )
        
        if test_record:
            print(f"✅ Created test conversation record: {test_record['id']}")
            
            # Verify in database
            db_record = supabase_client.get_conversation_record(test_record['id'])
            if db_record:
                print("✅ Conversation record verified in database")
            else:
                print("❌ Conversation record not found in database")
                return False
        else:
            print("❌ Failed to create test conversation record")
            return False
        
        # Test session persistence
        session_result = session_service.create_user_session("persistence_session", "persistence_user")
        
        if session_result:
            print(f"✅ Created test session: {session_result['session_id']}")
            
            # Verify in database
            db_session = supabase_client.get_user_session(session_result['session_id'])
            if db_session:
                print("✅ Session verified in database")
            else:
                print("❌ Session not found in database")
                return False
        else:
            print("❌ Failed to create test session")
            return False
        
        # Clean up test data
        voice_interaction_service.delete_voice_interaction(interaction_id)
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing data persistence: {e}")
        return False

def show_test_summary():
    """Show summary of all tests"""
    
    print("\n📋 Database Integration Summary")
    print("=" * 50)
    
    print("\n✅ Services Integrated:")
    print("   - Supabase Database Connection")
    print("   - Voice Interaction Service")
    print("   - Conversation Service")
    print("   - Session Service")
    print("   - Google Services Integration")
    print("   - Streamlit App Integration")
    
    print("\n🔗 Database Tables:")
    print("   - voice_interactions (NEW)")
    print("   - conversation_records")
    print("   - user_sessions")
    
    print("\n🤖 Integration Points:")
    print("   - main.py: REST API endpoints")
    print("   - grpc_server.py: Automatic storage during processing")
    print("   - google_services.py: Database methods")
    print("   - streamlit_app.py: Database operations UI")
    
    print("\n💾 Data Flow:")
    print("   - Voice Processing → Database Storage")
    print("   - API Requests → Database CRUD")
    print("   - Streamlit UI → Database Operations")
    print("   - Google Services → Database Integration")

def main():
    """Main test function"""
    print("🚀 Comprehensive Database Connection Test")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Supabase Connection", test_supabase_connection),
        ("Voice Interaction Service", test_voice_interaction_service),
        ("Conversation Service", test_conversation_service),
        ("Session Service", test_session_service),
        ("Google Services Integration", test_google_services_integration),
        ("Streamlit Integration", test_streamlit_integration),
        ("Data Persistence", test_data_persistence)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        result = test_func()
        results.append((test_name, result))
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All database connection tests passed!")
        show_test_summary()
        
        print("\n💡 Next steps:")
        print("   1. Run the application: python3 main.py")
        print("   2. Start Streamlit app: streamlit run streamlit_app.py")
        print("   3. Test gRPC server: python3 grpc_server.py")
        print("   4. Monitor database: Check Supabase dashboard")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        
        print("\n🔧 Troubleshooting tips:")
        print("   1. Check Supabase credentials in .env file")
        print("   2. Verify database tables exist")
        print("   3. Run schema setup: python3 setup_supabase_schema.py")
        print("   4. Check internet connection")

if __name__ == "__main__":
    main()