#!/usr/bin/env python3
"""
Setup script for Voice Assistant system
Automates initial setup and verification
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def generate_grpc_code():
    """Generate gRPC Python code from protobuf"""
    print("\n🔧 Generating gRPC code...")
    try:
        subprocess.check_call([sys.executable, "generate_grpc.py"])
        print("✅ gRPC code generated successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to generate gRPC code")
        return False

def check_environment_file():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("⚠️  .env file not found. Creating from template...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("📝 Please edit .env file with your actual values")
            return False
        else:
            print("❌ .env.example not found")
            return False
    
    load_dotenv()
    
    required_vars = [
        'OPENAI_API_KEY',
        'DATABASE_URL',
        'GOOGLE_APPLICATION_CREDENTIALS'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith('your_'):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or incomplete environment variables: {', '.join(missing_vars)}")
        print("📝 Please update your .env file with actual values")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def check_google_credentials():
    """Verify Google Cloud credentials"""
    print("\n🔐 Checking Google Cloud credentials...")
    
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.exists(creds_path):
        print("⚠️  Google Cloud credentials file not found")
        print("Please ensure GOOGLE_APPLICATION_CREDENTIALS points to a valid JSON file")
        return False
    
    print("✅ Google Cloud credentials file found")
    return True

def test_database_connection():
    """Test database connection and create tables"""
    print("\n🗄️  Testing database connection...")
    
    try:
        from models import create_tables, engine
        from sqlalchemy import text
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Create tables
        create_tables()
        print("✅ Database connection successful and tables created")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your DATABASE_URL and ensure PostgreSQL is running")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🤖 Testing OpenAI API connection...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ OpenAI API connection successful")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        print("Please check your OPENAI_API_KEY")
        return False

def test_google_cloud_services():
    """Test Google Cloud STT and TTS services"""
    print("\n☁️  Testing Google Cloud services...")
    
    try:
        from google.cloud import speech
        from google.cloud import texttospeech
        
        # Test STT client
        speech_client = speech.SpeechClient()
        print("✅ Google Cloud Speech-to-Text client initialized")
        
        # Test TTS client
        tts_client = texttospeech.TextToSpeechClient()
        print("✅ Google Cloud Text-to-Speech client initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Cloud services initialization failed: {e}")
        print("Please check your Google Cloud credentials and API enablement")
        return False

def run_basic_test():
    """Run a basic system test"""
    print("\n🧪 Running basic system test...")
    
    try:
        # Test VAD processor
        from vad_processor import vad_processor
        print("✅ SileroVAD processor loaded")
        
        # Test other components
        from google_services import google_services
        print("✅ Google services loaded")
        
        from llm_processor import llm_processor
        print("✅ LLM processor loaded")
        
        print("✅ All components loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Component loading failed: {e}")
        return False

def main():
    """Main setup process"""
    print("🎤 Voice Assistant Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Generate gRPC code
    if not generate_grpc_code():
        return False
    
    # Check environment configuration
    env_ok = check_environment_file()
    
    if env_ok:
        # Test database connection
        db_ok = test_database_connection()
        
        # Test OpenAI connection
        openai_ok = test_openai_connection()
        
        # Check Google credentials
        google_creds_ok = check_google_credentials()
        
        # Test Google Cloud services
        google_services_ok = test_google_cloud_services() if google_creds_ok else False
        
        # Run basic component test
        components_ok = run_basic_test()
        
        # Summary
        print("\n📋 Setup Summary")
        print("-" * 30)
        print(f"Environment Config: {'✅' if env_ok else '❌'}")
        print(f"Database: {'✅' if db_ok else '❌'}")
        print(f"OpenAI API: {'✅' if openai_ok else '❌'}")
        print(f"Google Credentials: {'✅' if google_creds_ok else '❌'}")
        print(f"Google Services: {'✅' if google_services_ok else '❌'}")
        print(f"Components: {'✅' if components_ok else '❌'}")
        
        if all([env_ok, db_ok, openai_ok, google_creds_ok, google_services_ok, components_ok]):
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Start the gRPC server: python grpc_server.py")
            print("2. Run the client example: python client_example.py")
            print("3. Or start the FastAPI server: python main.py")
            return True
        else:
            print("\n⚠️  Setup completed with issues. Please resolve the failed items above.")
            return False
    else:
        print("\n📝 Please configure your .env file and run setup again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)