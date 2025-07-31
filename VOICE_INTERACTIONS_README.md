# Voice Interactions Table Guide

## Overview

The `voice_interactions` table is designed to store complete voice interaction data for your voice assistant application. It provides a structured way to record and analyze voice conversations between users and your AI assistant.

## Table Schema

```sql
CREATE TABLE IF NOT EXISTS voice_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audio_file_url TEXT NOT NULL,         -- URL to the audio file in Supabase Storage
    transcript TEXT NOT NULL,             -- Audio transcript
    llm_response TEXT NOT NULL,           -- LLM response text
    created_at TIMESTAMPTZ DEFAULT NOW()  -- Timestamp
);
```

### Fields Explained

- **`id`**: Unique identifier for each voice interaction (auto-generated UUID)
- **`audio_file_url`**: URL pointing to the audio file stored in Supabase Storage
- **`transcript`**: Text transcript of the user's speech
- **`llm_response`**: The AI assistant's response to the user's input
- **`created_at`**: Timestamp when the interaction was recorded

## Setup Instructions

### 1. Database Setup

Run the updated schema in your Supabase SQL Editor:

```bash
# Copy the contents of supabase_schema.sql and run it in Supabase
# The file now includes the voice_interactions table
```

### 2. Verify Setup

Test that the table was created correctly:

```bash
python3 setup_supabase_schema.py
python3 test_voice_interactions.py
```

## Usage Examples

### Basic Usage

```python
from models import voice_interaction_service

# Create a new voice interaction
interaction = voice_interaction_service.create_voice_interaction(
    audio_file_url="https://supabase.com/storage/v1/object/public/audio/recording.wav",
    transcript="Hello, how can you help me today?",
    llm_response="I'm here to help! I can assist you with various tasks. What would you like to know?"
)

# Retrieve an interaction
interaction = voice_interaction_service.get_voice_interaction("interaction-id-here")

# Get all interactions with pagination
interactions = voice_interaction_service.get_voice_interactions(limit=20, offset=0)

# Update an interaction
updated = voice_interaction_service.update_voice_interaction(
    "interaction-id-here",
    {
        'transcript': 'Updated transcript',
        'llm_response': 'Updated response'
    }
)

# Delete an interaction
success = voice_interaction_service.delete_voice_interaction("interaction-id-here")
```

### Integration with Voice Processing

```python
def process_voice_input(audio_data, user_id):
    """Complete voice processing workflow"""
    
    # 1. Upload audio to Supabase Storage
    audio_url = upload_audio_to_storage(audio_data)
    
    # 2. Transcribe audio using speech-to-text service
    transcript = transcribe_audio(audio_data)
    
    # 3. Generate LLM response
    llm_response = generate_llm_response(transcript)
    
    # 4. Store the complete interaction
    interaction = voice_interaction_service.create_voice_interaction(
        audio_file_url=audio_url,
        transcript=transcript,
        llm_response=llm_response
    )
    
    return interaction
```

### Analytics and Monitoring

```python
def analyze_voice_interactions():
    """Analyze voice interaction patterns"""
    
    # Get recent interactions
    interactions = voice_interaction_service.get_voice_interactions(limit=100)
    
    # Calculate statistics
    total_interactions = len(interactions)
    avg_transcript_length = sum(len(i['transcript']) for i in interactions) / total_interactions
    avg_response_length = sum(len(i['llm_response']) for i in interactions) / total_interactions
    
    print(f"Total interactions: {total_interactions}")
    print(f"Average transcript length: {avg_transcript_length:.0f} characters")
    print(f"Average response length: {avg_response_length:.0f} characters")
    
    return {
        'total_interactions': total_interactions,
        'avg_transcript_length': avg_transcript_length,
        'avg_response_length': avg_response_length
    }
```

## API Reference

### VoiceInteractionService

The service provides the following methods:

#### `create_voice_interaction(audio_file_url, transcript, llm_response)`
Creates a new voice interaction record.

**Parameters:**
- `audio_file_url` (str): URL to the audio file in Supabase Storage
- `transcript` (str): Text transcript of the user's speech
- `llm_response` (str): The AI assistant's response

**Returns:** Dictionary containing the created interaction data

#### `get_voice_interaction(interaction_id)`
Retrieves a specific voice interaction by ID.

**Parameters:**
- `interaction_id` (str): The UUID of the interaction

**Returns:** Dictionary containing the interaction data or None if not found

#### `get_voice_interactions(limit=50, offset=0)`
Retrieves multiple voice interactions with pagination.

