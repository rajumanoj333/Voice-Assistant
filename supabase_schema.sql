-- Simple Supabase Schema for Voice Assistant Conversation Log
-- Run these commands in the Supabase SQL Editor

-- Drop old tables if they exist (optional, for clean setup)
DROP TABLE IF EXISTS conversation_records CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;

-- Create new conversation_log table
CREATE TABLE IF NOT EXISTS conversation_log (
    id TEXT PRIMARY KEY,
    audio_type TEXT NOT NULL, -- e.g., 'wav', 'mp3', etc.
    audio_transcription TEXT NOT NULL, -- Transcription from Google service
    llm_response TEXT NOT NULL, -- LLM response
    timestamp TIMESTAMPTZ DEFAULT NOW() -- When the record was created
);

-- Index for fast retrieval by timestamp
CREATE INDEX IF NOT EXISTS idx_conversation_log_timestamp ON conversation_log(timestamp DESC);

-- Enable Row Level Security (RLS) for security
ALTER TABLE conversation_log ENABLE ROW LEVEL SECURITY;

-- Allow all access for development (REMOVE in production)
CREATE POLICY "Allow all access to conversation_log" ON conversation_log
    FOR ALL USING (true);