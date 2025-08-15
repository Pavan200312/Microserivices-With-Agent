#!/usr/bin/env python3
"""
Test script to verify database connection to "new DB"
"""

import psycopg2
import json
from datetime import datetime

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'new DB',  # Note the space in the name
    'user': 'postgres',
    'password': '191089193'
}

def test_connection():
    """Test database connection"""
    try:
        print("🔍 Testing database connection...")
        print(f"Host: {DB_CONFIG['host']}")
        print(f"Port: {DB_CONFIG['port']}")
        print(f"Database: '{DB_CONFIG['database']}'")
        print(f"User: {DB_CONFIG['user']}")
        
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Database connection successful!")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('commits', 'tracking_sessions', 'ai_analysis')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"📋 Found {len(tables)} required tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check commits table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'commits' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"\n📊 Commits table structure:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]}")
        
        # Test inserting a sample commit
        sample_commit = {
            'commit_hash': 'test1234567890abcdef1234567890abcdef12345678',
            'author': 'Test User',
            'author_email': 'test@example.com',
            'message': 'Test commit from Python script',
            'timestamp': datetime.now(),
            'repository': 'test/repo',
            'branch': 'main',
            'files_changed': json.dumps([
                {
                    'status': 'added',
                    'filename': 'test.txt',
                    'additions': 1,
                    'deletions': 0
                }
            ])
        }
        
        cursor.execute("""
            INSERT INTO commits (commit_hash, author, author_email, message, timestamp, repository, branch, files_changed)
            VALUES (%(commit_hash)s, %(author)s, %(author_email)s, %(message)s, %(timestamp)s, %(repository)s, %(branch)s, %(files_changed)s::jsonb)
            ON CONFLICT (commit_hash) DO NOTHING
        """, sample_commit)
        
        conn.commit()
        print("✅ Successfully inserted test commit!")
        
        # Count commits
        cursor.execute("SELECT COUNT(*) FROM commits")
        count = cursor.fetchone()[0]
        print(f"📈 Total commits in database: {count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
