-- PostgreSQL Schema for RAG Logging System
-- Database: AskMyDocLOG
-- This schema is idempotent and can be run multiple times safely

-- ============================================
-- 1. Query Logs Table
-- ============================================
-- Tracks all query executions with latency metrics
CREATE TABLE IF NOT EXISTS rag_query_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
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
    
    -- Indexing for common queries
    CONSTRAINT valid_latency CHECK (total_latency >= 0)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_query_logs_timestamp ON rag_query_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_query_logs_total_latency ON rag_query_logs(total_latency DESC);
CREATE INDEX IF NOT EXISTS idx_query_logs_slow_queries ON rag_query_logs(is_slow_query) WHERE is_slow_query = TRUE;
CREATE INDEX IF NOT EXISTS idx_query_logs_model ON rag_query_logs(model_used);

-- ============================================
-- 2. Error Logs Table
-- ============================================
-- Captures pipeline failures and errors
CREATE TABLE IF NOT EXISTS rag_error_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
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

-- Indexes for error analysis
CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON rag_error_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_error_logs_stage ON rag_error_logs(pipeline_stage);
CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON rag_error_logs(severity);
CREATE INDEX IF NOT EXISTS idx_error_logs_error_type ON rag_error_logs(error_type);

-- ============================================
-- 3. Evaluation Metrics Table
-- ============================================
-- Stores RAGAS and other evaluation metrics
CREATE TABLE IF NOT EXISTS rag_evaluation_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
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

-- Indexes for evaluation analysis
CREATE INDEX IF NOT EXISTS idx_eval_metrics_timestamp ON rag_evaluation_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_run_id ON rag_evaluation_metrics(evaluation_run_id);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_overall_score ON rag_evaluation_metrics(overall_score DESC);

-- ============================================
-- 4. Component Latency Table
-- ============================================
-- Detailed latency breakdown for each pipeline component
CREATE TABLE IF NOT EXISTS rag_component_latency (
    id SERIAL PRIMARY KEY,
    query_log_id INTEGER REFERENCES rag_query_logs(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Component details
    component_name VARCHAR(100) NOT NULL,
    latency_ms FLOAT NOT NULL,
    
    -- Component metadata
    metadata JSONB,
    
    CONSTRAINT valid_component_latency CHECK (latency_ms >= 0)
);

-- Indexes for component analysis
CREATE INDEX IF NOT EXISTS idx_component_latency_query_log ON rag_component_latency(query_log_id);
CREATE INDEX IF NOT EXISTS idx_component_latency_component ON rag_component_latency(component_name);
CREATE INDEX IF NOT EXISTS idx_component_latency_timestamp ON rag_component_latency(timestamp DESC);

-- ============================================
-- 5. Cache Statistics Table
-- ============================================
-- Tracks cache performance
CREATE TABLE IF NOT EXISTS rag_cache_stats (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Cache metrics
    cache_type VARCHAR(50) NOT NULL, -- 'retrieval', 'response', 'embedding'
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
    window_start TIMESTAMP WITH TIME ZONE,
    window_end TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_cache_counts CHECK (hit_count >= 0 AND miss_count >= 0)
);

-- Indexes for cache analysis
CREATE INDEX IF NOT EXISTS idx_cache_stats_timestamp ON rag_cache_stats(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_cache_stats_type ON rag_cache_stats(cache_type);

-- ============================================
-- 6. System Health Table
-- ============================================
-- Tracks overall system health metrics
CREATE TABLE IF NOT EXISTS rag_system_health (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
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
    window_start TIMESTAMP WITH TIME ZONE,
    window_end TIMESTAMP WITH TIME ZONE
);

-- Indexes for health monitoring
CREATE INDEX IF NOT EXISTS idx_system_health_timestamp ON rag_system_health(timestamp DESC);

-- ============================================
-- Views for Common Queries
-- ============================================

-- View: Recent slow queries
CREATE OR REPLACE VIEW v_recent_slow_queries AS
SELECT 
    id,
    timestamp,
    query_text,
    total_latency,
    retrieval_latency,
    rerank_latency,
    llm_latency,
    model_used
FROM rag_query_logs
WHERE is_slow_query = TRUE
ORDER BY timestamp DESC
LIMIT 100;

-- View: Error summary by stage
CREATE OR REPLACE VIEW v_error_summary_by_stage AS
SELECT 
    pipeline_stage,
    COUNT(*) as error_count,
    COUNT(DISTINCT error_type) as unique_error_types,
    MAX(timestamp) as last_error_time
FROM rag_error_logs
GROUP BY pipeline_stage
ORDER BY error_count DESC;

-- View: Average latencies by hour
CREATE OR REPLACE VIEW v_hourly_latency_stats AS
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as query_count,
    AVG(total_latency) as avg_total_latency,
    AVG(retrieval_latency) as avg_retrieval_latency,
    AVG(rerank_latency) as avg_rerank_latency,
    AVG(llm_latency) as avg_llm_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_latency) as p95_latency,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY total_latency) as p99_latency
