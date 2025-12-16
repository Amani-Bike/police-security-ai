import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.database.db_setup import SessionLocal
from backend.models.user_model import User
from backend.utils.security import hash_password

def create_admin():
    db = SessionLocal()
    
    try:
        # Create an admin user
        admin_username = "admin"
        admin_email = "admin@safetynet.com"
        admin_password = "admin123"
        
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.username}")
            return
        
        # Create new admin user
        hashed_password = hash_password(admin_password)
        admin_user = User(
            username=admin_username,
            email=admin_email,
            password=hashed_password,
            role="admin"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Admin user created successfully!")
        print(f"Username: {admin_user.username}")
        print(f"Email: {admin_user.email}")
        print(f"Password: {admin_password} (for testing)")
        print(f"Role: {admin_user.role}")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {str(e)}")
    finally:
        db.close()

def list_users():
    db = SessionLocal()
    
    try:
        users = db.query(User).order_by(User.id).all()
        
        print(f"Total users: {len(users)}")
        print("=" * 80)
        print(f"{'ID':<5} {'Username':<20} {'Email':<25} {'Role':<10} {'Created':<20}")
        print("-" * 80)
        
        for user in users:
            created_str = str(user.created_at)[:16] if user.created_at else "N/A"
            print(f"{user.id:<5} {user.username[:19]:<20} {user.email[:24] if user.email else 'N/A':<25} {user.role:<10} {created_str:<20}")
            
    except Exception as e:
        print(f"Error listing users: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating admin user...")
    create_admin()
    print("\nListing all users...")
    list_users()