-- Simple fix - remove the problematic columns
DROP FUNCTION IF EXISTS search_project_chunks_arr(text, vector(1536), int);

CREATE OR REPLACE FUNCTION search_project_chunks_arr(
    p_project TEXT,
    q vector(1536),
    k INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    text TEXT,
    similarity FLOAT,
    project_id TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.text,
        1 - (c.embedding <=> q) as similarity,
        c.project_id
    FROM chunks c
    WHERE c.project_id = p_project
        AND c.embedding IS NOT NULL
    ORDER BY c.embedding <=> q
    LIMIT k;
END;
$$;

GRANT EXECUTE ON FUNCTION search_project_chunks_arr TO service_role;