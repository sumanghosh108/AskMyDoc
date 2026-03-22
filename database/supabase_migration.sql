-- ============================================
-- Supabase Migration for AskMyDoc RAG System
-- ============================================
-- Run this SQL in your Supabase SQL Editor:
--   https://supabase.com/dashboard → SQL Editor
--
-- This creates all required tables, indexes,
-- views, and RPC functions for the RAG logging system.
-- All statements are idempotent (safe to re-run).
-- ============================================

-- ============================================
-- 1. Query Logs Table
-- ============================================
CREATE TABLE IF NOT EXISTS rag_query_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    query_text TEXT NOT NULL,

    -- Latency metrics (in milliseconds)
    retrieval_latency FLOAT,
    rerank_latency FLOAT,
    llm_latency FLOAT,
    total_latency FLOAT NOT NULL,

    -- Chunk metrics
    retrieved_chunks INTEGER,
    reranked_chunks INTEGER,

    -- Model information
    model_used VARCHAR(255),
    embedding_model VARCHAR(255),

    -- Additional metadata
    query_rewriting_enabled BOOLEAN DEFAULT FALSE,
    multi_hop_enabled BOOLEAN DEFAULT FALSE,
    cache_hit BOOLEAN DEFAULT FALSE,

    -- Response metadata
    answer_length INTEGER,
    source_count INTEGER,

    -- Performance flags
    is_slow_query BOOLEAN GENERATED ALWAYS AS (total_latency > 2000) STORED,

    CONSTRAINT valid_latency CHECK (total_latency >= 0)
);

CREATE INDEX IF NOT EXISTS idx_query_logs_timestamp ON rag_query_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_query_logs_total_latency ON rag_query_logs(total_latency DESC);
CREATE INDEX IF NOT EXISTS idx_query_logs_slow_queries ON rag_query_logs(is_slow_query) WHERE is_slow_query = TRUE;
CREATE INDEX IF NOT EXISTS idx_query_logs_model ON rag_query_logs(model_used);

-- ============================================
-- 2. Error Logs Table
-- ============================================
CREATE TABLE IF NOT EXISTS rag_error_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    query_text TEXT,

    -- Error details
    pipeline_stage VARCHAR(100) NOT NULL,
    error_type VARCHAR(255),
    error_message TEXT NOT NULL,
    stack_trace TEXT,

    -- Context
    user_id VARCHAR(255),
    session_id VARCHAR(255),

    -- Error severity
    severity VARCHAR(20) DEFAULT 'ERROR',

    -- Additional metadata
    metadata JSONB,

    CONSTRAINT valid_severity CHECK (severity IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
);

CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON rag_error_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_error_logs_stage ON rag_error_logs(pipeline_stage);
CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON rag_error_logs(severity);
CREATE INDEX IF NOT EXISTS idx_error_logs_error_type ON rag_error_logs(error_type);

-- ============================================
-- 3. Evaluation Metrics Table
-- ============================================
CREATE TABLE IF NOT EXISTS rag_evaluation_metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- RAGAS metrics
    faithfulness_score FLOAT,
    answer_correctness FLOAT,
    context_precision FLOAT,
    context_recall FLOAT,

    -- Overall score
    overall_score FLOAT GENERATED ALWAYS AS (
        (COALESCE(faithfulness_score, 0) +
         COALESCE(answer_correctness, 0) +
         COALESCE(context_precision, 0) +
         COALESCE(context_recall, 0)) / 4.0
    ) STORED,

    -- Test details
    test_query TEXT,
    expected_answer TEXT,
    actual_answer TEXT,

    -- Evaluation metadata
    evaluation_run_id VARCHAR(255),
    dataset_name VARCHAR(255),

    -- Quality flags
    passed_threshold BOOLEAN,

    CONSTRAINT valid_scores CHECK (
        (faithfulness_score IS NULL OR (faithfulness_score >= 0 AND faithfulness_score <= 1)) AND
        (answer_correctness IS NULL OR (answer_correctness >= 0 AND answer_correctness <= 1)) AND
        (context_precision IS NULL OR (context_precision >= 0 AND context_precision <= 1)) AND
        (context_recall IS NULL OR (context_recall >= 0 AND context_recall <= 1))
    )
);

CREATE INDEX IF NOT EXISTS idx_eval_metrics_timestamp ON rag_evaluation_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_run_id ON rag_evaluation_metrics(evaluation_run_id);

