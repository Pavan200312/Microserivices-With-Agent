import psycopg2

try:
    conn = psycopg2.connect(
        host='host.docker.internal',
        port=5432,
        database='new DB',
        user='postgres',
        password='191089193'
    )
    print("✅ Connected successfully!")
    conn.close()
except Exception as e:
    print(f"❌ Failed: {e}")
