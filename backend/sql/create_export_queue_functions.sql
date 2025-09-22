-- ============================================================================
-- Export Queue RPC Functions for Tenant Supabase Project
-- ============================================================================
-- This script creates helper RPCs for interacting with the pgmq export queue.
-- They provide a stable interface for the Python queue service.
-- Run this in the TENANT Supabase database before launching the app.
-- ============================================================================

-- Ensure pgmq extension is available
CREATE EXTENSION IF NOT EXISTS pgmq;

-- Create the export queue if it does not already exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pgmq.queues WHERE name = 'export_queue'
    ) THEN
        PERFORM pgmq.create_queue('export_queue');
    END IF;
END;
$$;

-- Helper RPC to send a message to the export queue
CREATE OR REPLACE FUNCTION send_to_export_queue(message JSONB)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    queue_name CONSTANT TEXT := 'export_queue';
    msg_id BIGINT;
BEGIN
    -- Ensure queue exists (safety if extension reset)
    IF NOT EXISTS (
        SELECT 1 FROM pgmq.queues WHERE name = queue_name
    ) THEN
        PERFORM pgmq.create_queue(queue_name);
    END IF;

    SELECT pgmq.send(queue_name => queue_name, message => message)
    INTO msg_id;

    RETURN msg_id;
END;
$$;

-- Helper RPC to read messages from the export queue
CREATE OR REPLACE FUNCTION read_export_queue(
    qty INT DEFAULT 1,
    visibility_timeout INT DEFAULT 30
)
RETURNS TABLE (
    msg_id BIGINT,
    read_ct INT,
    enqueued_at TIMESTAMPTZ,
    vt TIMESTAMPTZ,
    message JSONB
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    queue_name CONSTANT TEXT := 'export_queue';
BEGIN
    -- Ensure queue exists before reading
    IF NOT EXISTS (
        SELECT 1 FROM pgmq.queues WHERE name = queue_name
    ) THEN
        PERFORM pgmq.create_queue(queue_name);
    END IF;

    RETURN QUERY
    SELECT
        q.msg_id,
        q.read_ct,
        q.enqueued_at,
        q.vt,
        q.message
    FROM pgmq.read(queue_name => queue_name, vt => visibility_timeout, qty => qty) AS q;
END;
$$;

-- Grant execution permissions to roles used by the application
GRANT EXECUTE ON FUNCTION send_to_export_queue(JSONB) TO service_role;
GRANT EXECUTE ON FUNCTION read_export_queue(INT, INT) TO service_role;
GRANT EXECUTE ON FUNCTION read_export_queue(INT, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION send_to_export_queue(JSONB) TO authenticated;

-- Optional verification query
SELECT 'Export queue RPC functions created successfully' AS status;
