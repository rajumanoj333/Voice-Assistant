from sqlalchemy import Column, String, LargeBinary, DateTime, Integer, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import uuid

# Import Supabase client
try:
    from supabase_client import supabase_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Supabase client not available, falling back to PostgreSQL")

load_dotenv()

Base = declarative_base()

class ConversationRecord(Base):
    __tablename__ = 'conversation_records'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    audio_input = Column(LargeBinary, nullable=False)
    text_input = Column(Text, nullable=False)
    text_response = Column(Text, nullable=False)
    audio_response = Column(LargeBinary, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sample_rate = Column(Integer, default=16000)
    audio_format = Column(String, default='wav')

class UserSession(Base):
    __tablename__ = 'user_sessions'
    
    session_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)

# Database configuration for PostgreSQL (fallback)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/voice_assistant')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create tables - handles both Supabase and PostgreSQL"""
    if SUPABASE_AVAILABLE:
        # For Supabase, tables should be created through the Supabase dashboard
        # This function will test the connection instead
        try:
            if supabase_client.test_connection():
                print("✅ Supabase connection successful")
            else:
                print("❌ Supabase connection failed")
        except Exception as e:
            print(f"❌ Supabase connection error: {e}")
    else:
        # Create PostgreSQL tables
        Base.metadata.create_all(bind=engine)
        print("✅ PostgreSQL tables created")

