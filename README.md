# Voice Assistant with Supabase Database

A comprehensive voice assistant system powered by **Supabase** that integrates:
- **🗄️ Supabase** for cloud database and real-time features
- **🎤 SileroVAD** for voice activity detection
- **🗣️ Google Cloud Speech-to-Text** for transcription
- **🤖 OpenAI GPT** for intelligent responses
- **🔊 Google Cloud Text-to-Speech** for audio synthesis
- **⚡ gRPC** for efficient client-server communication
- **🌐 FastAPI** for REST API endpoints

## ✨ Features

🎤 **Voice Activity Detection**: Uses SileroVAD to detect and extract speech segments  
🗣️ **Speech Recognition**: Google Cloud STT for accurate transcription  
🤖 **AI Processing**: OpenAI GPT for intelligent conversation  
🔊 **Speech Synthesis**: Google Cloud TTS for natural-sounding responses  
💾 **Cloud Database**: Supabase for scalable conversation storage  
⚡ **gRPC Communication**: Efficient binary protocol for audio streaming  
🔄 **Streaming Support**: Real-time audio processing capabilities  
🔒 **Security**: Row-level security with Supabase  

## 🏗️ Architecture

```
Audio Input → SileroVAD → Google STT → OpenAI LLM → Google TTS → Audio Output
                ↓                                                      ↓
           Supabase ←←←←←←←←←← Conversation Storage ←←←←←←←←←←←←←←←←←←←
```

## 🚀 Quick Start Guide

### Prerequisites

- Python 3.8+
- Supabase account (free tier available)
- OpenAI API key
- Google Cloud account with Speech & Text-to-Speech APIs enabled

### 1. Clone and Setup Environment

#### Option A: Automated Setup (Recommended)
```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd voice-assistant

# Run the automated setup script
./setup.sh
```

#### Option B: Manual Setup
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Supabase Database Setup

#### Option A: Use Pre-configured Supabase Project (Recommended)
The project comes with a pre-configured Supabase project. The credentials are already in the `.env` file.

#### Option B: Create Your Own Supabase Project
1. Go to [supabase.com](https://supabase.com) and create a new project
2. Copy your project URL and anon key
3. Update the `.env` file with your credentials
4. Run the SQL schema in your Supabase dashboard

**Setting up the database schema:**

*Option A: Using the Setup Helper (Recommended)*
```bash
python3 setup_supabase_schema.py
```

*Option B: Manual Setup*
1. Go to your Supabase dashboard → SQL Editor
2. Copy the contents of `supabase_schema.sql`
3. Paste and execute the SQL script
4. This creates the necessary tables, indexes, and security policies

### 3. Configure Environment Variables

The `.env` file is already created. Update the following variables:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=your_actual_openai_api_key_here

# Required: Google Cloud Service Account
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/google-service-account.json

# Supabase credentials (already configured)
SUPABASE_URL=https://czqnzosfhqthjjblkmfh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Google Cloud Setup

1. Create a Google Cloud project
2. Enable Speech-to-Text and Text-to-Speech APIs
3. Create a service account and download the JSON key file
4. Update `GOOGLE_APPLICATION_CREDENTIALS` in `.env` with the path to your JSON file

### 5. Verify Setup

Run the comprehensive setup verification script:

```bash
python3 setup_verification.py
```

This will check:
- ✅ Python version and dependencies
- ✅ Environment variables
- ✅ Project files
- ✅ Supabase connection
- ✅ Database schema
- ✅ Basic functionality

**Alternative:** Run the focused Supabase test:
```bash
python3 test_supabase.py
```

### 6. Generate gRPC Code (if needed)

```bash
python3 generate_grpc.py
```

## 🎯 Running the Application

### Method 1: FastAPI Server (Recommended for testing)

```bash
python3 main.py
```

The server starts on `http://localhost:8000`

**Available endpoints:**
- `GET /health` - Check system health and database status
- `POST /process-text/` - Process text input with LLM
- `POST /upload-audio/` - Upload and process audio files
- `GET /conversation-history/{user_id}` - Get conversation history
- `WebSocket /ws/audio` - Real-time audio processing

**API Documentation:** http://localhost:8000/docs

### Method 2: gRPC Server (For production/advanced usage)

```bash
python3 grpc_server.py
```

The gRPC server starts on `localhost:50051`

### Method 3: Client Examples

Run the comprehensive client demo:

```bash
python3 client_example.py
```

## 🧪 Testing & Verification

### Quick Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "supabase_available": true
}
```

### Test Text Processing

```bash
curl -X POST "http://localhost:8000/process-text/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Hello, how are you today?"
```

### View Conversation History

```bash
curl "http://localhost:8000/conversation-history/default_user?limit=5"
```

### Run Comprehensive Tests

```bash
# Test Supabase integration
python3 test_supabase.py

