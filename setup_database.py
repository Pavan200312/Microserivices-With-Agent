#!/usr/bin/env python3
"""
Setup script to create database with correct name
"""

import psycopg2

def setup_database():
    """Create database with correct name"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='postgres',
            user='postgres',
            password='191089193'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("🔍 Connected to PostgreSQL server")
        
        # Check if new_DB exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'new_DB'")
        exists = cursor.fetchone()
        
        if exists:
            print("✅ Database 'new_DB' already exists")
        else:
            print("📝 Creating database 'new_DB'...")
            cursor.execute("CREATE DATABASE new_DB")
            print("✅ Database 'new_DB' created successfully")
        
        # Connect to new_DB and create tables
        conn.close()
        
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='new_DB',
            user='postgres',
            password='191089193'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("🔍 Connected to new_DB database")
        
        # Create commits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commits (
                id TEXT PRIMARY KEY,
                hash VARCHAR(40) UNIQUE NOT NULL,
                author VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                commit_timestamp_utc TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        print("✅ Commits table created/verified")
        
        # Create tracking_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracking_sessions (
                id SERIAL PRIMARY KEY,
                repository VARCHAR(255) NOT NULL,
                branch VARCHAR(100) DEFAULT 'main',
                status VARCHAR(50) DEFAULT 'active',
                started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_commit_hash VARCHAR(40),
                last_polled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        print("✅ Tracking_sessions table created/verified")
        
        # Create ai_analysis table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_analysis (
                id SERIAL PRIMARY KEY,
                commit_hash VARCHAR(40) NOT NULL,
                analysis_type VARCHAR(50) DEFAULT 'commit_analysis',
                analysis_data JSONB NOT NULL,
                model_used VARCHAR(100) DEFAULT 'codellama',
                processing_time_ms INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                FOREIGN KEY (commit_hash) REFERENCES commits(hash) ON DELETE CASCADE
            )
        """)
        
        print("✅ AI_analysis table created/verified")
        
        cursor.close()
        conn.close()
        
        print("🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_database()
