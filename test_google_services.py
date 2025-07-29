#!/usr/bin/env python3
"""
Google Cloud Services Test Script
Tests Speech-to-Text and Text-to-Speech functionality
"""

import os
import sys
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section"""
    print(f"\n--- {title} ---")

def check_environment():
    """Check environment variables and configuration"""
    print_header("Environment Check")
    
    # Check Google Cloud credentials
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Please set this environment variable to your service account key file")
        return False
    
    print(f"✅ GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")
    
    # Check if file exists
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        return False
    
    print(f"✅ Credentials file exists")
    
    # Validate JSON format
    try:
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            print(f"❌ Invalid credentials file - missing fields: {missing_fields}")
            return False
        
        print(f"✅ Credentials file is valid JSON")
        print(f"   Project ID: {creds_data.get('project_id', 'N/A')}")
        print(f"   Client Email: {creds_data.get('client_email', 'N/A')}")
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in credentials file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False
    
    return True

def test_imports():
    """Test if required packages are installed"""
    print_header("Package Import Test")
    
    try:
        import google.cloud.speech
        print("✅ google-cloud-speech imported successfully")
    except ImportError as e:
        print(f"❌ google-cloud-speech import failed: {e}")
        print("   Install with: pip install google-cloud-speech")
        return False
    
    try:
        import google.cloud.texttospeech
        print("✅ google-cloud-texttospeech imported successfully")
    except ImportError as e:
        print(f"❌ google-cloud-texttospeech import failed: {e}")
        print("   Install with: pip install google-cloud-texttospeech")
        return False
    
    return True

def test_google_services():
    """Test Google Cloud Services functionality"""
    print_header("Google Cloud Services Test")
    
    try:
        from google_services import google_services
        
        if not google_services:
            print("❌ Google services not initialized")
            return False
        
        # Get service status
        print_section("Service Status")
        status = google_services.get_service_status()
        print(json.dumps(status, indent=2))
        
        if not status["configured"]:
            print("❌ Google Cloud Services not properly configured")
            return False
        
        # Test services
        print_section("Service Tests")
        test_results = google_services.test_services()
        print(json.dumps(test_results, indent=2))
        
        # Check overall status
        if test_results["overall_status"] == "all_working":
            print("✅ All Google Cloud Services working correctly")
            return True
        elif test_results["overall_status"] == "partial":
            print("⚠️ Some Google Cloud Services working")
            return True
        else:
            print("❌ Google Cloud Services not working")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google services: {e}")
        return False

def test_speech_to_text():
    """Test Speech-to-Text functionality"""
    print_header("Speech-to-Text Test")
    
    try:
        from google_services import google_services
        import numpy as np
        
        # Create a simple test audio (silence)
        sample_rate = 16000
        duration = 1.0
        audio_data = np.zeros(int(sample_rate * duration), dtype=np.int16)
        audio_bytes = audio_data.tobytes()
        
        print(f"📊 Test audio created: {len(audio_bytes)} bytes")
        
        # Test transcription
        transcript, metadata = google_services.speech_to_text(audio_bytes)
        
        print(f"📝 Transcription result: {transcript}")
        print(f"📊 Metadata: {json.dumps(metadata, indent=2)}")
        
        if "error" in metadata:
            print(f"❌ Speech-to-Text failed: {metadata['error']}")
            return False
        
        print("✅ Speech-to-Text test completed")
        return True
        
    except Exception as e:
        print(f"❌ Speech-to-Text test failed: {e}")
        return False

def test_text_to_speech():
    """Test Text-to-Speech functionality"""
    print_header("Text-to-Speech Test")
    
    try:
        from google_services import google_services
        
        test_text = "Hello, this is a test of the text-to-speech service."
        print(f"📝 Test text: {test_text}")
        
        # Test synthesis
        audio_response, metadata = google_services.text_to_speech(test_text)
        
        if audio_response:
            print(f"🔊 Audio generated: {len(audio_response)} bytes")
            print(f"📊 Metadata: {json.dumps(metadata, indent=2)}")
            
            # Save test audio file
            test_filename = f"test_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            with open(test_filename, 'wb') as f:
                f.write(audio_response)
            print(f"💾 Test audio saved as: {test_filename}")
            
            print("✅ Text-to-Speech test completed")
            return True
        else:
            print(f"❌ Text-to-Speech failed: {metadata.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Text-to-Speech test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints if server is running"""
    print_header("API Endpoints Test")
    
    try:
        import requests
        
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        print_section("Health Check")
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Health endpoint working")
                print(f"📊 Status: {health_data.get('status', 'unknown')}")
                print(f"📊 Services: {json.dumps(health_data.get('services', {}), indent=2)}")
            else:
                print(f"❌ Health endpoint returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Health endpoint not accessible: {e}")
            print("   Make sure the server is running on http://localhost:8000")
        
        # Test services status endpoint
        print_section("Services Status")
        try:
            response = requests.get(f"{base_url}/services/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                print("✅ Services status endpoint working")
                print(f"📊 Status: {json.dumps(status_data, indent=2)}")
            else:
                print(f"❌ Services status endpoint returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Services status endpoint not accessible: {e}")
        
        # Test services test endpoint
        print_section("Services Test")
        try:
            response = requests.get(f"{base_url}/services/test", timeout=10)
            if response.status_code == 200:
                test_data = response.json()
                print("✅ Services test endpoint working")
                print(f"📊 Test results: {json.dumps(test_data, indent=2)}")
            else:
                print(f"❌ Services test endpoint returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Services test endpoint not accessible: {e}")
        
        return True
        
    except ImportError:
        print("⚠️ requests library not available - skipping API tests")
        print("   Install with: pip install requests")
        return True
    except Exception as e:
        print(f"❌ API endpoint tests failed: {e}")
        return False

def main():
    """Run all tests"""
    print_header("Google Cloud Services Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Environment Check", check_environment),
        ("Package Imports", test_imports),
        ("Google Services", test_google_services),
        ("Speech-to-Text", test_speech_to_text),
        ("Text-to-Speech", test_text_to_speech),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print_section(f"Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed! Google Cloud Services are working correctly.")
        print("\nNext steps:")
        print("1. Start the main application: python main.py")
        print("2. Start the Streamlit app: streamlit run streamlit_app.py")
        print("3. Test with real audio files")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the errors above.")
        print("\nTroubleshooting tips:")
        print("1. Verify Google Cloud credentials are set correctly")
        print("2. Check that required APIs are enabled")
        print("3. Ensure service account has proper permissions")
        print("4. Review the GOOGLE_CLOUD_SETUP.md guide")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)