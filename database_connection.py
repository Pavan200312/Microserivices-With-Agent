import psycopg2
import urllib.parse
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

def get_database_url():
    """Get properly formatted database URL for the 'new DB' database"""
    
    # Database parameters
    username = "postgres"
    password = "191089193"
    host = "host.docker.internal"  # For Docker containers
    port = "5432"
    database = "new DB"  # Database name with space
    
    # URL encode the database name properly
    encoded_database = urllib.parse.quote(database, safe='')
    
    # Construct the URL
    database_url = f"postgresql://{username}:{password}@{host}:{port}/{encoded_database}"
    
    return database_url

def get_local_database_url():
    """Get database URL for local connections (outside Docker)"""
    
    username = "postgres"
    password = "191089193"
    host = "localhost"
    port = "5432"
    database = "new DB"
    
    # For local connections, we can use the database name directly
    database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    return database_url

def test_connection():
    """Test database connection"""
    try:
        # Test local connection
        local_url = get_local_database_url()
        print(f"Testing local connection: {local_url}")
        
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="new DB",
            user="postgres",
            password="191089193"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Local connection successful: {version[0]}")
        
        cursor.close()
        conn.close()
        
        # Test Docker URL format
        docker_url = get_database_url()
        print(f"\nDocker URL format: {docker_url}")
        print("✅ URL encoding looks correct for Docker containers")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
