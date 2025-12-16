import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.database.db_setup import SessionLocal
from backend.models.user_model import User
from sqlalchemy.orm import Session

def reset_users():
    db = SessionLocal()
    
    try:
        # Count existing users
        all_users = db.query(User).all()
        print(f"Found {len(all_users)} users in database")
        
        for user in all_users:
            print(f"  - ID: {user.id}, Username: {user.username}, Role: {user.role}, Email: {user.email}")
        
        print("\nDeleting all users...")
        # Delete all users except potential admin accounts if you want to keep them
        confirm = input(f"Are you sure you want to delete ALL {len(all_users)} users? (yes/no): ")
        
        if confirm.lower() == 'yes':
            db.query(User).delete()
            db.commit()
            print("All users have been deleted successfully!")
        else:
            print("Operation cancelled.")
            
    except Exception as e:
        print(f"Error during reset: {str(e)}")
        db.rollback()
    finally:
        db.close()

def reset_non_admin_users():
    """Reset all users except admin accounts"""
    db = SessionLocal()
    
    try:
        # Get all non-admin users
        non_admin_users = db.query(User).filter(User.role != "admin").all()
        print(f"Found {len(non_admin_users)} non-admin users")
        
        for user in non_admin_users:
            print(f"  - ID: {user.id}, Username: {user.username}, Role: {user.role}, Email: {user.email}")
        
        if non_admin_users:
            print("\nDeleting all non-admin users...")
            confirm = input(f"Are you sure you want to delete these {len(non_admin_users)} users? (yes/no): ")
            
            if confirm.lower() == 'yes':
                for user in non_admin_users:
                    db.delete(user)
                db.commit()
                print("Non-admin users have been deleted successfully!")
            else:
                print("Operation cancelled.")
        else:
            print("No non-admin users found.")
            
    except Exception as e:
        print(f"Error during reset: {str(e)}")
        db.rollback()
    finally:
        db.close()

def main():
    print("SafetyNet User Data Reset Tool")
    print("1. Delete ALL users (including admins)")
    print("2. Delete only civilian and police users (keep admins)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        reset_users()
    elif choice == "2":
        reset_non_admin_users()
    elif choice == "3":
        print("Goodbye!")
        return
    else:
        print("Invalid choice. Please try again.")
        main()

if __name__ == "__main__":
    main()