"""
Database migration script to add timestamp columns to existing users table
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def migrate_database():
    print("SafetyNet Database Migration")
    print("=" * 30)

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
            conn.close()
            return

        # Check if we need to recreate the table (SQLite doesn't support adding multiple columns easily)
        print("Checking if we need to recreate the table...")

        # Get the current table structure to recreate it
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
        current_table_sql = cursor.fetchone()[0]
        print(f"Current table schema: {current_table_sql}")

        # Since we added timestamp columns to our model, we need to recreate with new schema
        # First, backup the data
        cursor.execute("SELECT * FROM users")
        existing_users = cursor.fetchall()

        print(f"Found {len(existing_users)} existing users to migrate...")

        # Get column names (excluding the new timestamp columns)
        cursor.execute("PRAGMA table_info(users)")
        current_columns = [column[1] for column in cursor.fetchall() if column[1] not in ['created_at', 'updated_at']]

        print(f"Current data columns: {current_columns}")

        # Drop the old table
        cursor.execute("DROP TABLE users")

        # Create the new table with timestamps (this will use the new model definition)
        from backend.models.user_model import User
        from backend.database.db_setup import Base
        Base.metadata.create_all(conn)
        print("New table created with timestamp columns.")

        # Prepare the insert statement (without timestamp columns, they'll be auto-populated)
        placeholders = ', '.join(['?' for _ in current_columns])
        columns_str = ', '.join(current_columns)
        insert_sql = f"INSERT INTO users ({columns_str}) VALUES ({placeholders})"

        # Insert the old data back
        for user in existing_users:
            # Only insert the values for the original columns
            user_values = user[:len(current_columns)]  # Only values for existing columns
            cursor.execute(insert_sql, user_values)

        conn.commit()
        print(f"Successfully migrated {len(existing_users)} users to new table structure!")
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {str(e)}")
        print("Attempting to rollback...")
        conn.rollback()
        conn.close()
        raise
    finally:
        conn.close()

def recreate_database():
    """Option to recreate the database with the new schema"""
    print("\nRecreating database with new schema...")
    
    import sqlite3
    
    # Remove the existing database
    db_path = os.path.join(project_root, "police_security.db")
    
    if os.path.exists(db_path):
        backup_path = db_path.replace(".db", "_backup.db")
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Backup created: {backup_path}")
        os.remove(db_path)
        print("Old database removed.")
    
    # Create new database with updated schema
    from backend.database.db_setup import create_tables
    create_tables()
    print("New database created with updated schema.")
    
    # Try to copy data from backup if possible (this is complex and may need manual handling)
    print(f"\nOriginal database backed up as: {backup_path}")
    print("You can manually migrate data if needed.")

def main():
    print("SafetyNet Database Migration Tool")
    print("1. Attempt to migrate existing database (may not work with SQLite)")
    print("2. Recreate database with new schema (creates backup first)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        migrate_database()
    elif choice == "2":
        response = input("This will backup and recreate your database. Continue? (y/N): ")
        if response.lower() == 'y':
            recreate_database()
        else:
            print("Operation cancelled.")
    elif choice == "3":
        print("Goodbye!")
        return
    else:
        print("Invalid choice. Please try again.")
        main()

if __name__ == "__main__":
    main()