"""
Admin user creation script for SafetyNet app
This script allows you to create or update an admin user in the database
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.database.db_setup import get_db, SessionLocal
from backend.models.user_model import User
from backend.utils.security import hash_password
from sqlalchemy.orm import Session

def create_admin_user():
    db = SessionLocal()
    
    try:
        print("SafetyNet Admin User Creator")
        print("=" * 30)
        
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.username} (ID: {existing_admin.id})")
            response = input("Do you want to create another admin? (y/N): ")
            if response.lower() != 'y':
                return
        
        username = input("Enter admin username: ").strip()
        email = input("Enter admin email: ").strip()
        password = input("Enter admin password: ").strip()
        
        if not username or not email or not password:
            print("Error: All fields are required!")
            return
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"User with username '{username}' or email '{email}' already exists!")
            response = input("Do you want to update their role to admin instead? (y/N): ")
            if response.lower() == 'y':
                existing_user.role = "admin"
                db.commit()
                print(f"User {existing_user.username} (ID: {existing_user.id}) updated to admin role!")
                return
            else:
                return
        
        # Create new admin user
        hashed_password = hash_password(password)
        admin_user = User(
            username=username,
            email=email,
            password=hashed_password,
            role="admin"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Admin user created successfully!")
        print(f"Username: {admin_user.username}")
        print(f"Email: {admin_user.email}")
        print(f"User ID: {admin_user.id}")
        print(f"Role: {admin_user.role}")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {str(e)}")
    finally:
        db.close()

def list_all_users():
    db = SessionLocal()
    
    try:
        users = db.query(User).order_by(User.id).all()
        
        if not users:
            print("No users found in the database.")
            return
        
        print(f"Total users: {len(users)}")
        print("=" * 80)
        print(f"{'ID':<5} {'Username':<20} {'Email':<25} {'Role':<10} {'Created':<20}")
        print("-" * 80)
        
        for user in users:
            created_str = user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "N/A"
            print(f"{user.id:<5} {user.username[:19]:<20} {user.email[:24] if user.email else 'N/A':<25} {user.role:<10} {created_str:<20}")
            
    except Exception as e:
        print(f"Error listing users: {str(e)}")
    finally:
        db.close()

def make_user_admin():
    db = SessionLocal()
    
    try:
        user_id = int(input("Enter user ID to make admin: ").strip())
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"No user found with ID {user_id}")
            return
        
        print(f"Current user: {user.username} (Role: {user.role})")
        response = input(f"Make user {user.username} an admin? (y/N): ")
        
        if response.lower() == 'y':
            user.role = "admin"
            db.commit()
            print(f"User {user.username} (ID: {user.id}) updated to admin role!")
        else:
            print("Operation cancelled.")
            
    except ValueError:
        print("Invalid user ID. Please enter a number.")
    except Exception as e:
        print(f"Error updating user: {str(e)}")
    finally:
        db.close()

def main():
    print("SafetyNet Admin Management Tool")
    print("1. Create new admin user")
    print("2. List all users")
    print("3. Make existing user admin")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        create_admin_user()
    elif choice == "2":
        list_all_users()
    elif choice == "3":
        make_user_admin()
    elif choice == "4":
        print("Goodbye!")
        return
    else:
        print("Invalid choice. Please try again.")
        main()

if __name__ == "__main__":
    main()