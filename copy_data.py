#!/usr/bin/env python3
"""
Copy data from "new DB" to new_DB
"""

import psycopg2

def copy_data():
    """Copy data from existing database to new one"""
    try:
        # Connect to existing "new DB"
        conn_old = psycopg2.connect(
            host='localhost',
            port=5432,
            database='new DB',
            user='postgres',
            password='191089193'
        )
        
        print("✅ Connected to 'new DB'")
        
        # Create new database
        conn_postgres = psycopg2.connect(
            host='localhost',
            port=5432,
            database='postgres',
            user='postgres',
            password='191089193'
        )
        conn_postgres.autocommit = True
        cursor_postgres = conn_postgres.cursor()
        
        # Create new_DB if it doesn't exist
        cursor_postgres.execute("SELECT 1 FROM pg_database WHERE datname = 'new_DB'")
        if not cursor_postgres.fetchone():
            cursor_postgres.execute("CREATE DATABASE new_DB")
            print("✅ Created new_DB database")
        
        cursor_postgres.close()
        conn_postgres.close()
        
        # Connect to new_DB
        conn_new = psycopg2.connect(
            host='localhost',
            port=5432,
            database='new_DB',
            user='postgres',
            password='191089193'
        )
        
        print("✅ Connected to new_DB")
        
        # Create tables in new_DB
        cursor_new = conn_new.cursor()
        
        cursor_new.execute("""
            CREATE TABLE IF NOT EXISTS commits (
                id TEXT PRIMARY KEY,
                hash VARCHAR(40) UNIQUE NOT NULL,
                author VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                commit_timestamp_utc TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        cursor_new.execute("""
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
        
        cursor_new.execute("""
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
        
        print("✅ Tables created in new_DB")
        
        # Copy data from old to new
        cursor_old = conn_old.cursor()
        cursor_old.execute("SELECT * FROM commits")
        commits = cursor_old.fetchall()
        
        print(f"📊 Found {len(commits)} commits to copy")
        
        for commit in commits:
            try:
                cursor_new.execute("""
                    INSERT INTO commits (id, hash, author, message, commit_timestamp_utc, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, commit)
            except Exception as e:
                print(f"⚠️ Error copying commit: {e}")
        
        conn_new.commit()
        print("✅ Data copied successfully!")
        
        cursor_old.close()
        cursor_new.close()
        conn_old.close()
        conn_new.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    copy_data()
