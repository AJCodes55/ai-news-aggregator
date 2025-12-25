"""
Migration script to add markdown column to x_posts table.
Run this once to update the existing table schema.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.database.connection import engine

if __name__ == "__main__":
    with engine.connect() as conn:
        try:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='x_posts' AND column_name='markdown'
            """))
            exists = result.fetchone()
            
            if exists:
                print("Column 'markdown' already exists in x_posts table")
            else:
                # Add the markdown column
                conn.execute(text("ALTER TABLE x_posts ADD COLUMN markdown TEXT"))
                conn.commit()
                print("Successfully added 'markdown' column to x_posts table")
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
            raise

