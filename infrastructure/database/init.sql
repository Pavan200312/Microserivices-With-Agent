-- Database initialization script for GitHub Commit Tracker

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
    files_changed JSONB,
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
    analysis_data JSONB NOT NULL,
    model_used VARCHAR(100) DEFAULT 'codellama',
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (commit_hash) REFERENCES commits(commit_hash) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_commits_hash ON commits(commit_hash);
CREATE INDEX IF NOT EXISTS idx_commits_timestamp ON commits(timestamp);
CREATE INDEX IF NOT EXISTS idx_commits_repository ON commits(repository);
CREATE INDEX IF NOT EXISTS idx_commits_author ON commits(author);
CREATE INDEX IF NOT EXISTS idx_tracking_sessions_repository ON tracking_sessions(repository);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_commit_hash ON ai_analysis(commit_hash);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_commits_updated_at BEFORE UPDATE ON commits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tracking_sessions_updated_at BEFORE UPDATE ON tracking_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