-- ============================================
-- 4. Component Latency Table
-- ============================================
CREATE TABLE IF NOT EXISTS rag_component_latency (
    id BIGSERIAL PRIMARY KEY,
    query_log_id BIGINT REFERENCES rag_query_logs(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Component details
    component_name VARCHAR(100) NOT NULL,
    latency_ms FLOAT NOT NULL,

    -- Component metadata
    metadata JSONB,

    CONSTRAINT valid_component_latency CHECK (latency_ms >= 0)
);

CREATE INDEX IF NOT EXISTS idx_component_latency_query_log ON rag_component_latency(query_log_id);
CREATE INDEX IF NOT EXISTS idx_component_latency_component ON rag_component_latency(component_name);
CREATE INDEX IF NOT EXISTS idx_component_latency_timestamp ON rag_component_latency(timestamp DESC);

-- ============================================
-- 5. Cache Statistics Table
-- ============================================
CREATE TABLE IF NOT EXISTS rag_cache_stats (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Cache metrics
    cache_type VARCHAR(50) NOT NULL,
    hit_count INTEGER DEFAULT 0,
    miss_count INTEGER DEFAULT 0,

    -- Hit rate calculation
    hit_rate FLOAT GENERATED ALWAYS AS (
        CASE
            WHEN (hit_count + miss_count) > 0
            THEN hit_count::FLOAT / (hit_count + miss_count)
            ELSE 0
        END
    ) STORED,

    -- Time window
    window_start TIMESTAMPTZ,
    window_end TIMESTAMPTZ,

    CONSTRAINT valid_cache_counts CHECK (hit_count >= 0 AND miss_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_cache_stats_timestamp ON rag_cache_stats(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_cache_stats_type ON rag_cache_stats(cache_type);

-- ============================================
-- 6. System Health Table
-- ============================================
CREATE TABLE IF NOT EXISTS rag_system_health (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- System metrics
    total_queries INTEGER DEFAULT 0,
    successful_queries INTEGER DEFAULT 0,
    failed_queries INTEGER DEFAULT 0,

    -- Success rate
    success_rate FLOAT GENERATED ALWAYS AS (
        CASE
            WHEN total_queries > 0
            THEN successful_queries::FLOAT / total_queries
            ELSE 0
        END
    ) STORED,

    -- Average latencies
    avg_total_latency FLOAT,
    avg_retrieval_latency FLOAT,
    avg_llm_latency FLOAT,

    -- Resource usage
    cpu_usage_percent FLOAT,
    memory_usage_mb FLOAT,

    -- Time window
    window_start TIMESTAMPTZ,
    window_end TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_system_health_timestamp ON rag_system_health(timestamp DESC);

-- ============================================
-- Disable RLS on all logging tables
-- (we use service_role key from backend)
-- ============================================
ALTER TABLE rag_query_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_error_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_evaluation_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_component_latency ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_cache_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_system_health ENABLE ROW LEVEL SECURITY;

-- Allow full access (service_role bypasses RLS automatically,
-- these policies allow access for authenticated/anon roles too)
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'allow_all_rag_query_logs') THEN
    CREATE POLICY "allow_all_rag_query_logs" ON rag_query_logs FOR ALL USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'allow_all_rag_error_logs') THEN
    CREATE POLICY "allow_all_rag_error_logs" ON rag_error_logs FOR ALL USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'allow_all_rag_evaluation_metrics') THEN
    CREATE POLICY "allow_all_rag_evaluation_metrics" ON rag_evaluation_metrics FOR ALL USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'allow_all_rag_component_latency') THEN
    CREATE POLICY "allow_all_rag_component_latency" ON rag_component_latency FOR ALL USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'allow_all_rag_cache_stats') THEN
    CREATE POLICY "allow_all_rag_cache_stats" ON rag_cache_stats FOR ALL USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'allow_all_rag_system_health') THEN
    CREATE POLICY "allow_all_rag_system_health" ON rag_system_health FOR ALL USING (true);
  END IF;
END $$;

-- ============================================
-- RPC Functions for Analytics
-- ============================================

-- Function: Get latency statistics
CREATE OR REPLACE FUNCTION get_latency_stats(hours_back INTEGER DEFAULT 24)
RETURNS TABLE (
    query_count BIGINT,
    avg_total_latency FLOAT,
    avg_retrieval_latency FLOAT,
    avg_rerank_latency FLOAT,
    avg_llm_latency FLOAT,
    p50_latency FLOAT,
    p95_latency FLOAT,
    p99_latency FLOAT,
    slow_query_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        AVG(q.total_latency)::FLOAT,
        AVG(q.retrieval_latency)::FLOAT,
        AVG(q.rerank_latency)::FLOAT,
        AVG(q.llm_latency)::FLOAT,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY q.total_latency)::FLOAT,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY q.total_latency)::FLOAT,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY q.total_latency)::FLOAT,
        COUNT(*) FILTER (WHERE q.is_slow_query)::BIGINT
    FROM rag_query_logs q
    WHERE q.timestamp > NOW() - (hours_back || ' hours')::INTERVAL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get model performance
CREATE OR REPLACE FUNCTION get_model_performance()
RETURNS TABLE (
    model_used VARCHAR,
    query_count BIGINT,
    avg_latency FLOAT,
    avg_answer_length FLOAT,
    p95_latency FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        q.model_used,
        COUNT(*)::BIGINT,
        AVG(q.llm_latency)::FLOAT,
        AVG(q.answer_length)::FLOAT,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY q.llm_latency)::FLOAT
    FROM rag_query_logs q
    WHERE q.model_used IS NOT NULL
    GROUP BY q.model_used
    ORDER BY COUNT(*) DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get error summary