**Parameters:**
- `limit` (int): Maximum number of interactions to return (default: 50)
- `offset` (int): Number of interactions to skip (default: 0)

**Returns:** List of interaction dictionaries

#### `update_voice_interaction(interaction_id, updates)`
Updates specific fields of a voice interaction.

**Parameters:**
- `interaction_id` (str): The UUID of the interaction
- `updates` (dict): Dictionary of fields to update

**Returns:** Dictionary containing the updated interaction data or None if not found

#### `delete_voice_interaction(interaction_id)`
Deletes a voice interaction.

**Parameters:**
- `interaction_id` (str): The UUID of the interaction

**Returns:** Boolean indicating success

## Database Operations

### Direct Supabase Client Usage

```python
from supabase_client import supabase_client

# Create interaction
result = supabase_client.create_voice_interaction({
    'audio_file_url': 'https://example.com/audio.wav',
    'transcript': 'User transcript',
    'llm_response': 'AI response'
})

# Get interaction
interaction = supabase_client.get_voice_interaction('interaction-id')

# Get all interactions
interactions = supabase_client.get_voice_interactions(limit=20, offset=0)

# Update interaction
updated = supabase_client.update_voice_interaction('interaction-id', {
    'transcript': 'Updated transcript'
})

# Delete interaction
success = supabase_client.delete_voice_interaction('interaction-id')
```

## Security and Permissions

The table includes Row Level Security (RLS) policies:

- **Development**: Anonymous access is allowed for testing
- **Production**: Should be configured with proper user-based policies

### Recommended Production Policies

```sql
-- Replace the anonymous access policies with user-specific ones
CREATE POLICY "Users can view their own voice interactions" ON voice_interactions
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert their own voice interactions" ON voice_interactions
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);
```

## Testing

### Run Tests

```bash
# Test the voice interactions functionality
python3 test_voice_interactions.py

# Run the integration example
python3 voice_interactions_example.py

# Run comprehensive verification
python3 setup_verification.py
```

### Test Coverage

The tests cover:
- ✅ Creating voice interactions
- ✅ Retrieving voice interactions
- ✅ Updating voice interactions
- ✅ Deleting voice interactions
- ✅ Pagination and listing
- ✅ Error handling
- ✅ Database connection

## Integration with Existing Code

### Files Modified

1. **`supabase_schema.sql`**: Added voice_interactions table definition
2. **`supabase_client.py`**: Added voice interaction CRUD operations
3. **`models.py`**: Added VoiceInteraction model and VoiceInteractionService
4. **`setup_supabase_schema.py`**: Updated to include voice_interactions verification
5. **`setup_verification.py`**: Updated to check voice_interactions table

### New Files Created

1. **`test_voice_interactions.py`**: Comprehensive test suite
2. **`voice_interactions_example.py`**: Integration examples
3. **`VOICE_INTERACTIONS_README.md`**: This documentation

## Best Practices

### 1. Audio File Management
- Store audio files in Supabase Storage with organized folder structure
- Use consistent naming conventions for audio files
- Implement cleanup for old audio files

### 2. Data Privacy
- Implement proper user authentication
- Add user_id field if needed for multi-user applications
- Consider data retention policies

### 3. Performance
- Use pagination for large datasets
- Implement caching for frequently accessed interactions
- Monitor database performance

### 4. Error Handling
- Always handle database connection errors
- Implement retry logic for failed operations
- Log errors for debugging

## Troubleshooting

### Common Issues

1. **Table not found**: Run the schema setup again
2. **Connection errors**: Check Supabase credentials in .env file
3. **Permission errors**: Verify RLS policies are configured correctly
4. **Import errors**: Ensure all dependencies are installed

### Debug Commands

```bash
# Test database connection
python3 -c "from supabase_client import supabase_client; print(supabase_client.test_connection())"

# Check table exists
python3 setup_supabase_schema.py

# Run comprehensive tests
python3 test_voice_interactions.py
```

## Next Steps

1. **Integrate with main application**: Add voice_interaction_service to your voice processing pipeline
2. **Add audio upload functionality**: Implement Supabase Storage integration
3. **Connect speech-to-text**: Integrate with Google Speech-to-Text or similar service
4. **Implement analytics**: Add monitoring and analysis features
5. **Add user authentication**: Implement proper user management
6. **Optimize performance**: Add caching and indexing as needed

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test files for usage examples
3. Verify your Supabase setup and credentials
4. Check the comprehensive verification script