-- Feedback System Tables for ValtricAI Consulting Agent
-- Execute this in your Tenant Supabase database

-- User Feedback Table
CREATE TABLE IF NOT EXISTS user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('bug_report', 'feature_request', 'general_feedback', 'ai_response_quality', 'usability', 'performance')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    session_id TEXT,
    message_id TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    context JSONB DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Response Ratings Table
CREATE TABLE IF NOT EXISTS response_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    overall_rating INTEGER NOT NULL CHECK (overall_rating >= 1 AND overall_rating <= 5),
    comment TEXT,
    aspects JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Request Traces Table (for analytics)
CREATE TABLE IF NOT EXISTS request_traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id TEXT NOT NULL,
    user_id TEXT,
    project_id TEXT,
    route TEXT NOT NULL,
    intent TEXT,
    retrieve_ms FLOAT,
    generate_ms FLOAT,
    tokens_in INTEGER,
    tokens_out INTEGER,
    cost_usd FLOAT,
    cache_hit BOOLEAN,
    error TEXT,
    session_id TEXT,
    model_used TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback (user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_project_id ON user_feedback (project_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_type ON user_feedback (type);
CREATE INDEX IF NOT EXISTS idx_user_feedback_severity ON user_feedback (severity);
CREATE INDEX IF NOT EXISTS idx_user_feedback_status ON user_feedback (status);
CREATE INDEX IF NOT EXISTS idx_user_feedback_created_at ON user_feedback (created_at);

CREATE INDEX IF NOT EXISTS idx_response_ratings_user_id ON response_ratings (user_id);
CREATE INDEX IF NOT EXISTS idx_response_ratings_project_id ON response_ratings (project_id);
CREATE INDEX IF NOT EXISTS idx_response_ratings_session_id ON response_ratings (session_id);
CREATE INDEX IF NOT EXISTS idx_response_ratings_created_at ON response_ratings (created_at);

CREATE INDEX IF NOT EXISTS idx_request_traces_user_id ON request_traces (user_id);
CREATE INDEX IF NOT EXISTS idx_request_traces_project_id ON request_traces (project_id);
CREATE INDEX IF NOT EXISTS idx_request_traces_route ON request_traces (route);
CREATE INDEX IF NOT EXISTS idx_request_traces_timestamp ON request_traces (timestamp);

-- RLS Policies for user_feedback
ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;

-- Users can only access their own feedback
CREATE POLICY user_feedback_user_policy ON user_feedback
    FOR ALL
    USING (user_id = auth.jwt() ->> 'sub');

-- Project isolation policy
CREATE POLICY user_feedback_project_policy ON user_feedback
    FOR ALL
    USING (
        project_id = COALESCE(
            auth.jwt() ->> 'project_id',
            (auth.jwt() -> 'app_metadata' ->> 'project_id')
        )
    );

-- RLS Policies for response_ratings
ALTER TABLE response_ratings ENABLE ROW LEVEL SECURITY;

-- Users can only access their own ratings
CREATE POLICY response_ratings_user_policy ON response_ratings
    FOR ALL
    USING (user_id = auth.jwt() ->> 'sub');

-- Project isolation policy
CREATE POLICY response_ratings_project_policy ON response_ratings
    FOR ALL
    USING (
        project_id = COALESCE(
            auth.jwt() ->> 'project_id',
            (auth.jwt() -> 'app_metadata' ->> 'project_id')
        )
    );

-- RLS Policies for request_traces (read-only for users, full access for service role)
ALTER TABLE request_traces ENABLE ROW LEVEL SECURITY;

-- Users can only read their own traces
CREATE POLICY request_traces_user_policy ON request_traces
    FOR SELECT
    USING (user_id = auth.jwt() ->> 'sub');

-- Project isolation policy
CREATE POLICY request_traces_project_policy ON request_traces
    FOR SELECT
    USING (
        project_id = COALESCE(
            auth.jwt() ->> 'project_id',
            (auth.jwt() -> 'app_metadata' ->> 'project_id')
        )
    );

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_feedback_updated_at
    BEFORE UPDATE ON user_feedback
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL ON user_feedback TO authenticated;
GRANT ALL ON response_ratings TO authenticated;
GRANT SELECT ON request_traces TO authenticated;

-- Service role has full access (for backend operations)
GRANT ALL ON user_feedback TO service_role;
GRANT ALL ON response_ratings TO service_role;
GRANT ALL ON request_traces TO service_role;

-- Comments for documentation
COMMENT ON TABLE user_feedback IS 'User feedback submissions including bug reports, feature requests, and general feedback';
COMMENT ON TABLE response_ratings IS 'User ratings and feedback for AI responses';
COMMENT ON TABLE request_traces IS 'Performance tracing data for all API requests';

COMMENT ON COLUMN user_feedback.type IS 'Type of feedback: bug_report, feature_request, general_feedback, ai_response_quality, usability, performance';
COMMENT ON COLUMN user_feedback.severity IS 'Severity level: low, medium, high, critical';
COMMENT ON COLUMN user_feedback.status IS 'Processing status: open, in_progress, resolved, closed';
COMMENT ON COLUMN user_feedback.context IS 'Additional context like browser info, error details, etc.';

COMMENT ON COLUMN response_ratings.aspects IS 'Detailed aspect ratings like {"accuracy": 4, "helpfulness": 5}';
COMMENT ON COLUMN request_traces.cache_hit IS 'Whether RAG retrieval hit cache';
COMMENT ON COLUMN request_traces.cost_usd IS 'Estimated cost in USD for this request';

-- Success message
SELECT 'Feedback system tables created successfully!' as status;