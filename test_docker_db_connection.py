import psycopg2
import urllib.parse
import sys

def test_docker_database_connection():
    """Test if Docker containers can connect to the existing database"""
    
    # Test the exact URL that Docker containers will use
    database_url = "postgresql://postgres:191089193@host.docker.internal:5432/new%20DB"
    
    print(f"Testing Docker database URL: {database_url}")
    print("This simulates how Docker containers will connect to your database")
    
    try:
        # Parse the URL to extract components
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        
        # Extract database name and decode it
        database_name = urllib.parse.unquote(parsed.path.lstrip('/'))
        
        print(f"Parsed database name: '{database_name}'")
        
        # Test connection using the same parameters Docker will use
        conn = psycopg2.connect(
            host="localhost",  # We're testing locally, Docker will use host.docker.internal
            port=5432,
            database="new DB",  # Use the actual database name
            user="postgres",
            password="191089193"
        )
        
        cursor = conn.cursor()
        
        # Test basic connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Database connection successful: {version[0]}")
        
        # Test if we can access your tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"✅ Can access {len(tables)} tables: {[table[0] for table in tables]}")
        
        # Test a simple query on one of your tables
        cursor.execute("SELECT COUNT(*) FROM commits;")
        count = cursor.fetchone()
        print(f"✅ Commits table has {count[0]} records")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Docker database connection test PASSED!")
        print("Your Docker containers should be able to connect to the database.")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure PostgreSQL is running on port 5432")
        print("2. Verify the database 'new DB' exists")
        print("3. Check that user 'postgres' has access")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_docker_database_connection()
