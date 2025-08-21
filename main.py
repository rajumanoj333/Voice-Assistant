from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, Form, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
import uuid
import os
import uvicorn
import io
from dotenv import load_dotenv
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database services
try:
    from models import create_tables, get_db, conversation_service, session_service, voice_interaction_service
    DATABASE_AVAILABLE = True
except ImportError:
    logger.warning("Database models not available - running in demo mode")
    def create_tables(): pass
    def get_db(): yield None
    DATABASE_AVAILABLE = False
    
try:
    from llm_processor import llm_processor
    LLM_AVAILABLE = True
except ImportError:
    logger.warning("LLM processor not available - using mock responses")
    class MockLLMProcessor:
        def process_text(self, text, user_id, session_id):
            return f"Echo: {text} (processed by mock LLM)"
    llm_processor = MockLLMProcessor()
    LLM_AVAILABLE = False

# Import Google Cloud Services
try:
    from google_services import google_services
    GOOGLE_SERVICES_AVAILABLE = True
except Exception as e:
    logger.error(f"Google Cloud Services not available: {e}")
    GOOGLE_SERVICES_AVAILABLE = False
    google_services = None

load_dotenv()

app = FastAPI(
    title="Voice Assistant API",
    description="Enhanced Voice Assistant with Google Cloud Speech Services and OpenAI",
    version="2.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 Starting Voice Assistant API...")
    create_tables()  # Ensure tables are created
    
    # Log service availability
    services_status = {
        "database": DATABASE_AVAILABLE,
        "llm": LLM_AVAILABLE,
        "google_cloud": GOOGLE_SERVICES_AVAILABLE
    }
    
    logger.info(f"📊 Services Status: {services_status}")
    
    if GOOGLE_SERVICES_AVAILABLE and google_services:
        status = google_services.get_service_status()
        if status["configured"]:
            logger.info("✅ Google Cloud Services configured and ready")
        else:
            logger.warning("⚠️ Google Cloud Services not properly configured")

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time audio processing"""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    user_id = "default_user"
    
    logger.info(f"🔌 WebSocket connection established for session: {session_id}")
    
    # Create user session if database is available
    if DATABASE_AVAILABLE:
        try:
            session_service.create_user_session(session_id, user_id)
        except Exception as e:
            logger.error(f"Error creating session: {e}")
    
    try:
        while True:
            # For now, expect text input via websocket for testing
            data = await websocket.receive_text()
            
            logger.info(f"📨 Received text via WebSocket: {data[:50]}...")
            
            # Process text with LLM
            if LLM_AVAILABLE:
                response_text = llm_processor.process_text(data, user_id=user_id, session_id=session_id)
            else:
                response_text = f"Mock response: {data} (LLM not available)"
            
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
                    logger.error(f"Error saving conversation: {e}")

            # Send response back
            await websocket.send_text(response_text)
            logger.info(f"📤 Sent response via WebSocket: {response_text[:50]}...")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1000)

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile):
    """Enhanced audio upload endpoint with Google Cloud Speech processing"""
    session_id = str(uuid.uuid4())
    user_id = "default_user"
    
    logger.info(f"📁 Processing audio upload: {file.filename}")
    
    # Create user session if database is available
    if DATABASE_AVAILABLE:
        try:
            session_service.create_user_session(session_id, user_id)
        except Exception as e:
            logger.error(f"Error creating session: {e}")
    
    try:
        # Read file into bytes
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="Empty audio file provided")
        
        # Process with Google Cloud Speech-to-Text if available
        transcript = None
        transcription_metadata = {}
        
        if GOOGLE_SERVICES_AVAILABLE and google_services:
            logger.info(f"🎤 Transcribing audio with Google Cloud (size: {len(contents)} bytes)")
            transcript, transcription_metadata = google_services.speech_to_text(contents)
            
            if not transcript:
                if "error" in transcription_metadata:
                    error_msg = f"Transcription failed: {transcription_metadata['error']}"
                    logger.error(f"❌ {error_msg}")
                    raise HTTPException(status_code=500, detail=error_msg)
                else:
                    logger.warning("⚠️ No speech detected in audio")
                    transcript = "No speech detected in audio"
        else:
            # Fallback to mock transcript
            transcript = f"Mock transcript for uploaded file: {file.filename}"
            logger.warning("⚠️ Using mock transcript - Google Cloud Services not available")
        
        # Process text with LLM
        if LLM_AVAILABLE:
            response_text = llm_processor.process_text(transcript, user_id=user_id, session_id=session_id)
        else:
            response_text = f"Mock response: {transcript} (LLM not available)"
        
        # Generate audio response if Google Cloud TTS is available
        audio_response = None
        tts_metadata = {}
        
        if GOOGLE_SERVICES_AVAILABLE and google_services:
            logger.info("🔊 Generating audio response with Google Cloud TTS")
            audio_response, tts_metadata = google_services.text_to_speech(response_text)
            
            if not audio_response:
                logger.warning("⚠️ Failed to generate audio response")
        
        # Save conversation to database if available
        if DATABASE_AVAILABLE:
            try:
                conversation_service.create_conversation_record(
                    user_id=user_id,
                    session_id=session_id,
                    audio_input=contents,
                    text_input=transcript,
                    text_response=response_text,
                    audio_response=audio_response or b""
                )
                # Update session activity
                session_service.update_session_activity(session_id)
            except Exception as e:
                logger.error(f"Error saving conversation: {e}")

        # Prepare response
        response_data = {
            "filename": file.filename,
            "transcript": transcript,
            "llm_response": response_text,
            "session_id": session_id,
            "services_status": {
                "google_cloud": GOOGLE_SERVICES_AVAILABLE,
                "llm": LLM_AVAILABLE,
                "database": DATABASE_AVAILABLE
            },
            "metadata": {
                "transcription": transcription_metadata,
                "tts": tts_metadata
            }
        }
        
        # Add audio response if available
        if audio_response:
            response_data["audio_available"] = True
            response_data["audio_size"] = len(audio_response)
        else:
            response_data["audio_available"] = False
            response_data["message"] = "Audio response not available - Google Cloud TTS not configured"

        logger.info(f"✅ Audio processing completed successfully")
        return JSONResponse(response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Failed to process audio: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/process-text/")
async def process_text(text: str = Form(...)):
    """Enhanced text processing endpoint with audio response generation"""
    session_id = str(uuid.uuid4())
    user_id = "default_user"
    
    logger.info(f"💬 Processing text input: {text[:50]}...")
    
    # Create user session if database is available
    if DATABASE_AVAILABLE:
        try:
            session_service.create_user_session(session_id, user_id)
        except Exception as e:
            logger.error(f"Error creating session: {e}")
    
    try:
        # Process text with LLM
        if LLM_AVAILABLE:
            response_text = llm_processor.process_text(text, user_id=user_id, session_id=session_id)
        else:
            response_text = f"Mock response: {text} (LLM not available)"
        
        # Generate audio response if Google Cloud TTS is available
        audio_response = None
        tts_metadata = {}
        
        if GOOGLE_SERVICES_AVAILABLE and google_services:
            logger.info("🔊 Generating audio response with Google Cloud TTS")
            audio_response, tts_metadata = google_services.text_to_speech(response_text)
            
            if not audio_response:
                logger.warning("⚠️ Failed to generate audio response")
        
        # Save conversation to database if available
        if DATABASE_AVAILABLE:
            try:
                conversation_service.create_conversation_record(
                    user_id=user_id,
                    session_id=session_id,
                    audio_input=b"",  # No audio input
                    text_input=text,
                    text_response=response_text,
                    audio_response=audio_response or b""
                )
                # Update session activity
                session_service.update_session_activity(session_id)
            except Exception as e:
                logger.error(f"Error saving conversation: {e}")
        
        # Prepare response
        response_data = {
            "input_text": text,
            "llm_response": response_text,
            "session_id": session_id,
            "services_status": {
                "google_cloud": GOOGLE_SERVICES_AVAILABLE,
                "llm": LLM_AVAILABLE,
                "database": DATABASE_AVAILABLE
            },
            "metadata": {
                "tts": tts_metadata
            }
        }
        
        # Add audio response if available
        if audio_response:
            response_data["audio_available"] = True
            response_data["audio_size"] = len(audio_response)
        else:
            response_data["audio_available"] = False
            response_data["message"] = "Audio response not available - Google Cloud TTS not configured"

        logger.info(f"✅ Text processing completed successfully")
        return JSONResponse(response_data)
        
    except Exception as e:
        error_msg = f"Failed to process text: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

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
        logger.error(f"Error getting conversation history: {e}")
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
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with comprehensive service status"""
    # Check database status
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
    
    # Check Google Cloud Services status
    google_status = "not_available"
    google_details = {}
    
    if GOOGLE_SERVICES_AVAILABLE and google_services:
        try:
            status = google_services.get_service_status()
            google_status = "configured" if status["configured"] else "not_configured"
            google_details = status
        except Exception as e:
            google_status = f"error: {str(e)}"
    
    # Overall health status
    overall_status = "healthy"
    if db_status != "connected" or google_status != "configured":
        overall_status = "degraded"
    
    return JSONResponse({
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": {
                "status": db_status,
                "available": DATABASE_AVAILABLE
            },
            "llm": {
                "status": "available" if LLM_AVAILABLE else "not_available",
                "available": LLM_AVAILABLE
            },
            "google_cloud": {
                "status": google_status,
                "available": GOOGLE_SERVICES_AVAILABLE,
                "details": google_details
            }
        },
        "version": "2.0.0"
    })

