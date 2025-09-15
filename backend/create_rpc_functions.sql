-- ============================================================================
-- RPC Functions for ValtricAI Tenant Database
-- ============================================================================
-- This creates the search_project_chunks_arr function that the RAG system needs
-- Run this in your TENANT Supabase database (Project 2)
-- ============================================================================

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop the function if it exists (to avoid conflicts)
DROP FUNCTION IF EXISTS search_project_chunks_arr(uuid, vector, int);
DROP FUNCTION IF EXISTS search_project_chunks_arr(text, vector, int);

-- Create the vector search function for project chunks
-- This function searches chunks belonging to a specific project
CREATE OR REPLACE FUNCTION search_project_chunks_arr(
    p_project TEXT,  -- Project ID as text (matching your code)
    q vector(1536),  -- Query embedding vector (1536 dimensions for OpenAI)
    k INT DEFAULT 10 -- Number of results to return
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
        c.content as text,
        1 - (c.embedding <=> q) as similarity,  -- Cosine similarity
        c.metadata,
        c.project_id,
        c.created_at
    FROM chunks c
    WHERE c.project_id = p_project
        AND c.embedding IS NOT NULL
    ORDER BY c.embedding <=> q  -- Order by distance (closest first)
    LIMIT k;
END;
$$;

-- Create a simpler version that works even without embeddings (for testing)
CREATE OR REPLACE FUNCTION search_project_chunks_text(
    p_project TEXT,
    query_text TEXT,
    k INT DEFAULT 10
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
        c.content as text,
        -- Simple text similarity scoring
        CASE 
            WHEN c.content ILIKE '%' || query_text || '%' THEN 0.9
            ELSE 0.5
        END as similarity,
        c.metadata,
        c.project_id,
        c.created_at
    FROM chunks c
    WHERE c.project_id = p_project
        AND c.content ILIKE '%' || query_text || '%'
    ORDER BY LENGTH(c.content)
    LIMIT k;
END;
$$;

-- Create hybrid search function (combines vector and text search)
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text TEXT,
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    text TEXT,
    similarity FLOAT,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH vector_results AS (
        -- Vector similarity search
        SELECT 
            c.id,
            c.content as text,
            1 - (c.embedding <=> query_embedding) as similarity,
            c.metadata
        FROM chunks c
        WHERE c.embedding IS NOT NULL
            AND 1 - (c.embedding <=> query_embedding) > match_threshold
        ORDER BY c.embedding <=> query_embedding
        LIMIT match_count
    ),
    text_results AS (
        -- Full text search
        SELECT 
            c.id,
            c.content as text,
            0.8 as similarity,  -- Fixed similarity for text matches
            c.metadata
        FROM chunks c
        WHERE c.content ILIKE '%' || query_text || '%'
        LIMIT match_count
    ),
    combined AS (
        SELECT * FROM vector_results
        UNION
        SELECT * FROM text_results
    )
    SELECT DISTINCT ON (id) 
        id, 
        text, 
        MAX(similarity) as similarity,
        metadata
    FROM combined
    GROUP BY id, text, metadata
    ORDER BY id, MAX(similarity) DESC
    LIMIT match_count;
END;
$$;

-- Grant permissions to authenticated users
GRANT EXECUTE ON FUNCTION search_project_chunks_arr TO authenticated;
GRANT EXECUTE ON FUNCTION search_project_chunks_text TO authenticated;
GRANT EXECUTE ON FUNCTION hybrid_search TO authenticated;

-- Grant permissions to service role (for backend)
GRANT EXECUTE ON FUNCTION search_project_chunks_arr TO service_role;
GRANT EXECUTE ON FUNCTION search_project_chunks_text TO service_role;
GRANT EXECUTE ON FUNCTION hybrid_search TO service_role;

-- Add comments for documentation
COMMENT ON FUNCTION search_project_chunks_arr IS 'Vector similarity search for chunks within a specific project';
COMMENT ON FUNCTION search_project_chunks_text IS 'Text-based search for chunks within a specific project (fallback when no embeddings)';
COMMENT ON FUNCTION hybrid_search IS 'Hybrid search combining vector and text search across all chunks';

-- Verification query
SELECT 'RPC functions created successfully!' as status;

-- Test the function (uncomment and modify with actual data to test)
/*
-- Test with dummy vector
SELECT * FROM search_project_chunks_arr(
    'your-project-id',
    ARRAY_FILL(0.1::float, ARRAY[1536])::vector(1536),
    5
);
*/