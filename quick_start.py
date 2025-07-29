#!/usr/bin/env python3
"""
Voice Assistant Quick Start Script
Helps users set up and test the Voice Assistant with Google Cloud services
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step_num, title):
    """Print a step header"""
    print(f"\n{step_num}. {title}")
    print("-" * 40)

def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python Version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("   Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print_step(2, "Installing Dependencies")
    
    try:
        print("Installing packages from requirements.txt...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print_step(3, "Checking Environment Configuration")
    
    # Load .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("⚠️ python-dotenv not available, loading .env manually")
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    else:
        print("⚠️ .env file not found")
        print("   Create a .env file with your configuration")
    
    # Check required environment variables
    required_vars = {
        'GOOGLE_APPLICATION_CREDENTIALS': 'Google Cloud credentials file path',
        'OPENAI_API_KEY': 'OpenAI API key (optional for testing)',
        'SUPABASE_URL': 'Supabase project URL (optional)',
        'SUPABASE_KEY': 'Supabase API key (optional)'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"⚠️ {var}: Not set - {description}")
            if var == 'GOOGLE_APPLICATION_CREDENTIALS':
                missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {missing_vars}")
        print("\nTo set up Google Cloud credentials:")
        print("1. Follow the guide in GOOGLE_CLOUD_SETUP.md")
        print("2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("3. Or add it to your .env file")
        return False
    
    return True

def run_tests():
    """Run the Google Cloud services test suite"""
    print_step(4, "Running Google Cloud Services Tests")
    
    try:
        result = subprocess.run([
            sys.executable, "test_google_services.py"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def start_services():
    """Start the Voice Assistant services"""
    print_step(5, "Starting Voice Assistant Services")
    
    print("Choose an option:")
    print("1. Start FastAPI server (main.py)")
    print("2. Start Streamlit app (streamlit_app.py)")
    print("3. Start both (in separate terminals)")
    print("4. Skip for now")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\nStarting FastAPI server...")
        print("Server will be available at: http://localhost:8000")
        print("API documentation at: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        
        try:
            subprocess.run([sys.executable, "main.py"])
        except KeyboardInterrupt:
            print("\nServer stopped")
    
    elif choice == "2":
        print("\nStarting Streamlit app...")
        print("App will be available at: http://localhost:8501")
        print("Press Ctrl+C to stop the app")
        
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
        except KeyboardInterrupt:
            print("\nApp stopped")
    
    elif choice == "3":
        print("\nTo start both services, run these commands in separate terminals:")
        print("Terminal 1: python main.py")
        print("Terminal 2: streamlit run streamlit_app.py")
        print("\nFastAPI server: http://localhost:8000")
        print("Streamlit app: http://localhost:8501")
    
    else:
        print("Skipping service startup")

def show_next_steps():
    """Show next steps for the user"""
    print_step(6, "Next Steps")
    
    print("🎉 Setup completed! Here's what you can do next:")
    
    print("\n📚 Documentation:")
    print("- Google Cloud Setup: GOOGLE_CLOUD_SETUP.md")
    print("- API Documentation: http://localhost:8000/docs (when server is running)")
    print("- Architecture: ARCHITECTURE.md")
    
    print("\n🚀 Start Services:")
    print("- FastAPI Server: python main.py")
    print("- Streamlit App: streamlit run streamlit_app.py")
    print("- Test Services: python test_google_services.py")
    
    print("\n🧪 Testing:")
    print("- Upload audio files via Streamlit")
    print("- Use the API endpoints directly")
    print("- Test with different audio formats")
    
    print("\n🔧 Configuration:")
    print("- Edit .env file for environment variables")
    print("- Modify google_services.py for voice settings")
    print("- Customize the UI in streamlit_app.py")
    
    print("\n📊 Monitoring:")
    print("- Check service status: http://localhost:8000/health")
    print("- View detailed status: http://localhost:8000/services/status")
    print("- Run service tests: http://localhost:8000/services/test")

def main():
    """Main quick start function"""
    print_header("Voice Assistant Quick Start")
    print("This script will help you set up and test the Voice Assistant")
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Environment Configuration", check_environment),
        ("Google Cloud Tests", run_tests),
    ]
    
    for i, (title, func) in enumerate(steps, 1):
        if not func():
            print(f"\n❌ Setup failed at step {i}: {title}")
            print("\nTroubleshooting:")
            print("1. Check the error messages above")
            print("2. Review GOOGLE_CLOUD_SETUP.md")
            print("3. Ensure all prerequisites are met")
            return False
    
    # Ask if user wants to start services
    start_services()
    
    # Show next steps
    show_next_steps()
    
    print("\n🎉 Quick start completed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)