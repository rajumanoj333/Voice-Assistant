from sqlalchemy import Column, String, LargeBinary, DateTime, Integer, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

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

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/voice_assistant')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