@app.get("/services/status")
async def get_services_status():
    """Get detailed status of all services"""
    status = {
        "database": {
            "available": DATABASE_AVAILABLE,
            "description": "Supabase database for conversation storage"
        },
        "llm": {
            "available": LLM_AVAILABLE,
            "description": "OpenAI LLM for text processing"
        },
        "google_cloud": {
            "available": GOOGLE_SERVICES_AVAILABLE,
            "description": "Google Cloud Speech-to-Text and Text-to-Speech"
        }
    }
    
    # Add Google Cloud details if available
    if GOOGLE_SERVICES_AVAILABLE and google_services:
        status["google_cloud"]["details"] = google_services.get_service_status()
    
    return JSONResponse(status)

@app.get("/services/test")
async def test_services():
    """Test all available services"""
    test_results = {
        "database": {"status": "not_tested", "error": None},
        "llm": {"status": "not_tested", "error": None},
        "google_cloud": {"status": "not_tested", "error": None}
    }
    
    # Test database
    if DATABASE_AVAILABLE:
        try:
            from supabase_client import supabase_client
            if supabase_client.test_connection():
                test_results["database"] = {"status": "working", "error": None}
            else:
                test_results["database"] = {"status": "failed", "error": "Connection failed"}
        except Exception as e:
            test_results["database"] = {"status": "failed", "error": str(e)}
    
    # Test LLM
    if LLM_AVAILABLE:
        try:
            test_response = llm_processor.process_text("Test message", "test_user", "test_session")
            if test_response:
                test_results["llm"] = {"status": "working", "error": None}
            else:
                test_results["llm"] = {"status": "failed", "error": "No response generated"}
        except Exception as e:
            test_results["llm"] = {"status": "failed", "error": str(e)}
    
    # Test Google Cloud Services
    if GOOGLE_SERVICES_AVAILABLE and google_services:
        try:
            google_test_results = google_services.test_services()
            test_results["google_cloud"] = google_test_results
        except Exception as e:
            test_results["google_cloud"] = {"status": "failed", "error": str(e)}
    
    return JSONResponse(test_results)