def get_db():
    """Get database session - PostgreSQL only (for legacy support)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# New Supabase-based data access layer
class ConversationService:
    """Service class for conversation record operations"""
    
    def __init__(self):
        self.use_supabase = SUPABASE_AVAILABLE
    
    def create_conversation_record(self, user_id: str, session_id: str, 
                                 audio_input: bytes, text_input: str, 
                                 text_response: str, audio_response: bytes,
                                 sample_rate: int = 16000, audio_format: str = 'wav') -> Optional[Dict[str, Any]]:
        """Create a new conversation record"""
        record_id = str(uuid.uuid4())
        
        if self.use_supabase:
            record_data = {
                'id': record_id,
                'user_id': user_id,
                'session_id': session_id,
                'audio_input': audio_input.hex() if audio_input else None,  # Convert bytes to hex string
                'text_input': text_input,
                'text_response': text_response,
                'audio_response': audio_response.hex() if audio_response else None,  # Convert bytes to hex string
                'timestamp': datetime.utcnow().isoformat(),
                'sample_rate': sample_rate,
                'audio_format': audio_format
            }
            return supabase_client.create_conversation_record(record_data)
        else:
            # Fallback to PostgreSQL
            db = SessionLocal()
            try:
                record = ConversationRecord(
                    id=record_id,
                    user_id=user_id,
                    session_id=session_id,
                    audio_input=audio_input,
                    text_input=text_input,
                    text_response=text_response,
                    audio_response=audio_response,
                    sample_rate=sample_rate,
                    audio_format=audio_format
                )
                db.add(record)
                db.commit()
                db.refresh(record)
                return {
                    'id': record.id,
                    'user_id': record.user_id,
                    'session_id': record.session_id,
                    'text_input': record.text_input,
                    'text_response': record.text_response,
                    'timestamp': record.timestamp.isoformat() if record.timestamp else None,
                    'sample_rate': record.sample_rate,
                    'audio_format': record.audio_format
                }
            except Exception as e:
                db.rollback()
                print(f"Error creating conversation record: {e}")
                return None
            finally:
                db.close()
    
    def get_conversation_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation record by ID"""
        if self.use_supabase:
            record = supabase_client.get_conversation_record(record_id)
            if record:
                # Convert hex strings back to bytes, handling None values
                if record.get('audio_input'):
                    try:
                        record['audio_input'] = bytes.fromhex(record['audio_input'])
                    except (ValueError, TypeError):
                        record['audio_input'] = b''
                
                if record.get('audio_response'):
                    try:
                        record['audio_response'] = bytes.fromhex(record['audio_response'])
                    except (ValueError, TypeError):
                        record['audio_response'] = b''
            return record
        else:
            # Fallback to PostgreSQL
            db = SessionLocal()
            try:
                record = db.query(ConversationRecord).filter(ConversationRecord.id == record_id).first()
                if record:
                    return {
                        'id': record.id,
                        'user_id': record.user_id,
                        'session_id': record.session_id,
                        'audio_input': record.audio_input,
                        'text_input': record.text_input,
                        'text_response': record.text_response,
                        'audio_response': record.audio_response,
                        'timestamp': record.timestamp.isoformat() if record.timestamp else None,
                        'sample_rate': record.sample_rate,
                        'audio_format': record.audio_format
                    }
                return None
            finally:
                db.close()
    
    def get_conversation_history(self, user_id: str, session_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for a user"""
        if self.use_supabase:
            return supabase_client.get_conversation_history(user_id, session_id, limit)
        else:
            # Fallback to PostgreSQL
            db = SessionLocal()
            try:
                query = db.query(ConversationRecord).filter(ConversationRecord.user_id == user_id)
                if session_id:
                    query = query.filter(ConversationRecord.session_id == session_id)
                
                records = query.order_by(ConversationRecord.timestamp.desc()).limit(limit).all()
                return [{
                    'id': record.id,
                    'user_id': record.user_id,
                    'session_id': record.session_id,
                    'text_input': record.text_input,
                    'text_response': record.text_response,
                    'timestamp': record.timestamp.isoformat() if record.timestamp else None,
                    'sample_rate': record.sample_rate,
                    'audio_format': record.audio_format
                } for record in records]
            finally:
                db.close()

class SessionService:
    """Service class for user session operations"""
    
    def __init__(self):
        self.use_supabase = SUPABASE_AVAILABLE
    
    def create_user_session(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Create a new user session"""
        if self.use_supabase:
            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'created_at': datetime.utcnow().isoformat(),
                'last_activity': datetime.utcnow().isoformat(),
                'is_active': True
            }
            return supabase_client.create_user_session(session_data)
        else:
            # Fallback to PostgreSQL
            db = SessionLocal()
            try:
                session = UserSession(
                    session_id=session_id,
                    user_id=user_id,
                    is_active=1
                )
                db.add(session)
                db.commit()
                db.refresh(session)
                return {
                    'session_id': session.session_id,
                    'user_id': session.user_id,
                    'created_at': session.created_at.isoformat() if session.created_at else None,
                    'last_activity': session.last_activity.isoformat() if session.last_activity else None,
                    'is_active': bool(session.is_active)
                }
            except Exception as e:
                db.rollback()
                print(f"Error creating user session: {e}")
                return None
            finally:
                db.close()
    
    def get_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a user session by ID"""
        if self.use_supabase:
            return supabase_client.get_user_session(session_id)
        else:
            # Fallback to PostgreSQL
            db = SessionLocal()
            try:
                session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
                if session:
                    return {
                        'session_id': session.session_id,
                        'user_id': session.user_id,
                        'created_at': session.created_at.isoformat() if session.created_at else None,
                        'last_activity': session.last_activity.isoformat() if session.last_activity else None,
                        'is_active': bool(session.is_active)
                    }
                return None
            finally:
                db.close()
    
    def update_session_activity(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Update the last activity timestamp for a session"""
        if self.use_supabase:
            return supabase_client.update_session_activity(session_id)
        else:
            # Fallback to PostgreSQL
            db = SessionLocal()
            try:
                session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
                if session:
                    session.last_activity = datetime.utcnow()
                    db.commit()
                    db.refresh(session)
                    return {
                        'session_id': session.session_id,
                        'user_id': session.user_id,
                        'created_at': session.created_at.isoformat() if session.created_at else None,
                        'last_activity': session.last_activity.isoformat() if session.last_activity else None,
                        'is_active': bool(session.is_active)
                    }
                return None
            except Exception as e:
                db.rollback()
                print(f"Error updating session activity: {e}")
                return None
            finally:
                db.close()

# Global service instances
conversation_service = ConversationService()
session_service = SessionService()
