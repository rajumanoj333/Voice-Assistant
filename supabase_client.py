from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

load_dotenv()

class SupabaseClient:
    """
    Supabase client wrapper for the voice assistant application (simple log only)
    """
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.client: Client = create_client(self.url, self.key)
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        return self.client

    # Conversation Log Operations
    def create_conversation_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new conversation log entry"""
        try:
            result = self.client.table('conversation_log').insert(log_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating conversation log: {e}")
            raise

    def get_conversation_log(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation log by ID"""
        try:
            result = self.client.table('conversation_log').select("*").eq('id', log_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting conversation log: {e}")
            return None

    def get_conversation_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent conversation logs"""
        try:
            result = self.client.table('conversation_log').select("*").order('timestamp', desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting conversation logs: {e}")
            return []

# Global instance
supabase_client = SupabaseClient()