import sys
from datetime import datetime
from app import app, db, User, EmailHistory
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text


def print_all_records():
    print("\n=== User Records ===")
    users = User.query.all()
    if not users:
        print("No users found in database.")
    else:
        for user in users:
            print(f"\nUser ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Name: {user.name}")
            print("-" * 50)

    print("\n=== Email History Records ===")
    history = EmailHistory.query.all()
    if not history:
        print("No email history records found in database.")
    else:
        for record in history:
            print(f"\nHistory ID: {record.id}")
            print(f"User ID: {record.user_id}")
            print(f"Contact Name: {record.contact_name}")
            print(f"Contact Company: {record.contact_company}")
            print(f"Email Draft: {record.email_draft[:100]}...")
            print(f"Created At: {record.created_at}")
            print("-" * 50)

def delete_all_records():
    try:
        # Delete all records from all tables
        EmailHistory.query.delete()
        User.query.delete()
        db.session.commit()
        print("Successfully deleted all records from the database.")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting records: {str(e)}")

def upgrade_database():
    try:
        with app.app_context():
            # Drop existing tables
            db.drop_all()
            print("Existing tables dropped successfully.")
            
            # Create new tables with updated schema
            db.create_all()
            print("New database schema created successfully!")
            
            # Create a test user
            test_user = User(
                email="test@example.com",
                name="Test User",
                resume_filename="test.pdf",
                resume_content="Sample content",
                resume_file_type="pdf",
                career_interest="Test interest"
            )
            test_user.set_password("password123")
            test_user.set_key_accomplishments([
                "Test accomplishment 1",
                "Test accomplishment 2"
            ])
            
            db.session.add(test_user)
            db.session.commit()
            
            # Create a test email history record
            test_history = EmailHistory(
                user_id=test_user.id,
                contact_name="John Doe",
                contact_company="Test Company",
                email_draft="This is a test email draft..."
            )
            
            db.session.add(test_history)
            db.session.commit()
            print("Test records created successfully to verify schema!")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error upgrading database: {str(e)}")

def main():
    with app.app_context():
        while True:
            print("\nDatabase Management Tool")
            print("1. Print all records")
            print("2. Delete all records")
            print("3. Upgrade database schema")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == "1":
                print_all_records()
            elif choice == "2":
                confirm = input("Are you sure you want to delete all records? This cannot be undone! (yes/no): ")
                if confirm.lower() == 'yes':
                    delete_all_records()
                else:
                    print("Delete operation cancelled.")
            elif choice == "3":
                confirm = input("This will reset the database and create a new schema. All existing data will be lost! Continue? (yes/no): ")
                if confirm.lower() == 'yes':
                    upgrade_database()
                else:
                    print("Database upgrade cancelled.")
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()