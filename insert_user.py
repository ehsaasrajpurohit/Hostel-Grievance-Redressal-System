import argparse
from werkzeug.security import generate_password_hash
from datetime import datetime
from main import app, db, Users  # Import your Flask app, db, and Users model

def insert_user(usn, username, password, email, utype, date_of_birth, guardians_name=None, phone_number=None):
    """Insert a new user into the database."""

    with app.app_context():  # Ensure the code runs inside Flask's app context

        # Generate hashed password
        hashed_password = generate_password_hash(password)

        # Parse date of birth string into a date object
        try:
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

        # Create a new user instance
        user = Users(
            usn=usn,
            username=username,
            password=hashed_password,
            email=email,
            utype=utype,
            date_of_birth=dob,
            guardians_name=guardians_name,
            phone_number=phone_number
        )

        # Insert into the database
        try:
            db.session.add(user)
            db.session.commit()
            print(f"User {username} with USN {usn} added successfully.")
        except Exception as e:
            print(f"Error adding user: {e}")
            db.session.rollback()

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Sign up a new user via CLI and insert into the database.")

    # Define arguments for user input
    parser.add_argument(
        '-u', '--usn', required=True, help="USN (Unique Serial Number), e.g., 1RV21IS001"
    )
    parser.add_argument(
        '-n', '--username', required=True, help="Username for the account"
    )
    parser.add_argument(
        '-p', '--password', required=True, help="Password for the account"
    )
    parser.add_argument(
        '-e', '--email', required=True, help="Email address for the user"
    )
    parser.add_argument(
        '-t', '--utype', required=True, choices=['Student', 'employee', 'manager'], help="User type (e.g., Student, employee, manager)"
    )
    parser.add_argument(
        '-d', '--date_of_birth', required=True, help="Date of birth in the format YYYY-MM-DD"
    )
    parser.add_argument(
        '-g', '--guardians_name', help="Guardian's Name (Optional)"
    )
    parser.add_argument(
        '-ph', '--phone_number', help="Phone Number (Optional)"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Confirm before inserting the user
    print("\nYou are about to insert the following user into the database:")
    print(f"USN: {args.usn}")
    print(f"Username: {args.username}")
    print(f"Email: {args.email}")
    print(f"User Type: {args.utype}")
    print(f"Date of Birth: {args.date_of_birth}")
    print(f"Guardian's Name: {args.guardians_name}")
    print(f"Phone Number: {args.phone_number}")
    
    confirm = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        # Insert the user into the database
        insert_user(
            usn=args.usn,
            username=args.username,
            password=args.password,
            email=args.email,
            utype=args.utype,
            date_of_birth=args.date_of_birth,
            guardians_name=args.guardians_name,
            phone_number=args.phone_number
        )
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()


# python3 insert_user.py --usn 1RV21IS001 --username john_doe --password secret123 --email john@example.com --utype manager --date_of_birth 2000-01-15 --guardians_name "John's Guardian" --phone_number 1234567890
