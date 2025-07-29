#!/usr/bin/env python3
"""
Voice Assistant Start Script
Convenient launcher for different components
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def start_grpc_server():
    """Start the gRPC server"""
    print("🚀 Starting gRPC Voice Assistant Server...")
    try:
        subprocess.run([sys.executable, "grpc_server.py"])
    except KeyboardInterrupt:
        print("\n⚠️  gRPC server stopped by user")
    except Exception as e:
        print(f"❌ Error starting gRPC server: {e}")

def start_fastapi_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI Server...")
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n⚠️  FastAPI server stopped by user")
    except Exception as e:
        print(f"❌ Error starting FastAPI server: {e}")

def run_client_demo():
    """Run the client demonstration"""
    print("🎤 Running Voice Assistant Client Demo...")
    try:
        subprocess.run([sys.executable, "client_example.py"])
    except Exception as e:
        print(f"❌ Error running client demo: {e}")

def run_setup():
    """Run the setup script"""
    print("⚙️  Running Voice Assistant Setup...")
    try:
        subprocess.run([sys.executable, "setup.py"])
    except Exception as e:
        print(f"❌ Error running setup: {e}")

def generate_grpc():
    """Generate gRPC code"""
    print("🔧 Generating gRPC code...")
    try:
        subprocess.run([sys.executable, "generate_grpc.py"])
        print("✅ gRPC code generated successfully")
    except Exception as e:
        print(f"❌ Error generating gRPC code: {e}")

def show_status():
    """Show system status"""
    print("📊 Voice Assistant System Status")
    print("=" * 40)
    
    # Check if required files exist
    required_files = [
        "voice_assistant.proto",
        "grpc_server.py",
        "client_example.py",
        "requirements.txt",
        ".env"
    ]
    
    print("\n📁 Required Files:")
    for file in required_files:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"  {exists} {file}")
    
    # Check if gRPC code is generated
    grpc_files = ["voice_assistant_pb2.py", "voice_assistant_pb2_grpc.py"]
    print("\n🔧 Generated gRPC Files:")
    for file in grpc_files:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"  {exists} {file}")
    
    # Check environment variables
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        
        print("\n🔐 Environment Variables:")
        env_vars = [
            "OPENAI_API_KEY",
            "DATABASE_URL", 
            "GOOGLE_APPLICATION_CREDENTIALS"
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value and not value.startswith('your_'):
                print(f"  ✅ {var}")
            else:
                print(f"  ❌ {var} (not set or using placeholder)")
    else:
        print("\n🔐 Environment Variables:")
        print("  ❌ .env file not found")

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Voice Assistant Start Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py --grpc          Start gRPC server
  python start.py --fastapi       Start FastAPI server
  python start.py --demo          Run client demo
  python start.py --setup         Run setup process
  python start.py --status        Show system status
        """
    )
    
    parser.add_argument('--grpc', action='store_true', 
                       help='Start the gRPC server')
    parser.add_argument('--fastapi', action='store_true',
                       help='Start the FastAPI server')
    parser.add_argument('--demo', action='store_true',
                       help='Run the client demonstration')
    parser.add_argument('--setup', action='store_true',
                       help='Run the setup process')
    parser.add_argument('--generate', action='store_true',
                       help='Generate gRPC code from protobuf')
    parser.add_argument('--status', action='store_true',
                       help='Show system status')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any(vars(args).values()):
        print("🎤 Voice Assistant System")
        print("=" * 30)
        print("\nAvailable commands:")
        print("  --setup     Run initial setup")
        print("  --grpc      Start gRPC server")
        print("  --fastapi   Start FastAPI server")
        print("  --demo      Run client demo")
        print("  --generate  Generate gRPC code")
        print("  --status    Show system status")
        print("\nFor more details: python start.py --help")
        return
    
    # Execute based on arguments
    if args.setup:
        run_setup()
    elif args.grpc:
        start_grpc_server()
    elif args.fastapi:
        start_fastapi_server()
    elif args.demo:
        run_client_demo()
    elif args.generate:
        generate_grpc()
    elif args.status:
        show_status()

if __name__ == "__main__":
    main()