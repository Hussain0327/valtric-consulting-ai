-- ============================================================================
-- Create Chat Tables for ValtricAI Consulting Agent
-- ============================================================================
-- This SQL creates the chat_sessions and chat_messages tables that integrate
-- with your existing project/organization structure
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CHAT SESSIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id uuid REFERENCES projects(id) ON DELETE CASCADE,
    org_id uuid REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Session metadata
    title text NOT NULL DEFAULT 'New Conversation',
    persona text NOT NULL DEFAULT 'partner' CHECK (persona IN ('associate', 'partner', 'senior_partner')),
    framework text CHECK (framework IN ('swot', 'porters', 'mckinsey', 'bcg_matrix', 'ansoff', 'pestel')),
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'archived')),
    
    -- Statistics
    message_count integer DEFAULT 0,
    total_tokens integer DEFAULT 0,
    
    -- Metadata
    context jsonb DEFAULT '{}',
    metadata jsonb DEFAULT '{}',
    
    -- Timestamps
    last_activity timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- ============================================================================
-- CHAT MESSAGES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id uuid NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Message content
    role text NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content text NOT NULL,
    
    -- Model information
    model text,
    prompt_tokens integer,
    completion_tokens integer,
    total_tokens integer,
    
    -- RAG sources
    sources jsonb DEFAULT '[]',
    
    -- Metadata
    metadata jsonb DEFAULT '{}',
    
    -- Timestamp
    created_at timestamp with time zone DEFAULT now()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Sessions indexes
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_project_id ON chat_sessions(project_id);
CREATE INDEX idx_chat_sessions_org_id ON chat_sessions(org_id);
CREATE INDEX idx_chat_sessions_status ON chat_sessions(status);
CREATE INDEX idx_chat_sessions_created_at ON chat_sessions(created_at DESC);
CREATE INDEX idx_chat_sessions_last_activity ON chat_sessions(last_activity DESC);

-- Messages indexes
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on both tables
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Chat Sessions RLS Policy
-- Users can only access sessions in projects they have access to
CREATE POLICY chat_sessions_rls ON chat_sessions
    FOR ALL
    USING (
        project_id IN (
            SELECT projects.id
            FROM projects
            WHERE projects.org_id IN (
                SELECT org_id FROM my_orgs
            )
        )
    )
    WITH CHECK (
        project_id IN (
            SELECT projects.id
            FROM projects
            WHERE projects.org_id IN (
                SELECT org_id FROM my_orgs
            )
        )
    );

-- Chat Messages RLS Policy
-- Users can only access messages from sessions they have access to
CREATE POLICY chat_messages_rls ON chat_messages
    FOR ALL
    USING (
        session_id IN (
            SELECT id FROM chat_sessions
            WHERE project_id IN (
                SELECT projects.id
                FROM projects
                WHERE projects.org_id IN (
                    SELECT org_id FROM my_orgs
                )
            )
        )
    )
    WITH CHECK (
        session_id IN (
            SELECT id FROM chat_sessions
            WHERE project_id IN (
                SELECT projects.id
                FROM projects
                WHERE projects.org_id IN (
                    SELECT org_id FROM my_orgs
                )
            )
        )
    );

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update session statistics after new message
CREATE OR REPLACE FUNCTION update_session_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_sessions
    SET 
        message_count = message_count + 1,
        total_tokens = total_tokens + COALESCE(NEW.total_tokens, 0),
        last_activity = now(),
        updated_at = now()
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update session stats on new message
CREATE TRIGGER update_session_stats_trigger
    AFTER INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_session_stats();

-- ============================================================================
-- GRANTS (if needed for your app user)
-- ============================================================================
-- Uncomment and modify if you have a specific app user
-- GRANT ALL ON chat_sessions TO your_app_user;
-- GRANT ALL ON chat_messages TO your_app_user;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- After running this script, verify with:
/*
-- Check tables were created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('chat_sessions', 'chat_messages');

-- Check RLS policies
SELECT tablename, policyname FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('chat_sessions', 'chat_messages');

-- Test insert (replace with actual IDs from your database)
-- You'll need a valid user_id, project_id, and org_id
*/