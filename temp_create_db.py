import sqlite3
import os

def create_db_with_full_name():
    conn = sqlite3.connect("temp_police_security.db")
    cursor = conn.cursor()
    
    # Create users table with full_name field
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            full_name VARCHAR(255),
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'civilian',
            latitude REAL,
            longitude REAL
        )
    ''')
    
    # Create emergency_reports table (same as before)
    cursor.execute('''
        CREATE TABLE emergency_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username VARCHAR(255) NOT NULL,
            emergency_type VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            status VARCHAR(50) DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_by INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("Temporary database created with full_name column")
    
    # Now try to replace the old database file
    if os.path.exists("police_security.db"):
        os.remove("police_security.db")
        print("Removed old database file")
    
    os.rename("temp_police_security.db", "police_security.db")
    print("Renamed temporary database to police_security.db")

if __name__ == "__main__":
    create_db_with_full_name()