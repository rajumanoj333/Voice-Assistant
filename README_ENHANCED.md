# 🗣️ Voice Assistant - Enhanced Edition

A comprehensive voice assistant application with **Google Cloud Speech-to-Text and Text-to-Speech** services, featuring enhanced error handling, user-friendly interfaces, and comprehensive monitoring.

## ✨ What's New in Enhanced Edition

### 🎯 Enhanced Google Cloud Integration
- **Comprehensive Error Handling**: Detailed error messages and troubleshooting guidance
- **Service Status Monitoring**: Real-time status of all Google Cloud services
- **Configuration Validation**: Automatic validation of credentials and setup
- **Fallback Mechanisms**: Graceful degradation when services are unavailable
- **Enhanced Logging**: Detailed logging for debugging and monitoring

### 🎨 Improved User Experience
- **Modern Streamlit Interface**: Beautiful, responsive UI with status indicators
- **Real-time Status Updates**: Live service status in the sidebar
- **Comprehensive Error Messages**: User-friendly error explanations
- **Processing Status Indicators**: Visual feedback during audio processing
- **Enhanced Conversation History**: Rich metadata and confidence scores

### 🔧 Better Developer Experience
- **Quick Start Script**: Automated setup and testing
- **Comprehensive Test Suite**: End-to-end testing of all services
- **Detailed Documentation**: Step-by-step setup guides
- **API Status Endpoints**: Health checks and service monitoring
- **Enhanced Logging**: Structured logging for debugging

## 🚀 Quick Start

### 1. Automated Setup (Recommended)

```bash
# Run the quick start script
python quick_start.py
```

This script will:
- ✅ Check Python version compatibility
- ✅ Install all dependencies
- ✅ Validate environment configuration
- ✅ Test Google Cloud services
- ✅ Guide you through starting the application

### 2. Manual Setup

#### Prerequisites
- Python 3.8+
- Google Cloud account
- OpenAI API key (optional)

#### Installation

```bash
# Clone the repository
git clone <repository-url>
cd voice-assistant

# Install dependencies
pip install -r requirements.txt

# Set up Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

# Test the setup
python test_google_services.py
```

#### Start the Application

```bash
# Start the FastAPI server
python main.py

# In another terminal, start the Streamlit app
streamlit run streamlit_app.py
```

## 📋 Features

### 🎤 Speech Processing
- **High-Quality Speech Recognition**: Powered by Google Cloud Speech-to-Text
- **Natural Text-to-Speech**: Google Cloud Text-to-Speech with neural voices
- **Multiple Audio Formats**: Support for WAV, MP3, M4A
- **Real-time Processing**: Streaming audio support
- **Confidence Scoring**: Quality metrics for transcriptions

### 🤖 AI Integration
- **OpenAI GPT Integration**: Advanced language processing
- **Conversation Memory**: Context-aware responses
- **Session Management**: Persistent conversation history
- **Customizable Responses**: Configurable AI behavior

### 🗄️ Data Management
- **Supabase Integration**: Cloud database for conversations
- **Session Tracking**: User session management
- **Conversation History**: Persistent storage of interactions
- **Metadata Storage**: Rich data about each interaction

### 🔍 Monitoring & Debugging
- **Service Health Checks**: Real-time service status
- **Comprehensive Logging**: Detailed operation logs
- **Error Tracking**: Detailed error reporting
- **Performance Metrics**: Processing time and quality metrics

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI Server │    │  Google Cloud   │
│                 │    │                  │    │                 │
│ • Audio Upload  │◄──►│ • REST API       │◄──►│ • Speech-to-Text│
│ • Text Input    │    │ • WebSocket      │    │ • Text-to-Speech│
│ • Status Display│    │ • Health Checks  │    │ • Neural Voices │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenAI GPT    │    │    Supabase      │    │   File System   │
│                 │    │                  │    │                 │
│ • LLM Processing│    │ • Conversations  │    │ • Audio Files   │
│ • Context Mgmt  │    │ • User Sessions  │    │ • Logs          │
│ • Response Gen  │    │ • Metadata       │    │ • Config        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with your configuration:

```env
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# Application
PORT=8000
```

### Google Cloud Setup

Follow the comprehensive guide in `GOOGLE_CLOUD_SETUP.md` for detailed setup instructions.

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Application information
- `GET /health` - Health check with service status
- `GET /services/status` - Detailed service status
- `GET /services/test` - Test all services

### Audio Processing
- `POST /upload-audio/` - Upload and process audio files
- `POST /process-text/` - Process text input with audio response
- `WS /ws/audio` - WebSocket for real-time audio

### Data Management
- `GET /conversation-history/{user_id}` - Get conversation history
- `GET /session/{session_id}` - Get session information

## 🧪 Testing

### Automated Test Suite

```bash
# Run comprehensive tests
python test_google_services.py
```

### Manual Testing

```bash
# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/services/status
curl http://localhost:8000/services/test
```

### Streamlit Testing

1. Start the Streamlit app
2. Check the sidebar for service status
3. Upload audio files or type text
4. Monitor processing status and results

## 🚨 Troubleshooting

### Common Issues

#### Google Cloud Services Not Working
1. **Check credentials**: Verify `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
2. **Validate JSON**: Ensure the service account key is valid JSON
3. **Enable APIs**: Make sure Speech-to-Text and Text-to-Speech APIs are enabled
4. **Check permissions**: Verify service account has proper roles
5. **Test connectivity**: Run `python test_google_services.py`

#### Audio Processing Issues
1. **Check format**: Use 16kHz mono WAV files for best results
2. **Verify size**: Ensure audio files are not empty or corrupted
3. **Check network**: Verify internet connectivity for cloud services
4. **Review logs**: Check application logs for detailed error messages

#### Application Not Starting
1. **Check dependencies**: Run `pip install -r requirements.txt`
2. **Verify Python version**: Ensure Python 3.8+ is installed
3. **Check ports**: Ensure ports 8000 and 8501 are available
4. **Review environment**: Verify all required environment variables are set

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. **Check logs**: Review application logs for error details
2. **Run tests**: Use `python test_google_services.py` for diagnostics
3. **Review documentation**: Check `GOOGLE_CLOUD_SETUP.md` for setup issues
4. **API status**: Use `/health` and `/services/status` endpoints

## 📈 Performance & Optimization

### Best Practices
- Use 16kHz mono audio for optimal performance
- Implement caching for repeated text-to-speech requests
- Monitor API usage to optimize costs
- Use appropriate audio quality settings

### Cost Optimization
- Google Cloud offers free tier with generous limits
- Monitor usage in Google Cloud Console
- Set up billing alerts
- Use appropriate voice models

## 🔒 Security

### Best Practices
- Never commit credentials to version control
- Use environment variables for sensitive data
- Restrict service account permissions
- Regularly rotate service account keys
- Monitor API usage for unusual activity

### Data Privacy
- Audio files are processed in memory
- No audio data is permanently stored
- Conversation history is stored in Supabase
- Implement data retention policies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Cloud for Speech-to-Text and Text-to-Speech services
- OpenAI for GPT language model integration
- Streamlit for the web interface framework
- FastAPI for the REST API framework
- Supabase for database services

## 📞 Support

- **Documentation**: Check the guides in this repository
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions on GitHub
- **Email**: Contact the maintainers for direct support

---

**🎉 Enjoy your enhanced Voice Assistant experience!**