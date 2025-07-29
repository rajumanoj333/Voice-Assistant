from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, Form, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
import uuid
import os
import uvicorn
import io
from dotenv import load_dotenv
import json

# Import database services
try:
    from models import create_tables, get_db, conversation_service, session_service
    DATABASE_AVAILABLE = True
except ImportError:
    print("Database models not available - running in demo mode")
    def create_tables(): pass
    def get_db(): yield None
    DATABASE_AVAILABLE = False
    
try:
    from llm_processor import llm_processor
except ImportError:
    print("LLM processor not available - using mock responses")
    class MockLLMProcessor:
        def process_text(self, text, user_id, session_id):
            return f"Echo: {text} (processed by mock LLM)"
    llm_processor = MockLLMProcessor()

load_dotenv()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    create_tables()  # Ensure tables are created

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    user_id = "default_user"
    
    # Create user session if database is available
    if DATABASE_AVAILABLE:
        try:
            session_service.create_user_session(session_id, user_id)
        except Exception as e:
            print(f"Error creating session: {e}")
    
    try:
        while True:
            # For now, expect text input via websocket for testing
            data = await websocket.receive_text()
            
            # Process text with LLM
            response_text = llm_processor.process_text(data, user_id=user_id, session_id=session_id)
            
            # Save conversation to database if available
            if DATABASE_AVAILABLE:
                try:
                    conversation_service.create_conversation_record(
                        user_id=user_id,
                        session_id=session_id,
                        audio_input=b"",  # No audio in websocket text mode
                        text_input=data,
                        text_response=response_text,
                        audio_response=b""  # No audio in websocket text mode
                    )
                    # Update session activity
                    session_service.update_session_activity(session_id)
                except Exception as e:
                    print(f"Error saving conversation: {e}")

            # For simplified version, just send back text response
            await websocket.send_text(response_text)

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1000)

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile):
    session_id = str(uuid.uuid4())
    user_id = "default_user"
    
    # Create user session if database is available
    if DATABASE_AVAILABLE:
        try:
            session_service.create_user_session(session_id, user_id)
        except Exception as e:
            print(f"Error creating session: {e}")
    
    try:
        # Read file into bytes
        contents = await file.read()
        
        # For simplified version, just return a mock response
        mock_transcript = f"Mock transcript for uploaded file: {file.filename}"
        
        # Process text with LLM
        response_text = llm_processor.process_text(mock_transcript, user_id=user_id, session_id=session_id)
        
        # Save conversation to database if available
        if DATABASE_AVAILABLE:
            try:
                conversation_service.create_conversation_record(
                    user_id=user_id,
                    session_id=session_id,
                    audio_input=contents,
                    text_input=mock_transcript,
                    text_response=response_text,
                    audio_response=b""  # No audio response in mock mode
                )
                # Update session activity
                session_service.update_session_activity(session_id)
            except Exception as e:
                print(f"Error saving conversation: {e}")

        # Return JSON response instead of audio for now
        return JSONResponse({
            "filename": file.filename,
            "mock_transcript": mock_transcript,
            "llm_response": response_text,
            "session_id": session_id,
            "message": "Audio processing is in simplified mode - actual speech processing not available",
            "database_status": "enabled" if DATABASE_AVAILABLE else "disabled"
        })
        
    except Exception as e:
        print(f"Error processing uploaded audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {str(e)}")

@app.post("/process-text/")
async def process_text(text: str = Form(...)):
    """Simple endpoint to process text input and get LLM response"""
    session_id = str(uuid.uuid4())
    user_id = "default_user"
    
    # Create user session if database is available
    if DATABASE_AVAILABLE:
        try:
            session_service.create_user_session(session_id, user_id)
        except Exception as e:
            print(f"Error creating session: {e}")
    
    try:
        # Process text with LLM
        response_text = llm_processor.process_text(text, user_id=user_id, session_id=session_id)
        
        # Save conversation to database if available
        if DATABASE_AVAILABLE:
            try:
                conversation_service.create_conversation_record(
                    user_id=user_id,
                    session_id=session_id,
                    audio_input=b"",  # No audio input
                    text_input=text,
                    text_response=response_text,
                    audio_response=b""  # No audio response
                )
                # Update session activity
                session_service.update_session_activity(session_id)
            except Exception as e:
                print(f"Error saving conversation: {e}")
        
        return JSONResponse({
            "input_text": text,
            "llm_response": response_text,
            "session_id": session_id,
            "database_status": "enabled" if DATABASE_AVAILABLE else "disabled"
        })
        
    except Exception as e:
        print(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process text: {str(e)}")

@app.get("/conversation-history/{user_id}")
async def get_conversation_history(user_id: str, session_id: str = None, limit: int = 50):
    """Get conversation history for a user"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        history = conversation_service.get_conversation_history(user_id, session_id, limit)
        return JSONResponse({
            "user_id": user_id,
            "session_id": session_id,
            "conversation_count": len(history),
            "conversations": history
        })
    except Exception as e:
        print(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        session = session_service.get_user_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return JSONResponse(session)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint with database status"""
    db_status = "connected"
    if DATABASE_AVAILABLE:
        try:
            from supabase_client import supabase_client
            if not supabase_client.test_connection():
                db_status = "connection_failed"
        except Exception as e:
            db_status = f"error: {str(e)}"
    else:
        db_status = "not_configured"
    
    return JSONResponse({
        "status": "healthy",
        "database": db_status,
        "supabase_available": DATABASE_AVAILABLE
    })

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return JSONResponse({
        "message": "Voice Assistant API with Supabase",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "websocket": "/ws/audio",
            "upload_audio": "/upload-audio/",
            "process_text": "/process-text/",
            "conversation_history": "/conversation-history/{user_id}",
            "session": "/session/{session_id}"
        },
        "database_status": "enabled" if DATABASE_AVAILABLE else "disabled",
        "status": "running"
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

