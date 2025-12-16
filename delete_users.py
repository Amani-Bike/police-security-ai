import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.database.db_setup import SessionLocal
from backend.models.user_model import User

def delete_non_admin_users():
    db = SessionLocal()
    
    try:
        # Count existing users by role
        all_users = db.query(User).all()
        print(f"Total users found: {len(all_users)}")
        
        for user in all_users:
            print(f"  - ID: {user.id}, Username: {user.username}, Role: {user.role}, Email: {user.email}")
        
        # Get non-admin users
        non_admin_users = db.query(User).filter(User.role != "admin").all()
        print(f"\nFound {len(non_admin_users)} civilian/police users to delete")
        
        # Delete non-admin users
        for user in non_admin_users:
            db.delete(user)
        
        db.commit()
        print(f"\nSuccessfully deleted {len(non_admin_users)} civilian and police users!")
        
        # Verify deletion
        remaining_users = db.query(User).all()
        print(f"Remaining users: {len(remaining_users)}")
        for user in remaining_users:
            print(f"  - ID: {user.id}, Username: {user.username}, Role: {user.role}")
            
    except Exception as e:
        print(f"Error during deletion: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    delete_non_admin_users()