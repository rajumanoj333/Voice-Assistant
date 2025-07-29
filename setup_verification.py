#!/usr/bin/env python3
"""
Comprehensive Setup Verification Script for Voice Assistant with Supabase
This script verifies all components are properly configured and working.
"""

import os
import sys
import subprocess
import importlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class SetupVerifier:
    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
        self.errors: List[str] = []
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log a test result"""
        status = "✅" if success else "❌"
        self.results.append((test_name, success, message))
        print(f"{status} {test_name}: {message}")
        if not success:
            self.errors.append(f"{test_name}: {message}")
    
    def check_python_version(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.log_result("Python Version", True, f"Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.log_result("Python Version", False, f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
            return False
    
    def check_dependencies(self) -> bool:
        """Check if all required packages are installed"""
        required_packages = [
            'fastapi', 'uvicorn', 'supabase', 'openai', 'python-dotenv',
            'sqlalchemy', 'psycopg2', 'numpy', 'torch', 'grpc',
            'google.cloud.speech', 'google.cloud.texttospeech'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                if '.' in package:
                    # Handle nested imports like google.cloud.speech
                    importlib.import_module(package)
                else:
                    # Handle special import names
                    if package == 'python-dotenv':
                        importlib.import_module('dotenv')
                    else:
                        importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        
        if not missing_packages:
            self.log_result("Dependencies", True, "All required packages installed")
            return True
        else:
            self.log_result("Dependencies", False, f"Missing packages: {', '.join(missing_packages)}")
            return False
    
    def check_environment_variables(self) -> bool:
        """Check environment variables"""
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = {
            'SUPABASE_URL': 'Supabase project URL',
            'SUPABASE_KEY': 'Supabase API key'
        }
        
        optional_vars = {
            'OPENAI_API_KEY': 'OpenAI API key (required for LLM)',
            'GOOGLE_APPLICATION_CREDENTIALS': 'Google Cloud credentials (required for speech services)'
        }
        
        all_good = True
        
        # Check required variables
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value:
                masked_value = value[:20] + "..." if len(value) > 20 else value
                self.log_result(f"Env Var: {var}", True, f"Set ({masked_value})")
            else:
                self.log_result(f"Env Var: {var}", False, f"Not set - {description}")
                all_good = False
        
        # Check optional variables
        for var, description in optional_vars.items():
            value = os.getenv(var)
            if value:
                if var == 'GOOGLE_APPLICATION_CREDENTIALS':
                    if os.path.exists(value):
                        self.log_result(f"Env Var: {var}", True, f"File exists: {value}")
                    else:
                        self.log_result(f"Env Var: {var}", False, f"File not found: {value}")
                        all_good = False
                else:
                    masked_value = value[:20] + "..." if len(value) > 20 else value
                    self.log_result(f"Env Var: {var}", True, f"Set ({masked_value})")
            else:
                if var == 'GOOGLE_APPLICATION_CREDENTIALS':
                    self.log_result(f"Env Var: {var}", True, f"Not set (optional for basic testing)")
                else:
                    self.log_result(f"Env Var: {var}", False, f"Not set - {description}")
        
        return all_good
    
    def check_supabase_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            from supabase_client import supabase_client
            if supabase_client.test_connection():
                self.log_result("Supabase Connection", True, "Connection successful")
                return True
            else:
                self.log_result("Supabase Connection", False, "Connection failed")
                return False
        except Exception as e:
            self.log_result("Supabase Connection", False, f"Error: {str(e)}")
            return False
    
    def check_database_schema(self) -> bool:
        """Check if database tables exist"""
        try:
            from supabase_client import supabase_client
            
            # Try to query each table
            tables_to_check = ['conversation_records', 'user_sessions']
            
            for table in tables_to_check:
                try:
                    result = supabase_client.client.table(table).select("count", count="exact").limit(1).execute()
                    self.log_result(f"Table: {table}", True, "Table exists and accessible")
                except Exception as e:
                    self.log_result(f"Table: {table}", False, f"Error accessing table: {str(e)}")
                    return False
            
            return True
        except Exception as e:
            self.log_result("Database Schema", False, f"Error: {str(e)}")
            return False
    
    def check_project_files(self) -> bool:
        """Check if all required project files exist"""
        required_files = [
            'main.py', 'grpc_server.py', 'client_example.py', 'models.py',
            'supabase_client.py', 'test_supabase.py', 'supabase_schema.sql',
            'requirements.txt', '.env', 'voice_assistant.proto'
        ]
        
        missing_files = []
        for file in required_files:
            if os.path.exists(file):
                self.log_result(f"File: {file}", True, "Exists")
            else:
                self.log_result(f"File: {file}", False, "Missing")
                missing_files.append(file)
        
        return len(missing_files) == 0
    
    def test_basic_functionality(self) -> bool:
        """Test basic application functionality"""
        try:
            # Test importing main modules
            from models import conversation_service, session_service
            self.log_result("Import Models", True, "Models imported successfully")
            
            # Test creating a test session
            import uuid
            test_session_id = f"test_{str(uuid.uuid4())[:8]}"
            test_user_id = f"test_user_{str(uuid.uuid4())[:8]}"
            
            session_result = session_service.create_user_session(test_session_id, test_user_id)
            if session_result:
                self.log_result("Session Creation", True, f"Test session created: {test_session_id}")
                
                # Test creating a conversation record
                record_result = conversation_service.create_conversation_record(
                    user_id=test_user_id,
                    session_id=test_session_id,
                    audio_input=b"test_audio",
                    text_input="Test message",
                    text_response="Test response",
                    audio_response=b"test_response_audio"
                )
                
                if record_result:
                    self.log_result("Conversation Creation", True, f"Test record created: {record_result['id']}")
                    return True
                else:
                    self.log_result("Conversation Creation", False, "Failed to create test record")
                    return False
            else:
                self.log_result("Session Creation", False, "Failed to create test session")
                return False
                
        except Exception as e:
            self.log_result("Basic Functionality", False, f"Error: {str(e)}")
            return False
    
    def check_api_server(self) -> bool:
        """Check if the API server can start"""
        try:
            # Try importing FastAPI app
            from main import app
            self.log_result("FastAPI Import", True, "FastAPI app imported successfully")
            return True
        except Exception as e:
            self.log_result("FastAPI Import", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_test(self) -> bool:
        """Run the comprehensive test suite"""
        try:
            result = subprocess.run([sys.executable, 'test_supabase.py'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.log_result("Comprehensive Tests", True, "All tests passed")
                return True
            else:
                self.log_result("Comprehensive Tests", False, f"Tests failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.log_result("Comprehensive Tests", False, "Tests timed out")
            return False
        except Exception as e:
            self.log_result("Comprehensive Tests", False, f"Error running tests: {str(e)}")
            return False
    
    def print_summary(self):
        """Print verification summary"""
        total_tests = len(self.results)
        passed_tests = sum(1 for _, success, _ in self.results if success)
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("🔍 SETUP VERIFICATION SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 ISSUES FOUND:")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
            
            print("\n💡 NEXT STEPS:")
            if any("Dependencies" in error for error in self.errors):
                print("- Run: pip install -r requirements.txt")
            if any("Env Var" in error for error in self.errors):
                print("- Update your .env file with the missing variables")
            if any("Supabase" in error for error in self.errors):
                print("- Check your Supabase credentials and project status")
                print("- Run the SQL schema in your Supabase dashboard")
            if any("Table" in error for error in self.errors):
                print("- Execute supabase_schema.sql in your Supabase SQL Editor")
        else:
            print("\n🎉 ALL CHECKS PASSED!")
            print("Your Voice Assistant with Supabase is ready to use!")
            print("\nTo start the application:")
            print("1. Run: python main.py")
            print("2. Visit: http://localhost:8000/docs")
            print("3. Test: curl http://localhost:8000/health")
        
        print("\n" + "="*60)

def main():
    print("🚀 Voice Assistant with Supabase - Setup Verification")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    verifier = SetupVerifier()
    
    # Run all verification steps
    print("📋 Running verification steps...\n")
    
    verifier.check_python_version()
    verifier.check_dependencies()
    verifier.check_environment_variables()
    verifier.check_project_files()
    verifier.check_supabase_connection()
    verifier.check_database_schema()
    verifier.check_api_server()
    verifier.test_basic_functionality()
    verifier.run_comprehensive_test()
    
    # Print summary
    verifier.print_summary()
    
    # Exit with appropriate code
    failed_tests = sum(1 for _, success, _ in verifier.results if not success)
    sys.exit(0 if failed_tests == 0 else 1)

if __name__ == "__main__":
    main()