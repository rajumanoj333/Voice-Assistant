#!/usr/bin/env python3
"""
Script to generate gRPC Python code from protobuf definitions
"""

import subprocess
import sys
import os

def generate_grpc_code():
    """Generate gRPC code from proto file"""
    try:
        # Run protoc command to generate Python code
        cmd = [
            sys.executable, "-m", "grpc_tools.protoc",
            "--proto_path=.",
            "--python_out=.",
            "--grpc_python_out=.",
            "voice_assistant.proto"
        ]
        
        print("Generating gRPC code...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ gRPC code generated successfully!")
            print("Generated files:")
            print("  - voice_assistant_pb2.py")
            print("  - voice_assistant_pb2_grpc.py")
        else:
            print("❌ Error generating gRPC code:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = generate_grpc_code()
    sys.exit(0 if success else 1)