CREATE OR REPLACE FUNCTION get_error_summary(hours_back INTEGER DEFAULT 24)
RETURNS TABLE (
    total_errors BIGINT,
    affected_stages BIGINT,
    unique_error_types BIGINT,
    critical_count BIGINT,
    error_count BIGINT,
    warning_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        COUNT(DISTINCT e.pipeline_stage)::BIGINT,
        COUNT(DISTINCT e.error_type)::BIGINT,
        COUNT(*) FILTER (WHERE e.severity = 'CRITICAL')::BIGINT,
        COUNT(*) FILTER (WHERE e.severity = 'ERROR')::BIGINT,
        COUNT(*) FILTER (WHERE e.severity = 'WARNING')::BIGINT
    FROM rag_error_logs e
    WHERE e.timestamp > NOW() - (hours_back || ' hours')::INTERVAL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get errors by stage
CREATE OR REPLACE FUNCTION get_errors_by_stage(hours_back INTEGER DEFAULT 24)
RETURNS TABLE (
    pipeline_stage VARCHAR,
    error_count BIGINT,
    unique_error_types BIGINT,
    last_error_time TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.pipeline_stage,
        COUNT(*)::BIGINT,
        COUNT(DISTINCT e.error_type)::BIGINT,
        MAX(e.timestamp)
    FROM rag_error_logs e
    WHERE e.timestamp > NOW() - (hours_back || ' hours')::INTERVAL
    GROUP BY e.pipeline_stage
    ORDER BY COUNT(*) DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get top errors
CREATE OR REPLACE FUNCTION get_top_errors(hours_back INTEGER DEFAULT 24, max_results INTEGER DEFAULT 10)
RETURNS TABLE (
    error_type VARCHAR,
    error_message TEXT,
    pipeline_stage VARCHAR,
    occurrence_count BIGINT,
    last_occurrence TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.error_type,
        e.error_message,
        e.pipeline_stage,
        COUNT(*)::BIGINT,
        MAX(e.timestamp)
    FROM rag_error_logs e
    WHERE e.timestamp > NOW() - (hours_back || ' hours')::INTERVAL
    GROUP BY e.error_type, e.error_message, e.pipeline_stage
    ORDER BY COUNT(*) DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get performance summary
CREATE OR REPLACE FUNCTION get_performance_summary(
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ
)
RETURNS TABLE (
    total_queries BIGINT,
    avg_latency FLOAT,
    p95_latency FLOAT,
    p99_latency FLOAT,
    slow_query_count BIGINT,
    error_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        AVG(q.total_latency)::FLOAT,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY q.total_latency)::FLOAT,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY q.total_latency)::FLOAT,
        COUNT(*) FILTER (WHERE q.is_slow_query)::BIGINT,
        (SELECT COUNT(*) FROM rag_error_logs e WHERE e.timestamp BETWEEN start_time AND end_time)::BIGINT
    FROM rag_query_logs q
    WHERE q.timestamp BETWEEN start_time AND end_time;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Clean old logs (retention policy)
CREATE OR REPLACE FUNCTION cleanup_old_logs(retention_days INTEGER DEFAULT 90)
RETURNS TABLE (
    deleted_queries INTEGER,
    deleted_errors INTEGER,
    deleted_components INTEGER
) AS $$
DECLARE
    cutoff_date TIMESTAMPTZ;
    del_queries INTEGER;
    del_errors INTEGER;
    del_components INTEGER;
BEGIN
    cutoff_date := NOW() - (retention_days || ' days')::INTERVAL;

    DELETE FROM rag_query_logs WHERE timestamp < cutoff_date;
    GET DIAGNOSTICS del_queries = ROW_COUNT;

    DELETE FROM rag_error_logs WHERE timestamp < cutoff_date;
    GET DIAGNOSTICS del_errors = ROW_COUNT;

    DELETE FROM rag_component_latency WHERE timestamp < cutoff_date;
    GET DIAGNOSTICS del_components = ROW_COUNT;

    RETURN QUERY SELECT del_queries, del_errors, del_components;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- Table Comments
-- ============================================
COMMENT ON TABLE rag_query_logs IS 'Stores all query executions with latency and performance metrics';
COMMENT ON TABLE rag_error_logs IS 'Captures pipeline failures and errors for debugging';
COMMENT ON TABLE rag_evaluation_metrics IS 'Stores RAGAS and other evaluation metrics';
COMMENT ON TABLE rag_component_latency IS 'Detailed latency breakdown for each pipeline component';
COMMENT ON TABLE rag_cache_stats IS 'Tracks cache performance and hit rates';
COMMENT ON TABLE rag_system_health IS 'Overall system health metrics';
