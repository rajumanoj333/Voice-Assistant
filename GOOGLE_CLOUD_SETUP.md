# Google Cloud Services Setup Guide

This guide will help you set up Google Cloud Speech-to-Text and Text-to-Speech services for the Voice Assistant application.

## 🎯 Overview

The Voice Assistant uses Google Cloud services for:
- **Speech-to-Text**: Converting audio to text
- **Text-to-Speech**: Converting text responses to audio

## 📋 Prerequisites

- Google Cloud account (free tier available)
- Python 3.8+ installed
- Basic familiarity with command line

## 🚀 Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "voice-assistant")
4. Click "Create"

### 2. Enable Required APIs

1. In your project, go to "APIs & Services" → "Library"
2. Search for and enable these APIs:
   - **Speech-to-Text API**
   - **Text-to-Speech API**

### 3. Create Service Account

1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Enter details:
   - **Name**: `voice-assistant-service`
   - **Description**: `Service account for Voice Assistant`
4. Click "Create and Continue"

### 4. Assign Permissions

1. Add these roles to your service account:
   - **Speech-to-Text User**
   - **Text-to-Speech User**
2. Click "Continue" → "Done"

### 5. Create and Download Key

1. Click on your service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select "JSON" format
5. Click "Create"
6. Save the downloaded JSON file securely

### 6. Configure Environment

#### Option A: Environment Variable (Recommended)

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

#### Option B: .env File

Create or update your `.env` file:

```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
```

### 7. Install Dependencies

```bash
pip install google-cloud-speech google-cloud-texttospeech
```

## 🔧 Configuration Options

### Voice Selection

The application uses these default voices:
- **Speech-to-Text**: English (US) with enhanced models
- **Text-to-Speech**: `en-US-Neural2-D` (Neural voice)

### Supported Audio Formats

- **Input**: WAV, MP3, M4A (16kHz mono recommended)
- **Output**: WAV (16kHz, 16-bit PCM)

## 🧪 Testing Your Setup

### 1. Test via API

```bash
curl http://localhost:8000/services/test
```

### 2. Test via Streamlit

1. Start the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```
2. Check the sidebar for service status
3. Click "Test Services" button

### 3. Test via Python

```python
from google_services import google_services

# Check status
status = google_services.get_service_status()
print(status)

# Test services
results = google_services.test_services()
print(results)
```

## 🚨 Troubleshooting

### Common Issues

#### 1. "Google Cloud credentials not configured"

**Solution:**
- Verify `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- Check that the JSON file exists and is readable
- Restart your application after setting the environment variable

#### 2. "Invalid JSON format in credentials file"

**Solution:**
- Download a fresh copy of the service account key
- Verify the file is not corrupted
- Check file permissions

#### 3. "Permission denied" errors

**Solution:**
- Ensure the service account has the correct roles
- Verify the APIs are enabled in your project
- Check billing is enabled (required for API usage)

#### 4. "API not enabled" errors

**Solution:**
- Go to Google Cloud Console → APIs & Services → Library
- Search for and enable:
  - Speech-to-Text API
  - Text-to-Speech API

#### 5. "Quota exceeded" errors

**Solution:**
- Check your Google Cloud billing
- Review usage quotas in Google Cloud Console
- Consider upgrading your plan if needed

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Service Status Check

```python
from google_services import google_services

# Get detailed status
status = google_services.get_service_status()
print(json.dumps(status, indent=2))

# Test individual services
test_results = google_services.test_services()
print(json.dumps(test_results, indent=2))
```

## 💰 Cost Considerations

### Free Tier Limits

- **Speech-to-Text**: 60 minutes per month
- **Text-to-Speech**: 4 million characters per month

### Pricing (after free tier)

- **Speech-to-Text**: $0.006 per 15 seconds
- **Text-to-Speech**: $4.00 per 1 million characters

### Cost Optimization Tips

1. Use appropriate audio quality (16kHz is sufficient)
2. Implement caching for repeated text-to-speech requests
3. Monitor usage in Google Cloud Console
4. Set up billing alerts

## 🔒 Security Best Practices

1. **Never commit credentials to version control**
2. **Use environment variables for credentials**
3. **Restrict service account permissions**
4. **Regularly rotate service account keys**
5. **Monitor API usage for unusual activity**

## 📊 Monitoring and Logging

### Google Cloud Console

- Go to "APIs & Services" → "Dashboard"
- Monitor API usage and errors
- Set up alerts for quota limits

### Application Logs

The application provides detailed logging:
- Service initialization status
- API call results
- Error details with suggestions

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

## 🆘 Getting Help

### Application Issues

1. Check the application logs
2. Use the `/services/status` endpoint
3. Run the service tests
4. Review this troubleshooting guide

### Google Cloud Issues

1. Check [Google Cloud Documentation](https://cloud.google.com/speech/docs)
2. Review [Google Cloud Status](https://status.cloud.google.com/)
3. Contact Google Cloud Support

### Community Support

- GitHub Issues
- Stack Overflow
- Google Cloud Community

## 📝 Example Configuration

### Complete .env File

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

### Service Account Key Structure

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "voice-assistant-service@your-project-id.iam.gserviceaccount.com",
  "client_id": "client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/voice-assistant-service%40your-project-id.iam.gserviceaccount.com"
}
```

## ✅ Verification Checklist

- [ ] Google Cloud project created
- [ ] Speech-to-Text API enabled
- [ ] Text-to-Speech API enabled
- [ ] Service account created
- [ ] Proper roles assigned
- [ ] Service account key downloaded
- [ ] Environment variable set
- [ ] Dependencies installed
- [ ] Services tested successfully
- [ ] Application running without errors

## 🎉 Success!

Once all steps are completed, your Voice Assistant will have:
- ✅ High-quality speech recognition
- ✅ Natural-sounding text-to-speech
- ✅ Comprehensive error handling
- ✅ Detailed status monitoring
- ✅ Cost-effective usage

Your users will enjoy a smooth, professional voice interaction experience!