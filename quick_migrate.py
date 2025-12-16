import sys
import os
import sqlite3

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def quick_migrate():
    db_path = os.path.join(project_root, "police_security.db")
    
    if not os.path.exists(db_path):
        print("Database not found. Creating with new schema...")
        from backend.database.db_setup import create_tables
        create_tables()
        print("New database created with updated schema.")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns in users table: {columns}")
        
        # Check if timestamp columns already exist
        if 'created_at' in columns and 'updated_at' in columns:
            print("Timestamp columns already exist. Migration not needed.")
        else:
            print("Adding timestamp columns to users table...")
            
            # Backup existing data first
            cursor.execute("SELECT * FROM users")
            existing_users = cursor.fetchall()
            
            # Get current column names (based on old schema)
            current_columns = [col for col in columns if col not in ['created_at', 'updated_at']]
            print(f"Current data columns: {current_columns}")
            
            # Create a new table with the correct schema using raw SQL
            cursor.execute("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR UNIQUE NOT NULL,
                    email VARCHAR UNIQUE,
                    phone VARCHAR UNIQUE,
                    badge_id VARCHAR UNIQUE,
                    full_name VARCHAR,
                    password VARCHAR NOT NULL,
                    role VARCHAR DEFAULT 'civilian',
                    latitude FLOAT,
                    longitude FLOAT,
                    photo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Copy data from old table to new table
            if current_columns:
                columns_str = ', '.join(current_columns)
                placeholders = ', '.join(['?' for _ in current_columns])
                
                for user in existing_users:
                    user_values = user[:len(current_columns)]  # Only values for existing columns
                    cursor.execute(f"INSERT INTO users_new ({columns_str}) VALUES ({placeholders})", user_values)
            
            # Drop the old table and rename the new one
            cursor.execute("DROP TABLE users")
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            
            conn.commit()
            print(f"Successfully migrated {len(existing_users)} users to new table structure!")
            print("Migration completed successfully!")
    
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    quick_migrate()