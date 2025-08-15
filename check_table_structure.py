#!/usr/bin/env python3
"""
Check the exact table structure in "new DB"
"""

import psycopg2

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'new DB',
    'user': 'postgres',
    'password': '191089193'
}

def check_table_structure():
    """Check the exact structure of the commits table"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔍 Checking commits table structure...")
        
        # Get all columns from commits table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'commits' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"\n📊 Commits table structure:")
        print(f"{'Column Name':<20} {'Data Type':<25} {'Nullable':<10} {'Default'}")
        print("-" * 70)
        
        for col in columns:
            print(f"{col[0]:<20} {col[1]:<25} {col[2]:<10} {col[3] or 'None'}")
        
        # Check if there are any constraints
        cursor.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'commits'
        """)
        
        constraints = cursor.fetchall()
        print(f"\n🔒 Table constraints:")
        for constraint in constraints:
            print(f"   - {constraint[0]}: {constraint[1]}")
        
        # Check sample data
        cursor.execute("SELECT * FROM commits LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"\n📋 Sample data exists in table")
        else:
            print(f"\n📋 Table is empty")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_table_structure()
