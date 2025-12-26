import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.connection import get_database_info, engine
from sqlalchemy import text

if __name__ == "__main__":
    db_info = get_database_info()

    print("\n" + "=" * 60)
    print("Database Connection Check")
    print("=" * 60)
    print(f"Environment: {db_info['environment']}")
    print(f"Database URL: {db_info['url_masked']}")
    print(f"Host: {db_info['host']}")
    print("=" * 60 + "\n")

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print("✓ Connection successful!")
            print(f"✓ PostgreSQL version: {version.split(',')[0]}")
            
            # Check current database name
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✓ Connected to database: {db_name}")
            print()

            # Check if digests table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'digests'
                )
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("⚠ 'digests' table does not exist!")
                print("  → Run 'python app/database/create_tables.py' to create tables")
                print()
                
                # Show what tables do exist
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                existing_tables = [row[0] for row in result.fetchall()]
                if existing_tables:
                    print(f"Existing tables: {', '.join(existing_tables)}")
                else:
                    print("No tables found in the database")
                sys.exit(1)
            
            # Table exists, proceed with checks
            result = conn.execute(text("SELECT COUNT(*) FROM digests"))
            count = result.scalar()
            print(f"✓ Digests table exists with {count} records")

            result = conn.execute(
                text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'digests' AND column_name = 'sent_at'
            """)
            )
            has_sent_at = result.fetchone() is not None
            if has_sent_at:
                print("✓ sent_at column exists")
            else:
                print("⚠ sent_at column does not exist (run migration)")

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)