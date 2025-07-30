#!/usr/bin/env python3
"""
Supabase Schema Setup Instructions (Simple Log Table)
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def test_supabase_connection():
    """Test connection to Supabase"""
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False, None
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase successfully")
        return True, supabase
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return False, None

def check_table_exists(supabase: Client):
    """Check if the conversation_log table exists"""
    try:
        result = supabase.table('conversation_log').select('*').limit(1).execute()
        print("✅ conversation_log table exists")
        return True
    except Exception as e:
        print("❌ conversation_log table does not exist")
        return False

def show_setup_instructions():
    print("\n" + "="*70)
    print("📋 SUPABASE DATABASE SCHEMA SETUP INSTRUCTIONS (Simple Log Table)")
    print("="*70)
    print("\n🔗 Step 1: Open Supabase Dashboard")
    print("   1. Go to https://supabase.com/dashboard")
    print("   2. Sign in to your account")
    print("   3. Select your project")
    print("\n📝 Step 2: Open SQL Editor")
    print("   1. Click on 'SQL Editor' in the left sidebar")
    print("   2. Click 'New query' to create a new SQL query")
    print("\n📋 Step 3: Execute Schema SQL")
    print("   1. Copy the contents of 'supabase_schema.sql' file")
    print("   2. Paste it into the SQL editor")
    print("   3. Click 'Run' to execute the SQL")
    print("\n✨ Step 4: Verify Setup")
    print("   1. After running the SQL, you should see the table created")
    print("   2. Run this script again to verify: python3 setup_supabase_schema.py")
    print("\n" + "="*70)

def main():
    print("🚀 Supabase Schema Setup Helper (Simple Log Table)")
    print("=" * 50)
    connected, supabase = test_supabase_connection()
    if not connected:
        print("\n❌ Cannot connect to Supabase. Please check your credentials in .env file.")
        return
    print("\n🔍 Checking if conversation_log table exists...")
    table_exists = check_table_exists(supabase)
    if table_exists:
        print("\n🎉 Table exists! Your database is ready.")
    else:
        print(f"\n⚠️  Missing table: conversation_log")
        show_setup_instructions()
        print("\n💡 Quick Setup Guide:")
        print("   1. Open Supabase Dashboard → SQL Editor")
        print("   2. Copy and paste contents of 'supabase_schema.sql'")
        print("   3. Click 'Run' to execute")
        print("   4. Run this script again to verify")

if __name__ == "__main__":
    main()