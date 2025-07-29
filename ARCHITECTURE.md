# Voice Assistant Architecture

## System Overview

The Voice Assistant is a comprehensive audio-to-audio conversation system that processes voice input through multiple stages to provide intelligent responses. The system is built using gRPC for efficient communication and integrates several AI services.

## Architecture Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Audio Input   │───▶│   SileroVAD      │───▶│ Speech Segments │
│   (WAV/MP3)     │    │   Processor      │    │   Extraction    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐             ▼
│  Audio Output   │◀───│  Google Cloud    │    ┌─────────────────┐
│   (Synthesized) │    │  Text-to-Speech  │◀───│ Google Cloud    │
└─────────────────┘    └──────────────────┘    │ Speech-to-Text  │
         │                                      └─────────────────┘
         ▼                                               │
┌─────────────────┐    ┌──────────────────┐             ▼
│   Database      │◀───│   gRPC Server    │    ┌─────────────────┐
│   Storage       │    │   (Coordinator)  │◀───│  Text Analysis  │
│ (Audio + Text)  │    └──────────────────┘    │   (OpenAI LLM)  │
└─────────────────┘                            └─────────────────┘
```

## Component Details

### 1. SileroVAD Processor (`vad_processor.py`)
- **Purpose**: Voice Activity Detection and speech segment extraction
- **Technology**: Silero VAD neural network
- **Functions**:
  - Detect speech presence in audio
  - Extract speech segments from audio
  - Filter out silence and noise
- **Input**: Raw audio bytes
- **Output**: Clean speech segments

### 2. Google Cloud Services (`google_services.py`)
- **Speech-to-Text**: Converts audio to text transcription
- **Text-to-Speech**: Synthesizes natural-sounding speech from text
- **Features**:
  - High-quality neural voices
  - Multiple language support
  - Confidence scoring
  - Word-level timestamps

### 3. LLM Processor (`llm_processor.py`)
- **Purpose**: Intelligent conversation processing
- **Technology**: OpenAI GPT models
- **Functions**:
  - Process user queries
  - Maintain conversation context
  - Generate appropriate responses
  - Intent analysis and entity extraction

### 4. Database Layer (`models.py`)
- **Technology**: PostgreSQL with SQLAlchemy ORM
- **Tables**:
  - `conversation_records`: Complete conversation history
  - `user_sessions`: Session management and tracking
- **Storage**: Both audio and text data for complete records

### 5. gRPC Server (`grpc_server.py`)
- **Purpose**: Main orchestration and API layer
- **Protocol**: gRPC with Protocol Buffers
- **Services**:
  - `ProcessVoice`: Single request processing
  - `StreamVoice`: Real-time streaming
  - `GetConversationHistory`: History retrieval

## Data Flow

### Single Voice Request Flow

1. **Client** sends `AudioRequest` with audio data
2. **SileroVAD** detects and extracts speech segments
3. **Google STT** transcribes speech to text
4. **Database** retrieves conversation history for context
5. **LLM Processor** generates intelligent response
6. **Google TTS** synthesizes response audio
7. **Database** stores complete conversation record
8. **Server** returns `AudioResponse` with audio and metadata

### Streaming Voice Request Flow

1. **Client** streams `AudioChunk` messages
2. **Server** buffers chunks until final chunk received
3. **Processing** follows same pipeline as single request
4. **Response** is streamed back as `AudioChunk` messages

## Protocol Buffers Schema

```protobuf
service VoiceAssistant {
    rpc ProcessVoice(AudioRequest) returns (AudioResponse);
    rpc StreamVoice(stream AudioChunk) returns (stream AudioChunk);
    rpc GetConversationHistory(HistoryRequest) returns (HistoryResponse);
}

message AudioRequest {
    bytes audio_data = 1;
    string session_id = 2;
    AudioFormat format = 3;
    int32 sample_rate = 4;
    string user_id = 5;
}

message AudioResponse {
    bytes audio_data = 1;
    string text_response = 2;
    string transcribed_text = 3;
    string session_id = 4;
    AudioFormat format = 5;
    int32 sample_rate = 6;
    bool success = 7;
    string error_message = 8;
}
```

## Error Handling

### Graceful Degradation
- If VAD fails: Process entire audio
- If STT fails: Return error with context
- If LLM fails: Return fallback response
- If TTS fails: Return text-only response
- If DB fails: Continue processing but log error

### Retry Logic
- Network failures: Automatic retry with exponential backoff
- Service timeouts: Configurable timeout values
- Rate limiting: Respect API rate limits

## Performance Considerations

### Audio Processing
- Recommended format: 16-bit PCM WAV at 16kHz
- Chunk size: 4KB for streaming
- Buffer management: Efficient memory usage

### Database Optimization
- Indexed queries on user_id and session_id
- Connection pooling for concurrent requests
- Binary data compression for audio storage

### Caching
- LLM responses for common queries
- TTS audio for repeated phrases
- Session data for active conversations

## Security

### Authentication
- API key validation for external services
- Session-based user identification
- Rate limiting per user/IP

### Data Protection
- Encrypted database connections
- Secure credential management
- Audio data encryption at rest

## Scalability

### Horizontal Scaling
- Stateless server design
- Load balancer compatible
- Database connection pooling

### Resource Management
- Thread pool for concurrent requests
- Memory-efficient audio processing
- Async I/O where applicable

## Configuration

### Environment Variables
```bash
# Core Services
OPENAI_API_KEY=your_openai_key
DATABASE_URL=postgresql://user:pass@host/db
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Server Configuration
GRPC_PORT=50051
LOG_LEVEL=INFO

# Model Configuration
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=150
TEMPERATURE=0.7
```

### Audio Configuration
- Sample Rate: 16000 Hz (recommended)
- Format: WAV (LINEAR16 encoding)
- Channels: Mono (1 channel)
- Bit Depth: 16-bit

## Monitoring and Logging

### Metrics
- Request latency per component
- Success/failure rates
- Audio processing times
- Database query performance

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request tracing with session IDs
- Performance metrics logging

## Deployment

### Development
```bash
python setup.py        # Initial setup
python start.py --grpc  # Start server
python start.py --demo  # Test client
```

### Production
- Docker containerization
- Environment-specific configurations
- Health check endpoints
- Graceful shutdown handling

## Future Enhancements

### Planned Features
- Multi-language support
- Voice cloning capabilities
- Real-time streaming optimization
- Advanced conversation memory
- Custom wake word detection

### Integration Opportunities
- WebRTC for browser clients
- Mobile SDK development
- IoT device integration
- Third-party service plugins