CREATE TABLE IF NOT EXISTS story_pipeline_results (
    id BIGSERIAL PRIMARY KEY,
    story_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_story_pipeline_story_id
ON story_pipeline_results (story_id);

CREATE INDEX IF NOT EXISTS idx_story_pipeline_stage
ON story_pipeline_results (stage);

CREATE INDEX IF NOT EXISTS idx_story_pipeline_data_gin
ON story_pipeline_results USING GIN (data);