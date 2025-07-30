from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import uuid

try:
    from supabase_client import supabase_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Supabase client not available.")

load_dotenv()

Base = declarative_base()

class ConversationLog(Base):
    __tablename__ = 'conversation_log'
    id = Column(String, primary_key=True)
    audio_type = Column(String, nullable=False)
    audio_transcription = Column(Text, nullable=False)
    llm_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Service for Supabase log operations
class ConversationLogService:
    def __init__(self):
        self.use_supabase = SUPABASE_AVAILABLE

    def create_conversation_log(self, audio_type: str, audio_transcription: str, llm_response: str) -> Optional[Dict[str, Any]]:
        log_id = str(uuid.uuid4())
        if self.use_supabase:
            log_data = {
                'id': log_id,
                'audio_type': audio_type,
                'audio_transcription': audio_transcription,
                'llm_response': llm_response,
                'timestamp': datetime.utcnow().isoformat()
            }
            return supabase_client.create_conversation_log(log_data)
        else:
            return None

    def get_conversation_log(self, log_id: str) -> Optional[Dict[str, Any]]:
        if self.use_supabase:
            return supabase_client.get_conversation_log(log_id)
        else:
            return None

    def get_conversation_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        if self.use_supabase:
            return supabase_client.get_conversation_logs(limit)
        else:
            return []

# Global service instance
conversation_log_service = ConversationLogService()
