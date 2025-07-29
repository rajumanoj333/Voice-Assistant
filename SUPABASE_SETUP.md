# Supabase Integration Setup Guide

This guide will help you set up Supabase as the database store for your Voice Assistant application.

## 🚀 Quick Start

Your Supabase project is already configured with the following credentials:

- **Project URL**: `https://czqnzosfhqthjjblkmfh.supabase.co`
- **API Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN6cW56b3NmaHF0aGpqYmxrbWZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3ODQ2MzcsImV4cCI6MjA2OTM2MDYzN30.MvJYLqKfy4lzkdmQLAm6QHl8weKTsQ1zZMtJEDT0BVI`

## 📋 Setup Steps

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file has been updated to include the Supabase Python client.

### 2. Environment Configuration

The `.env` file has been created with your Supabase credentials:

```env
SUPABASE_URL=https://czqnzosfhqthjjblkmfh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN6cW56b3NmaHF0aGpqYmxrbWZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3ODQ2MzcsImV4cCI6MjA2OTM2MDYzN30.MvJYLqKfy4lzkdmQLAm6QHl8weKTsQ1zZMtJEDT0BVI
```

### 3. Database Schema Setup

1. Go to your Supabase dashboard: https://app.supabase.com/project/czqnzosfhqthjjblkmfh
2. Navigate to the SQL Editor
3. Copy and paste the contents of `supabase_schema.sql` into the SQL Editor
4. Execute the script to create the necessary tables and indexes

The schema includes:
- `conversation_records` table for storing voice conversations
- `user_sessions` table for managing user sessions
- Proper indexes for optimal performance
- Row Level Security (RLS) policies for data protection

### 4. Test the Integration

Run the test script to verify everything is working:

```bash
python test_supabase.py
```

This will test:
- ✅ Database connection
- ✅ Session creation and retrieval
- ✅ Conversation record creation and retrieval
- ✅ Conversation history queries
- ✅ Session activity updates

## 🏗️ Architecture

The application now supports both Supabase and PostgreSQL with automatic fallback:

```
Application Layer
├── FastAPI endpoints (main.py)
├── gRPC server (grpc_server.py)
└── Data Services
    ├── ConversationService
    ├── SessionService
    └── Supabase Client (supabase_client.py)
```

### Key Files

- **`supabase_client.py`**: Supabase client wrapper with all database operations
- **`models.py`**: Updated with service classes that support both Supabase and PostgreSQL
- **`main.py`**: FastAPI application updated to use the new services
- **`supabase_schema.sql`**: Database schema for Supabase setup
- **`test_supabase.py`**: Comprehensive test suite

## 🔧 API Endpoints

The application now includes these Supabase-enabled endpoints:

### Core Endpoints
- `POST /process-text/` - Process text input with LLM
- `POST /upload-audio/` - Upload and process audio files
- `WebSocket /ws/audio` - Real-time audio processing

### Data Access Endpoints
- `GET /conversation-history/{user_id}` - Get conversation history
- `GET /session/{session_id}` - Get session information
- `GET /health` - Health check with database status

### Example Usage

```bash
# Process text and save to Supabase
curl -X POST "http://localhost:8000/process-text/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Hello, how are you?"

# Get conversation history
curl "http://localhost:8000/conversation-history/default_user?limit=10"

# Health check
curl "http://localhost:8000/health"
```

## 🔒 Security Features

### Row Level Security (RLS)
- Users can only access their own conversation records
- Sessions are protected by user ownership
- Anonymous access policies available for development

### Data Storage
- Audio data is stored as hex strings for efficient storage
- Timestamps use PostgreSQL's TIMESTAMPTZ for proper timezone handling
- Indexes optimize query performance

## 🚀 Running the Application

### Start the FastAPI Server
```bash
python main.py
```

### Start the gRPC Server
```bash
python grpc_server.py
```

### Access the API Documentation
Visit: http://localhost:8000/docs

## 🧪 Testing

### Run Integration Tests
```bash
python test_supabase.py
```

### Manual Testing
1. Visit http://localhost:8000/health to check database status
2. Use the `/process-text/` endpoint to create test conversations
3. Check the conversation history via `/conversation-history/{user_id}`

## 🔄 Migration from PostgreSQL

The application maintains backward compatibility:

1. **Automatic Detection**: The app detects if Supabase is available
2. **Graceful Fallback**: Falls back to PostgreSQL if Supabase is unavailable
3. **Service Layer**: Both databases use the same service interface
4. **Zero Downtime**: Can switch between databases without code changes

## 📊 Monitoring

### Database Status
Check the health endpoint for real-time database status:
```json
{
  "status": "healthy",
  "database": "connected",
  "supabase_available": true
}
```

### Logs
The application logs all database operations for debugging:
- Connection status
- Query execution
- Error handling
- Performance metrics

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify SUPABASE_URL and SUPABASE_KEY in .env
   - Check network connectivity
   - Ensure Supabase project is active

2. **RLS Policy Errors**
   - Review the RLS policies in supabase_schema.sql
   - For development, temporarily enable anonymous access
   - Ensure user authentication is properly configured

3. **Import Errors**
   - Run `pip install supabase>=2.3.0`
   - Check Python path and virtual environment

### Debug Mode
Set environment variable for detailed logging:
```bash
export DEBUG=1
python main.py
```

## 🔮 Next Steps

1. **Authentication**: Integrate Supabase Auth for user management
2. **Real-time**: Use Supabase Realtime for live conversation updates
3. **Storage**: Use Supabase Storage for large audio files
4. **Analytics**: Implement conversation analytics and insights
5. **Scaling**: Configure connection pooling for production

## 📚 Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase/supabase-py)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🎉 Success!

Your Voice Assistant is now powered by Supabase! The integration provides:

- ✅ Scalable cloud database
- ✅ Real-time capabilities
- ✅ Built-in authentication
- ✅ Automatic backups
- ✅ Global CDN
- ✅ Row-level security

Enjoy building with Supabase! 🚀