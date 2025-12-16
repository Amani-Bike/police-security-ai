import os
from backend.database.db_setup import Base, engine

def create_fresh_database():
    """Create a fresh database with the updated schema"""
    
    # Remove the old database if it exists
    db_path = "police_security.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed old database: {db_path}")
        except:
            print(f"Could not remove {db_path}, it might be in use by another process")
            return

    # Create tables with new schema
    Base.metadata.create_all(bind=engine)
    print("Created fresh database with updated schema including full_name column")
    
    # Verify the schema
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check the users table structure
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    print("\nUsers table structure:")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
    
    conn.close()

if __name__ == "__main__":
    create_fresh_database()