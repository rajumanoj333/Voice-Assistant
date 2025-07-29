from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, Form, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
import uuid
import os
import uvicorn
import io
from dotenv import load_dotenv
import json

# For now, we'll create simplified imports that work without complex dependencies
try:
    from models import create_tables, get_db, ConversationRecord
except ImportError:
    print("Database models not available - running in demo mode")
    def create_tables(): pass
    def get_db(): yield None
    
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
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    try:
        while True:
            # For now, expect text input via websocket for testing
            data = await websocket.receive_text()
            
            # Process text with LLM
            response_text = llm_processor.process_text(data, user_id="default_user", session_id=session_id)

            # For simplified version, just send back text response
            await websocket.send_text(response_text)

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1000)

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile, db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    try:
        # Read file into bytes
        contents = await file.read()
        
        # For simplified version, just return a mock response
        mock_transcript = f"Mock transcript for uploaded file: {file.filename}"
        
        # Process text with LLM
        response_text = llm_processor.process_text(mock_transcript, user_id="default_user", session_id=session_id)

        # Return JSON response instead of audio for now
        return JSONResponse({
            "filename": file.filename,
            "mock_transcript": mock_transcript,
            "llm_response": response_text,
            "session_id": session_id,
            "message": "Audio processing is in simplified mode - actual speech processing not available"
        })
        
    except Exception as e:
        print(f"Error processing uploaded audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {str(e)}")

@app.post("/process-text/")
async def process_text(text: str = Form(...), db: Session = Depends(get_db)):
    """Simple endpoint to process text input and get LLM response"""
    session_id = str(uuid.uuid4())
    try:
        # Process text with LLM
        response_text = llm_processor.process_text(text, user_id="default_user", session_id=session_id)
        
        return JSONResponse({
            "input_text": text,
            "llm_response": response_text,
            "session_id": session_id
        })
        
    except Exception as e:
        print(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process text: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return JSONResponse({
        "message": "Voice Assistant API",
        "endpoints": {
            "docs": "/docs",
            "websocket": "/ws/audio",
            "upload_audio": "/upload-audio/",
            "process_text": "/process-text/"
        },
        "status": "running"
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