FROM rag_query_logs
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;

-- View: Model performance comparison
CREATE OR REPLACE VIEW v_model_performance AS
SELECT 
    model_used,
    COUNT(*) as query_count,
    AVG(llm_latency) as avg_latency,
    AVG(answer_length) as avg_answer_length,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY llm_latency) as p95_latency
FROM rag_query_logs
WHERE model_used IS NOT NULL
GROUP BY model_used
ORDER BY query_count DESC;

-- ============================================
-- Functions for Analytics
-- ============================================

-- Function: Get performance summary for time range
CREATE OR REPLACE FUNCTION get_performance_summary(
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE
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
        COUNT(*)::BIGINT as total_queries,
        AVG(q.total_latency)::FLOAT as avg_latency,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY q.total_latency)::FLOAT as p95_latency,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY q.total_latency)::FLOAT as p99_latency,
        COUNT(*) FILTER (WHERE q.is_slow_query)::BIGINT as slow_query_count,
        (SELECT COUNT(*) FROM rag_error_logs e WHERE e.timestamp BETWEEN start_time AND end_time)::BIGINT as error_count
    FROM rag_query_logs q
    WHERE q.timestamp BETWEEN start_time AND end_time;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Maintenance
-- ============================================

-- Function: Clean old logs (retention policy)
CREATE OR REPLACE FUNCTION cleanup_old_logs(retention_days INTEGER DEFAULT 90)
RETURNS TABLE (
    deleted_queries INTEGER,
    deleted_errors INTEGER,
    deleted_components INTEGER
) AS $$
DECLARE
    cutoff_date TIMESTAMP WITH TIME ZONE;
    del_queries INTEGER;
    del_errors INTEGER;
    del_components INTEGER;
BEGIN
    cutoff_date := NOW() - (retention_days || ' days')::INTERVAL;
    
    -- Delete old query logs
    DELETE FROM rag_query_logs WHERE timestamp < cutoff_date;
    GET DIAGNOSTICS del_queries = ROW_COUNT;
    
    -- Delete old error logs
    DELETE FROM rag_error_logs WHERE timestamp < cutoff_date;
    GET DIAGNOSTICS del_errors = ROW_COUNT;
    
    -- Delete old component latency records
    DELETE FROM rag_component_latency WHERE timestamp < cutoff_date;
    GET DIAGNOSTICS del_components = ROW_COUNT;
    
    RETURN QUERY SELECT del_queries, del_errors, del_components;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Comments for Documentation
-- ============================================

COMMENT ON TABLE rag_query_logs IS 'Stores all query executions with latency and performance metrics';
COMMENT ON TABLE rag_error_logs IS 'Captures pipeline failures and errors for debugging';
COMMENT ON TABLE rag_evaluation_metrics IS 'Stores RAGAS and other evaluation metrics';
COMMENT ON TABLE rag_component_latency IS 'Detailed latency breakdown for each pipeline component';
COMMENT ON TABLE rag_cache_stats IS 'Tracks cache performance and hit rates';
COMMENT ON TABLE rag_system_health IS 'Overall system health metrics';

COMMENT ON COLUMN rag_query_logs.is_slow_query IS 'Automatically set to TRUE if total_latency > 2000ms';
COMMENT ON COLUMN rag_evaluation_metrics.overall_score IS 'Average of all RAGAS metrics';
COMMENT ON COLUMN rag_cache_stats.hit_rate IS 'Calculated as hit_count / (hit_count + miss_count)';
