#!/usr/bin/env python3
"""
Comprehensive Voice Assistant gRPC Server
Integrates SileroVAD, Google Cloud STT/TTS, LLM processing, and database storage
"""

import grpc
from concurrent import futures
import asyncio
import uuid
from datetime import datetime
import logging
from typing import Optional, List
import io

# Import generated protobuf classes
import voice_assistant_pb2
import voice_assistant_pb2_grpc

# Import our custom processors
from vad_processor import vad_processor
from google_services import google_services
from llm_processor import llm_processor
from models import SessionLocal, ConversationRecord, UserSession

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceAssistantServicer(voice_assistant_pb2_grpc.VoiceAssistantServicer):
    """
    Main gRPC servicer for the Voice Assistant
    Handles audio input/output with full processing pipeline
    """
    
    def __init__(self):
        self.active_sessions = {}  # Track active sessions
        
    def ProcessVoice(self, request, context):
        """
        Main voice processing endpoint
        Takes audio input, processes through full pipeline, returns audio response
        """
        try:
            logger.info(f"Processing voice request for session: {request.session_id}")
            
            # Step 1: Voice Activity Detection
            if not vad_processor.is_speech_present(request.audio_data):
                return voice_assistant_pb2.AudioResponse(
                    success=False,
                    error_message="No speech detected in audio",
                    session_id=request.session_id
                )
            
            # Step 2: Extract speech segments using SileroVAD
            speech_segments = vad_processor.extract_speech_segments(request.audio_data)
            if not speech_segments:
                return voice_assistant_pb2.AudioResponse(
                    success=False,
                    error_message="Failed to extract speech segments",
                    session_id=request.session_id
                )
            
            # Use the first (or combined) speech segment
            primary_speech = speech_segments[0] if speech_segments else request.audio_data
            
            # Step 3: Speech-to-Text using Google Cloud STT
            transcribed_text = google_services.speech_to_text(primary_speech)
            if not transcribed_text:
                return voice_assistant_pb2.AudioResponse(
                    success=False,
                    error_message="Failed to transcribe speech",
                    session_id=request.session_id
                )
            
            logger.info(f"Transcribed text: {transcribed_text}")
            
            # Step 4: Get conversation history for context
            db = SessionLocal()
            try:
                conversation_history = db.query(ConversationRecord).filter(
                    ConversationRecord.user_id == request.user_id,
                    ConversationRecord.session_id == request.session_id
                ).order_by(ConversationRecord.timestamp.desc()).limit(5).all()
                
                # Step 5: Process with LLM
                llm_response = llm_processor.process_text(
                    transcribed_text, 
                    request.user_id, 
                    request.session_id,
                    conversation_history
                )
                
                if not llm_response:
                    llm_response = "I'm sorry, I couldn't process your request."
                
                logger.info(f"LLM response: {llm_response}")
                
                # Step 6: Text-to-Speech using Google Cloud TTS
                response_audio = google_services.text_to_speech(llm_response)
                if not response_audio:
                    return voice_assistant_pb2.AudioResponse(
                        success=False,
                        error_message="Failed to generate speech response",
                        session_id=request.session_id,
                        text_response=llm_response,
                        transcribed_text=transcribed_text
                    )
                
                # Step 7: Save to database (both audio and text)
                conversation_record = ConversationRecord(
                    id=str(uuid.uuid4()),
                    user_id=request.user_id,
                    session_id=request.session_id,
                    audio_input=request.audio_data,
                    text_input=transcribed_text,
                    text_response=llm_response,
                    audio_response=response_audio,
                    timestamp=datetime.utcnow(),
                    sample_rate=request.sample_rate,
                    audio_format=voice_assistant_pb2.AudioFormat.Name(request.format).lower()
                )
                
                db.add(conversation_record)
                
                # Update session activity
                session = db.query(UserSession).filter(
                    UserSession.session_id == request.session_id
                ).first()
                
                if session:
                    session.last_activity = datetime.utcnow()
                else:
                    new_session = UserSession(
                        session_id=request.session_id,
                        user_id=request.user_id,
                        created_at=datetime.utcnow(),
                        last_activity=datetime.utcnow(),
                        is_active=1
                    )
                    db.add(new_session)
                
                db.commit()
                
                # Step 8: Return complete response
                return voice_assistant_pb2.AudioResponse(
                    audio_data=response_audio,
                    text_response=llm_response,
                    transcribed_text=transcribed_text,
                    session_id=request.session_id,
                    format=request.format,
                    sample_rate=request.sample_rate,
                    success=True
                )
                
            except Exception as db_error:
                db.rollback()
                logger.error(f"Database error: {db_error}")
                # Still return the response even if DB save fails
                return voice_assistant_pb2.AudioResponse(
                    audio_data=response_audio if 'response_audio' in locals() else b"",
                    text_response=llm_response if 'llm_response' in locals() else "Database error occurred",
                    transcribed_text=transcribed_text if 'transcribed_text' in locals() else "",
                    session_id=request.session_id,
                    format=request.format,
                    sample_rate=request.sample_rate,
                    success=True,
                    error_message=f"Response generated but database save failed: {str(db_error)}"
                )
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in ProcessVoice: {e}")
            return voice_assistant_pb2.AudioResponse(
                success=False,
                error_message=f"Internal server error: {str(e)}",
                session_id=request.session_id
            )
    
    def StreamVoice(self, request_iterator, context):
        """
        Streaming voice processing for real-time conversation
        """
        try:
            session_id = None
            audio_buffer = io.BytesIO()
            sequence_numbers = []
            
            for chunk in request_iterator:
                if session_id is None:
                    session_id = chunk.session_id
                    logger.info(f"Starting stream for session: {session_id}")
                
                # Buffer the audio chunks
                audio_buffer.write(chunk.chunk_data)
                sequence_numbers.append(chunk.sequence_number)
                
                # If this is the final chunk, process the complete audio
                if chunk.is_final:
                    logger.info(f"Processing final chunk for session: {session_id}")
                    
                    # Get complete audio data
                    complete_audio = audio_buffer.getvalue()
                    
                    # Create a ProcessVoice request and process it
                    audio_request = voice_assistant_pb2.AudioRequest(
                        audio_data=complete_audio,
                        session_id=session_id,
                        format=voice_assistant_pb2.AudioFormat.WAV,
                        sample_rate=16000,
                        user_id="stream_user"  # Default for streaming
                    )
                    
                    # Process through the main pipeline
                    response = self.ProcessVoice(audio_request, context)
                    
                    # Convert response to streaming chunks
                    if response.success and response.audio_data:
                        # Split audio into chunks for streaming
                        chunk_size = 4096  # 4KB chunks
                        audio_data = response.audio_data
                        
                        for i in range(0, len(audio_data), chunk_size):
                            chunk_data = audio_data[i:i + chunk_size]
                            is_final_chunk = (i + chunk_size) >= len(audio_data)
                            
                            yield voice_assistant_pb2.AudioChunk(
                                chunk_data=chunk_data,
                                session_id=session_id,
                                is_final=is_final_chunk,
                                sequence_number=i // chunk_size
                            )
                    else:
                        # Send error chunk
                        yield voice_assistant_pb2.AudioChunk(
                            chunk_data=b"",
                            session_id=session_id,
                            is_final=True,
                            sequence_number=0
                        )
                    
                    # Reset buffer for next stream
                    audio_buffer = io.BytesIO()
                    sequence_numbers = []
                    
        except Exception as e:
            logger.error(f"Error in StreamVoice: {e}")
            if session_id:
                yield voice_assistant_pb2.AudioChunk(
                    chunk_data=b"",
                    session_id=session_id,
                    is_final=True,
                    sequence_number=-1  # Error indicator
                )
    
    def GetConversationHistory(self, request, context):
        """
        Retrieve conversation history for a user/session
        """
        try:
            db = SessionLocal()
            try:
                query = db.query(ConversationRecord)
                
                if request.user_id:
                    query = query.filter(ConversationRecord.user_id == request.user_id)
                
                if request.session_id:
                    query = query.filter(ConversationRecord.session_id == request.session_id)
                
                # Apply limit
                limit = request.limit if request.limit > 0 else 10
                records = query.order_by(ConversationRecord.timestamp.desc()).limit(limit).all()
                
                # Convert to protobuf format
                pb_records = []
                for record in records:
                    pb_record = voice_assistant_pb2.ConversationRecord(
                        id=record.id,
                        user_id=record.user_id,
                        session_id=record.session_id,
                        audio_input=record.audio_input,
                        text_input=record.text_input,
                        text_response=record.text_response,
                        audio_response=record.audio_response,
                        timestamp=int(record.timestamp.timestamp())
                    )
                    pb_records.append(pb_record)
                
                return voice_assistant_pb2.HistoryResponse(records=pb_records)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in GetConversationHistory: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to retrieve conversation history: {str(e)}")
            return voice_assistant_pb2.HistoryResponse()


def serve():
    """
    Start the gRPC server
    """
    # Create server with thread pool
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add servicer to server
    voice_assistant_pb2_grpc.add_VoiceAssistantServicer_to_server(
        VoiceAssistantServicer(), server
    )
    
    # Configure server address
    listen_addr = '0.0.0.0:50051'
    server.add_insecure_port(listen_addr)
    
    # Start server
    server.start()
    logger.info(f"Voice Assistant gRPC server started on {listen_addr}")
    logger.info("Server is ready to accept connections...")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(0)


if __name__ == '__main__':
    # Ensure database tables are created
    from models import create_tables
    create_tables()
    
    # Start the server
    serve()