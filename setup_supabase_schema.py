#!/usr/bin/env python3
"""
Supabase Schema Setup Instructions
Provides step-by-step instructions for setting up the database schema in Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def test_supabase_connection():
    """Test connection to Supabase"""
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False, None
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase successfully")
        return True, supabase
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return False, None

def check_tables_exist(supabase: Client):
    """Check if the required tables exist"""
    tables_status = {}
    
    # Test user_sessions table
    try:
        result = supabase.table('user_sessions').select('*').limit(1).execute()
        tables_status['user_sessions'] = True
        print("✅ user_sessions table exists")
    except Exception as e:
        tables_status['user_sessions'] = False
        print("❌ user_sessions table does not exist")
    
    # Test conversation_records table  
    try:
        result = supabase.table('conversation_records').select('*').limit(1).execute()
        tables_status['conversation_records'] = True
        print("✅ conversation_records table exists")
    except Exception as e:
        tables_status['conversation_records'] = False
        print("❌ conversation_records table does not exist")
        
    return tables_status

def show_setup_instructions():
    """Show detailed setup instructions"""
    print("\n" + "="*70)
    print("📋 SUPABASE DATABASE SCHEMA SETUP INSTRUCTIONS")
    print("="*70)
    
    print("\n🔗 Step 1: Open Supabase Dashboard")
    print("   1. Go to https://supabase.com/dashboard")
    print("   2. Sign in to your account")
    print("   3. Select your project: czqnzosfhqthjjblkmfh")
    
    print("\n📝 Step 2: Open SQL Editor")
    print("   1. Click on 'SQL Editor' in the left sidebar")
    print("   2. Click 'New query' to create a new SQL query")
    
    print("\n📋 Step 3: Execute Schema SQL")
    print("   1. Copy the contents of 'supabase_schema.sql' file")
    print("   2. Paste it into the SQL editor")
    print("   3. Click 'Run' to execute the SQL")
    
    print("\n✨ Step 4: Verify Setup")
    print("   1. After running the SQL, you should see tables created")
    print("   2. Run this script again to verify: python3 setup_supabase_schema.py")
    print("   3. Or run the full verification: python3 setup_verification.py")
    
    print("\n📁 The SQL file contains:")
    print("   ✓ user_sessions table - stores user session data")
    print("   ✓ conversation_records table - stores conversation history")
    print("   ✓ RLS policies for security (with anonymous access for development)")
    print("   ✓ Indexes for performance optimization")
    
    print("\n" + "="*70)

def main():
    print("🚀 Supabase Schema Setup Helper")
    print("=" * 50)
    
    # Test connection
    connected, supabase = test_supabase_connection()
    
    if not connected:
        print("\n❌ Cannot connect to Supabase. Please check your credentials in .env file.")
        return
    
    print("\n🔍 Checking if database tables exist...")
    tables_status = check_tables_exist(supabase)
    
    all_tables_exist = all(tables_status.values())
    
    if all_tables_exist:
        print("\n🎉 All required tables exist! Your database is ready.")
        print("You can now run: python3 setup_verification.py")
    else:
        print(f"\n⚠️  Missing tables: {[table for table, exists in tables_status.items() if not exists]}")
        show_setup_instructions()
        
        print("\n💡 Quick Setup Guide:")
        print("   1. Open Supabase Dashboard → SQL Editor")
        print("   2. Copy and paste contents of 'supabase_schema.sql'")
        print("   3. Click 'Run' to execute")
        print("   4. Run this script again to verify")

if __name__ == "__main__":
    main()