# Voice Interactions Endpoints
@app.post("/voice-interactions/")
async def create_voice_interaction(
    audio_file_url: str = Form(...),
    transcript: str = Form(...),
    llm_response: str = Form(...)
):
    """Create a new voice interaction"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        interaction = voice_interaction_service.create_voice_interaction(
            audio_file_url=audio_file_url,
            transcript=transcript,
            llm_response=llm_response
        )
        
        if interaction:
            return JSONResponse({
                "success": True,
                "interaction": interaction,
                "message": "Voice interaction created successfully"
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to create voice interaction")
            
    except Exception as e:
        logger.error(f"Error creating voice interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create voice interaction: {str(e)}")

@app.get("/voice-interactions/{interaction_id}")
async def get_voice_interaction(interaction_id: str):
    """Get a specific voice interaction by ID"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        interaction = voice_interaction_service.get_voice_interaction(interaction_id)
        
        if interaction:
            return JSONResponse({
                "success": True,
                "interaction": interaction
            })
        else:
            raise HTTPException(status_code=404, detail="Voice interaction not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voice interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get voice interaction: {str(e)}")

@app.get("/voice-interactions/")
async def get_voice_interactions(limit: int = 50, offset: int = 0):
    """Get all voice interactions with pagination"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        interactions = voice_interaction_service.get_voice_interactions(limit=limit, offset=offset)
        
        return JSONResponse({
            "success": True,
            "interactions": interactions,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "count": len(interactions)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting voice interactions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get voice interactions: {str(e)}")

@app.put("/voice-interactions/{interaction_id}")
async def update_voice_interaction(
    interaction_id: str,
    updates: dict = Body(...)
):
    """Update a voice interaction"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        updated_interaction = voice_interaction_service.update_voice_interaction(
            interaction_id, updates
        )
        
        if updated_interaction:
            return JSONResponse({
                "success": True,
                "interaction": updated_interaction,
                "message": "Voice interaction updated successfully"
            })
        else:
            raise HTTPException(status_code=404, detail="Voice interaction not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating voice interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update voice interaction: {str(e)}")

