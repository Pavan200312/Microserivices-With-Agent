-- Setup script for "new DB" database
-- This will create the required tables for the GitHub Commit Tracker

-- Create commits table
CREATE TABLE IF NOT EXISTS commits (
    id SERIAL PRIMARY KEY,
    commit_hash VARCHAR(40) UNIQUE NOT NULL,
    author VARCHAR(255) NOT NULL,
    author_email VARCHAR(255),
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    repository VARCHAR(255) NOT NULL,
    branch VARCHAR(100) DEFAULT 'main',
    files_changed JSONB, -- Stores file change details as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tracking_sessions table
CREATE TABLE IF NOT EXISTS tracking_sessions (
    id SERIAL PRIMARY KEY,
    repository VARCHAR(255) NOT NULL,
    branch VARCHAR(100) DEFAULT 'main',
    status VARCHAR(50) DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_commit_hash VARCHAR(40),
    last_polled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ai_analysis table
CREATE TABLE IF NOT EXISTS ai_analysis (
    id SERIAL PRIMARY KEY,
    commit_hash VARCHAR(40) NOT NULL,
    analysis_type VARCHAR(50) DEFAULT 'commit_analysis',
    analysis_data JSONB NOT NULL, -- Stores AI analysis results as JSON
    model_used VARCHAR(100) DEFAULT 'codellama',
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (commit_hash) REFERENCES commits(commit_hash) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_commits_hash ON commits(commit_hash);
CREATE INDEX IF NOT EXISTS idx_commits_author ON commits(author);
CREATE INDEX IF NOT EXISTS idx_commits_repository ON commits(repository);
CREATE INDEX IF NOT EXISTS idx_commits_timestamp ON commits(timestamp);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_commits_updated_at 
    BEFORE UPDATE ON commits 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tracking_sessions_updated_at 
    BEFORE UPDATE ON tracking_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data (optional)
-- INSERT INTO commits (commit_hash, author, author_email, message, timestamp, repository, branch, files_changed) 
-- VALUES (
--     'sample1234567890abcdef1234567890abcdef12345678',
--     'Test User',
--     'test@example.com',
--     'Sample commit message',
--     CURRENT_TIMESTAMP,
--     'test/repository',
--     'main',
--     '[{"status": "added", "filename": "test.txt", "additions": 1, "deletions": 0}]'::jsonb
-- );

-- Show the created tables
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name IN ('commits', 'tracking_sessions', 'ai_analysis')
ORDER BY table_name, ordinal_position;
