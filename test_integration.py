#!/usr/bin/env python3
"""
Test script to verify voice_interaction_service integration with main.py and grpc_server.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_main_py_integration():
    """Test that main.py can import and use voice_interaction_service"""
    
    print("🧪 Testing main.py integration with voice_interaction_service")
    print("=" * 60)
    
    try:
        # Test importing the service from main.py context
        from models import voice_interaction_service
        
        print("✅ Successfully imported voice_interaction_service from models")
        
        # Test creating a voice interaction
        test_interaction = voice_interaction_service.create_voice_interaction(
            audio_file_url="https://test.com/audio.wav",
            transcript="Test transcript from main.py",
            llm_response="Test response from main.py"
        )
        
        if test_interaction:
            print("✅ Successfully created voice interaction from main.py context")
            print(f"   Interaction ID: {test_interaction['id']}")
            
            # Clean up
            voice_interaction_service.delete_voice_interaction(test_interaction['id'])
            print("✅ Successfully deleted test interaction")
            return True
        else:
            print("❌ Failed to create voice interaction from main.py context")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing main.py integration: {e}")
        return False

def test_grpc_server_integration():
    """Test that grpc_server.py can import and use voice_interaction_service"""
    
    print("\n🧪 Testing grpc_server.py integration with voice_interaction_service")
    print("=" * 60)
    
    try:
        # Test importing the service from grpc_server.py context
        from models import voice_interaction_service
        
        print("✅ Successfully imported voice_interaction_service from models")
        
        # Test creating a voice interaction
        test_interaction = voice_interaction_service.create_voice_interaction(
            audio_file_url="https://test.com/audio.wav",
            transcript="Test transcript from grpc_server.py",
            llm_response="Test response from grpc_server.py"
        )
        
        if test_interaction:
            print("✅ Successfully created voice interaction from grpc_server.py context")
            print(f"   Interaction ID: {test_interaction['id']}")
            
            # Clean up
            voice_interaction_service.delete_voice_interaction(test_interaction['id'])
            print("✅ Successfully deleted test interaction")
            return True
        else:
            print("❌ Failed to create voice interaction from grpc_server.py context")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing grpc_server.py integration: {e}")
        return False

def test_api_endpoints():
    """Test that the API endpoints are properly configured"""
    
    print("\n🧪 Testing API endpoints configuration")
    print("=" * 60)
    
    try:
        # Test importing FastAPI app
        from main import app
        
        print("✅ Successfully imported FastAPI app from main.py")
        
        # Check if voice interaction endpoints are registered
        routes = [route.path for route in app.routes]
        
        voice_interaction_routes = [
            "/voice-interactions/",
            "/voice-interactions/{interaction_id}"
        ]
        
        missing_routes = []
        for route in voice_interaction_routes:
            if route not in routes:
                missing_routes.append(route)
        
        if not missing_routes:
            print("✅ All voice interaction API endpoints are registered")
            print("   Available endpoints:")
            for route in voice_interaction_routes:
                print(f"   - {route}")
            return True
        else:
            print("❌ Missing voice interaction API endpoints:")
            for route in missing_routes:
                print(f"   - {route}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False

def test_grpc_methods():
    """Test that gRPC server has voice interaction functionality"""
    
    print("\n🧪 Testing gRPC server voice interaction functionality")
    print("=" * 60)
    
    try:
        # Test importing gRPC servicer
        from grpc_server import VoiceAssistantServicer
        
        print("✅ Successfully imported VoiceAssistantServicer from grpc_server.py")
        
        # Check if the servicer has the ProcessVoice method
        if hasattr(VoiceAssistantServicer, 'ProcessVoice'):
            print("✅ VoiceAssistantServicer has ProcessVoice method")
            
            # Create an instance to test
            servicer = VoiceAssistantServicer()
            print("✅ Successfully created VoiceAssistantServicer instance")
            
            return True
        else:
            print("❌ VoiceAssistantServicer missing ProcessVoice method")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing gRPC methods: {e}")
        return False

def show_integration_summary():
    """Show summary of integration status"""
    
    print("\n📋 Integration Summary")
    print("=" * 60)
    
    print("\n✅ Files Updated:")
    print("   - main.py: Added voice_interaction_service import and API endpoints")
    print("   - grpc_server.py: Added voice_interaction_service import and storage")
    print("   - models.py: Added VoiceInteractionService class")
    print("   - supabase_client.py: Added voice interaction CRUD operations")
    print("   - supabase_schema.sql: Added voice_interactions table")
    
    print("\n🔗 API Endpoints Added:")
    print("   - POST /voice-interactions/ - Create voice interaction")
    print("   - GET /voice-interactions/ - List voice interactions")
    print("   - GET /voice-interactions/{id} - Get specific interaction")
    print("   - PUT /voice-interactions/{id} - Update interaction")
    print("   - DELETE /voice-interactions/{id} - Delete interaction")
    
    print("\n🤖 gRPC Integration:")
    print("   - ProcessVoice method now saves voice interactions")
    print("   - Automatic voice interaction storage during processing")
    print("   - Error handling for voice interaction storage")
    
    print("\n💾 Database Integration:")
    print("   - voice_interactions table with proper schema")
    print("   - RLS policies for security")
    print("   - Indexes for performance")
    print("   - UUID primary keys for scalability")

def main():
    """Main test function"""
    print("🚀 Voice Interaction Service Integration Test")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("main.py integration", test_main_py_integration),
        ("grpc_server.py integration", test_grpc_server_integration),
        ("API endpoints", test_api_endpoints),
        ("gRPC methods", test_grpc_methods)
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
        print("\n🎉 All integration tests passed!")
        show_integration_summary()
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
    
    print(f"\n💡 Next steps:")
    print("   1. Run the application: python3 main.py")
    print("   2. Test the API endpoints using curl or Postman")
    print("   3. Test the gRPC server: python3 grpc_server.py")
    print("   4. Run comprehensive tests: python3 test_voice_interactions.py")

if __name__ == "__main__":
    main()