@app.delete("/voice-interactions/{interaction_id}")
async def delete_voice_interaction(interaction_id: str):
    """Delete a voice interaction"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        success = voice_interaction_service.delete_voice_interaction(interaction_id)
        
        if success:
            return JSONResponse({
                "success": True,
                "message": "Voice interaction deleted successfully"
            })
        else:
            raise HTTPException(status_code=404, detail="Voice interaction not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting voice interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete voice interaction: {str(e)}")

@app.get("/")
async def root():
    """Enhanced root endpoint with comprehensive information"""
    return JSONResponse({
        "message": "Voice Assistant API v2.0 - Enhanced with Google Cloud Speech Services",
        "version": "2.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "services_status": "/services/status",
            "services_test": "/services/test",
            "websocket": "/ws/audio",
            "upload_audio": "/upload-audio/",
            "process_text": "/process-text/",
            "conversation_history": "/conversation-history/{user_id}",
            "session": "/session/{session_id}",
            "voice_interactions": "/voice-interactions/",
            "voice_interaction": "/voice-interactions/{interaction_id}"
        },
        "services": {
            "database": "enabled" if DATABASE_AVAILABLE else "disabled",
            "llm": "enabled" if LLM_AVAILABLE else "disabled",
            "google_cloud": "enabled" if GOOGLE_SERVICES_AVAILABLE else "disabled"
        },
        "status": "running",
        "features": [
            "Speech-to-Text with Google Cloud",
            "Text-to-Speech with Google Cloud",
            "LLM processing with OpenAI",
            "Conversation history storage",
            "Voice interactions storage",
            "Real-time WebSocket support",
            "Enhanced error handling",
            "Comprehensive status monitoring"
        ]
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

