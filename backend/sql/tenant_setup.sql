-- =============================================================================
-- TENANT SUPABASE DATABASE SETUP
-- Tables for user sessions, conversation history, and profile memory
-- =============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- CHAT SESSIONS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    project_id TEXT DEFAULT 'default',
    title TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'archived')),
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_project_id ON chat_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_last_activity ON chat_sessions(last_activity DESC);

-- =============================================================================
-- CHAT MESSAGES TABLE  
-- =============================================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    model_used TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(role);

-- =============================================================================
-- PROFILE MEMORY TABLE
-- For storing user profile information (name, company, role, etc.)
-- =============================================================================
CREATE TABLE IF NOT EXISTS assistant_profile_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    confidence NUMERIC DEFAULT 0.9 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, key)
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_profile_memory_session_id ON assistant_profile_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_profile_memory_key ON assistant_profile_memory(key);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;  
ALTER TABLE assistant_profile_memory ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (adjust based on your auth model)
-- For now, allow service role full access

CREATE POLICY "service_role_all_chat_sessions" ON chat_sessions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_all_chat_messages" ON chat_messages  
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_all_profile_memory" ON assistant_profile_memory
    FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- FUNCTIONS FOR CONVERSATION MANAGEMENT
-- =============================================================================

-- Function to update last_activity when messages are added
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_sessions 
    SET last_activity = NOW(),
        message_count = message_count + 1
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update session activity
DROP TRIGGER IF EXISTS trigger_update_session_activity ON chat_messages;
CREATE TRIGGER trigger_update_session_activity
    AFTER INSERT ON chat_messages
    FOR EACH ROW EXECUTE FUNCTION update_session_activity();

-- =============================================================================
-- RPC FUNCTIONS FOR APPLICATION LAYER
-- =============================================================================

-- Get conversation with profile context
CREATE OR REPLACE FUNCTION get_conversation_with_profile(p_session_id UUID)
RETURNS JSON AS $$
DECLARE
    messages JSON;
    profile JSON;
    result JSON;
BEGIN
    -- Get messages
    SELECT json_agg(
        json_build_object(
            'role', role,
            'content', content,
            'model_used', model_used,
            'created_at', created_at,
            'metadata', metadata
        ) ORDER BY created_at ASC
    ) INTO messages
    FROM chat_messages 
    WHERE session_id = p_session_id;
    
    -- Get profile data
    SELECT json_object_agg(key, value) INTO profile
    FROM assistant_profile_memory
    WHERE session_id = p_session_id;
    
    -- Combine results
    result := json_build_object(
        'session_id', p_session_id,
        'messages', COALESCE(messages, '[]'::JSON),
        'profile', COALESCE(profile, '{}'::JSON)
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Clean up old sessions (for maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_sessions(days_old INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM chat_sessions 
    WHERE last_activity < NOW() - (days_old || ' days')::INTERVAL
    AND status = 'archived';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;