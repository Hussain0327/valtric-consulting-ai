-- Fix based on actual table structure
DROP FUNCTION IF EXISTS search_project_chunks_arr(text, vector(1536), int);

CREATE OR REPLACE FUNCTION search_project_chunks_arr(
    p_project TEXT,
    q vector(1536),
    k INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    text TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.text,
        1 - (c.embedding <=> q) as similarity
    FROM chunks c
    WHERE c.embedding IS NOT NULL
    ORDER BY c.embedding <=> q
    LIMIT k;
END;
$$;

GRANT EXECUTE ON FUNCTION search_project_chunks_arr TO service_role;