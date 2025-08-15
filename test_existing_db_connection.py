import psycopg2
from psycopg2 import sql
import sys

def test_database_connection():
    """Test connection to the existing 'new DB' database"""
    
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'new DB',
        'user': 'postgres',
        'password': '191089193'
    }
    
    try:
        # Connect to the database
        print("Attempting to connect to existing database 'new DB'...")
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Test basic connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Successfully connected to PostgreSQL: {version[0]}")
        
        # List all schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name;
        """)
        schemas = cursor.fetchall()
        print(f"📋 Available schemas: {[schema[0] for schema in schemas]}")
        
        # List tables in public schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"📊 Tables in public schema: {[table[0] for table in tables]}")
        
        # Show table structures
        for table in tables:
            table_name = table[0]
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print(f"\n📋 Table '{table_name}' structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        cursor.close()
        conn.close()
        print("\n✅ Database connection test completed successfully!")
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_database_connection()
