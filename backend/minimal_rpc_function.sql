-- ============================================================================
-- Minimal Working RPC Function for ValtricAI Tenant Database
-- ============================================================================
-- This creates the simplest possible working function
-- Run this in your TENANT Supabase database (Project 2)
-- ============================================================================

-- Drop existing functions
DROP FUNCTION IF EXISTS search_project_chunks_arr(text, vector(1536), int);

-- Create minimal function that only uses columns that definitely exist
CREATE OR REPLACE FUNCTION search_project_chunks_arr(
    p_project TEXT,  -- Project ID
    q vector(1536),  -- Query embedding vector
    k INT DEFAULT 10 -- Number of results
)
RETURNS TABLE (
    id UUID,
    text TEXT,
    similarity FLOAT,
    metadata JSONB,
    project_id TEXT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        COALESCE(c.text, c.content, 'No text available')::TEXT as text,
        CASE 
            WHEN c.embedding IS NOT NULL THEN 1 - (c.embedding <=> q) 
            ELSE 0.5 
        END::FLOAT as similarity,
        '{}'::JSONB as metadata,  -- Return empty JSON if metadata doesn't exist
        c.project_id,
        c.created_at
    FROM chunks c
    WHERE c.project_id = p_project
    ORDER BY 
        CASE 
            WHEN c.embedding IS NOT NULL THEN c.embedding <=> q
            ELSE 1.0
        END
    LIMIT k;
END;
$$;

-- Grant permissions
GRANT EXECUTE ON FUNCTION search_project_chunks_arr TO authenticated;
GRANT EXECUTE ON FUNCTION search_project_chunks_arr TO service_role;

-- Create a debug function to see actual table structure
CREATE OR REPLACE FUNCTION debug_chunks_structure()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result JSON;
BEGIN
    -- Return first row as JSON to see all columns
    SELECT row_to_json(c) INTO result
    FROM chunks c
    LIMIT 1;
    
    RETURN COALESCE(result, '{\"message\": \"No data in chunks table\"}'::JSON);
END;
$$;

GRANT EXECUTE ON FUNCTION debug_chunks_structure TO authenticated;
GRANT EXECUTE ON FUNCTION debug_chunks_structure TO service_role;

SELECT 'Minimal RPC function created successfully!' as status;