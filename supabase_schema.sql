-- Supabase Schema Setup for Voice Assistant
-- Run these commands in the Supabase SQL Editor

-- Create conversation_records table
CREATE TABLE IF NOT EXISTS conversation_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    audio_input TEXT, -- Stored as hex string
    text_input TEXT NOT NULL,
    text_response TEXT NOT NULL,
    audio_response TEXT, -- Stored as hex string
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    sample_rate INTEGER DEFAULT 16000,
    audio_format TEXT DEFAULT 'wav'
);

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversation_records_user_id ON conversation_records(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_records_session_id ON conversation_records(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_records_timestamp ON conversation_records(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active) WHERE is_active = TRUE;

-- Enable Row Level Security (RLS) for security
ALTER TABLE conversation_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
-- Note: Adjust these policies based on your authentication setup

-- Policy for conversation_records - users can only access their own records
CREATE POLICY "Users can view their own conversation records" ON conversation_records
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert their own conversation records" ON conversation_records
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update their own conversation records" ON conversation_records
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete their own conversation records" ON conversation_records
    FOR DELETE USING (auth.uid()::text = user_id);

-- Policy for user_sessions - users can only access their own sessions
CREATE POLICY "Users can view their own sessions" ON user_sessions
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert their own sessions" ON user_sessions
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update their own sessions" ON user_sessions
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete their own sessions" ON user_sessions
    FOR DELETE USING (auth.uid()::text = user_id);

-- For development/testing: Allow anonymous access (remove in production)
-- Uncomment these if you want to allow anonymous access for testing

/*
CREATE POLICY "Allow anonymous access to conversation_records" ON conversation_records
    FOR ALL USING (true);

CREATE POLICY "Allow anonymous access to user_sessions" ON user_sessions
    FOR ALL USING (true);
*/

-- Create a function to automatically update last_activity
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_sessions 
    SET last_activity = NOW() 
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update session activity when new conversation is added
CREATE TRIGGER update_session_activity_trigger
    AFTER INSERT ON conversation_records
    FOR EACH ROW
    EXECUTE FUNCTION update_session_activity();

-- Create a function to clean up old inactive sessions (optional)
CREATE OR REPLACE FUNCTION cleanup_inactive_sessions()
RETURNS void AS $$
BEGIN
    UPDATE user_sessions 
    SET is_active = FALSE 
    WHERE last_activity < NOW() - INTERVAL '24 hours' 
    AND is_active = TRUE;
END;
$$ LANGUAGE plpgsql;

-- You can run this periodically to clean up old sessions
-- SELECT cleanup_inactive_sessions();