# Test the complete pipeline (if you have audio files)
python3 client_example.py
```

## 📁 Project Structure

```
voice-assistant/
├── 📄 README.md                 # This comprehensive guide
├── 📄 SUPABASE_SETUP.md         # Detailed Supabase setup
├── 📄 ARCHITECTURE.md           # System architecture details
├── 📄 SETUP_SUMMARY.md          # Quick setup completion status
├── 🔧 .env                      # Environment configuration
├── 📦 requirements.txt          # Python dependencies
├── 🗄️ supabase_schema.sql       # Database schema
├── 🔧 supabase_client.py        # Supabase client wrapper
├── 🧪 test_supabase.py          # Comprehensive test suite
├── ✅ setup_verification.py     # Complete setup verification
├── 🗄️ setup_supabase_schema.py  # Supabase schema setup helper
├── 🛠️ setup.sh                  # Automated setup script
├── 🚀 main.py                   # FastAPI server
├── 🌐 grpc_server.py            # gRPC server
├── 👤 client_example.py         # Client demonstration
├── 🧠 models.py                 # Database models & services
├── 🤖 llm_processor.py          # OpenAI LLM integration
├── 🎤 vad_processor.py          # Voice activity detection
├── ☁️ google_services.py        # Google Cloud services
├── 📡 voice_assistant.proto     # gRPC service definition
└── 🔧 generate_grpc.py          # gRPC code generator
```

## 🔧 Configuration

### Audio Requirements

- **Format**: WAV recommended (16-bit PCM)
- **Sample Rate**: 16000 Hz recommended
- **Channels**: Mono (1 channel)
- **Encoding**: LINEAR16

### Database Schema

The Supabase database includes:

1. **`conversation_records`**: Stores complete conversation data
   - Audio input/output (as hex strings)
   - Text input/responses
   - User and session tracking
   - Timestamps and metadata

2. **`user_sessions`**: Manages user sessions
   - Session lifecycle
   - Activity tracking
   - User association

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. Supabase Connection Error
```
❌ Supabase connection failed
```
**Solutions:**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check network connectivity
- Ensure Supabase project is active
- Run: `python test_supabase.py` for detailed diagnostics

#### 2. Database Schema Not Found
```
❌ Table 'conversation_records' doesn't exist
```
**Solutions:**
- Go to Supabase dashboard → SQL Editor
- Execute the contents of `supabase_schema.sql`
- Enable anonymous access policies for development (see schema file)

#### 3. OpenAI API Error
```
❌ OpenAI API key not found
```
**Solutions:**
- Set valid `OPENAI_API_KEY` in `.env`
- Verify API key has sufficient credits
- Check API key permissions

#### 4. Google Cloud Authentication Error
```
❌ Google Cloud credentials not found
```
**Solutions:**
- Download service account JSON from Google Cloud Console
- Set correct path in `GOOGLE_APPLICATION_CREDENTIALS`
- Ensure Speech-to-Text and Text-to-Speech APIs are enabled

#### 5. Import Errors
```
❌ ModuleNotFoundError: No module named 'supabase'
```
**Solutions:**
```bash
pip install -r requirements.txt
# Or specifically:
pip install supabase>=2.3.0
```

### Debug Mode

Enable detailed logging:
```bash
export DEBUG=1
python3 main.py
```

### Step-by-Step Verification

1. **Test Environment Variables:**
   ```bash
   python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Supabase URL:', os.getenv('SUPABASE_URL')[:30] + '...' if os.getenv('SUPABASE_URL') else 'Not set')"
   ```

2. **Test Supabase Connection:**
   ```bash
   python3 -c "from supabase_client import supabase_client; print('Connection:', 'OK' if supabase_client.test_connection() else 'Failed')"
   ```

3. **Test Database Schema:**
   ```bash
   python3 test_supabase.py
   ```

4. **Test API Server:**
   ```bash
   python3 main.py &
   curl http://localhost:8000/health
   ```

## 🚀 Production Deployment

### Environment Setup

1. **Set Production Environment Variables:**
   ```bash
   export SUPABASE_URL=your_production_supabase_url
   export SUPABASE_KEY=your_production_supabase_key
   export OPENAI_API_KEY=your_production_openai_key
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/production/credentials.json
   ```

2. **Remove Anonymous Access:**
   - Comment out anonymous policies in `supabase_schema.sql`
   - Implement proper user authentication

3. **Configure Row Level Security:**
   - Review and adjust RLS policies in Supabase dashboard
   - Test with authenticated users

### Deployment Options

- **Docker**: Build container with all dependencies
- **Cloud Run**: Deploy FastAPI server to Google Cloud Run
- **Heroku**: Use Heroku with Supabase add-on
- **VPS**: Deploy on any VPS with Python support

## 📚 API Reference

### REST API Endpoints

#### Health Check
```http
GET /health
```
Returns system status and database connectivity.

#### Process Text
```http
POST /process-text/
Content-Type: application/x-www-form-urlencoded

text=Your message here
```

#### Upload Audio
```http
POST /upload-audio/
Content-Type: multipart/form-data

file: audio_file.wav
```

#### Get Conversation History
```http
GET /conversation-history/{user_id}?limit=10&session_id=optional
```

### gRPC Services

See `voice_assistant.proto` for complete service definitions:
- `ProcessVoice`: Single audio request processing
- `StreamVoice`: Streaming audio processing
- `GetConversationHistory`: Retrieve conversation history

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

## 📄 License

This project is open source. Please check individual component licenses for Google Cloud, OpenAI, and Supabase services.

## 🆘 Support

Need help? Try these steps:

1. **Check this README** for common solutions
2. **Run diagnostics**: `python test_supabase.py`
3. **Enable debug mode**: Set `DEBUG=1` in `.env`
4. **Check logs** for detailed error messages
5. **Verify all credentials** are correctly set

For issues and questions, ensure all dependencies are properly installed and environment variables are correctly configured.

---

🎉 **Ready to go!** Your Voice Assistant with Supabase is now set up and ready for use!