from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

load_dotenv()

class SupabaseClient:
    """
    Supabase client wrapper for the voice assistant application
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
    
    # Conversation Records Operations
    def create_conversation_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new conversation record"""
        try:
            result = self.client.table('conversation_records').insert(record_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating conversation record: {e}")
            raise
    
    def get_conversation_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation record by ID"""
        try:
            result = self.client.table('conversation_records').select("*").eq('id', record_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting conversation record: {e}")
            return None
    
    def get_conversation_history(self, user_id: str, session_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for a user, optionally filtered by session"""
        try:
            query = self.client.table('conversation_records').select("*").eq('user_id', user_id)
            
            if session_id:
                query = query.eq('session_id', session_id)
            
            result = query.order('timestamp', desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def update_conversation_record(self, record_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a conversation record"""
        try:
            result = self.client.table('conversation_records').update(updates).eq('id', record_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating conversation record: {e}")
            return None
    
    def delete_conversation_record(self, record_id: str) -> bool:
        """Delete a conversation record"""
        try:
            self.client.table('conversation_records').delete().eq('id', record_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting conversation record: {e}")
            return False
    
    # User Sessions Operations
    def create_user_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user session"""
        try:
            result = self.client.table('user_sessions').insert(session_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating user session: {e}")
            raise
    
    def get_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a user session by ID"""
        try:
            result = self.client.table('user_sessions').select("*").eq('session_id', session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user session: {e}")
            return None
    
    def get_active_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get active sessions for a user"""
        try:
            result = self.client.table('user_sessions').select("*").eq('user_id', user_id).eq('is_active', True).execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting active sessions: {e}")
            return []
    
    def update_session_activity(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Update the last activity timestamp for a session"""
        try:
            from datetime import datetime
            result = self.client.table('user_sessions').update({
                'last_activity': datetime.utcnow().isoformat()
            }).eq('session_id', session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating session activity: {e}")
            return None
    
    def deactivate_session(self, session_id: str) -> bool:
        """Deactivate a user session"""
        try:
            self.client.table('user_sessions').update({'is_active': False}).eq('session_id', session_id).execute()
            return True
        except Exception as e:
            print(f"Error deactivating session: {e}")
            return False
    
    # Voice Interactions Operations
    def create_voice_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new voice interaction"""
        try:
            result = self.client.table('voice_interactions').insert(interaction_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating voice interaction: {e}")
            raise
    
    def get_voice_interaction(self, interaction_id: str) -> Optional[Dict[str, Any]]:
        """Get a voice interaction by ID"""
        try:
            result = self.client.table('voice_interactions').select("*").eq('id', interaction_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting voice interaction: {e}")
            return None
    
    def get_voice_interactions(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get voice interactions with pagination"""
        try:
            result = self.client.table('voice_interactions').select("*").order('created_at', desc=True).range(offset, offset + limit - 1).execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting voice interactions: {e}")
            return []
    
    def update_voice_interaction(self, interaction_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a voice interaction"""
        try:
            result = self.client.table('voice_interactions').update(updates).eq('id', interaction_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating voice interaction: {e}")
            return None
    
    def delete_voice_interaction(self, interaction_id: str) -> bool:
        """Delete a voice interaction"""
        try:
            self.client.table('voice_interactions').delete().eq('id', interaction_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting voice interaction: {e}")
            return False
    
    # Utility methods
    def test_connection(self) -> bool:
        """Test the Supabase connection"""
        try:
            # Try to query the user_sessions table
            result = self.client.table('user_sessions').select("count", count="exact").limit(1).execute()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

# Global instance
supabase_client = SupabaseClient()