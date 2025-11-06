#!/usr/bin/env python3
"""
Script to set up a test user with a known password
This will update the database with a test password for easy testing
"""
import hashlib
from db_connector import get_db_connection

def hash_password(password, salt):
    """Hash password with salt using SHA-256"""
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def setup_test_user():
    """Set up a test user with email and password: test@test.com / test123"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Test password: test123
            # Test email: test@test.com
            test_password = "test123"
            test_email = "test@test.com"
            
            # Generate salt (varchar(64) - max 64 characters)
            salt = "test_salt_12345678901234567890123456789012345678901234567890"
            
            # Hash password
            hashed_password = hash_password(test_password, salt)
            
            # Update a student account (StuID 100) with test credentials
            cur.execute(
                "UPDATE students SET email = %s, password = %s, salt = %s WHERE StuID = 100",
                (test_email, hashed_password, salt)
            )
            
            print(f"✓ Test student account updated!")
            print(f"  Email: {test_email}")
            print(f"  Password: {test_password}")
            print(f"  User ID: 100 (StuID)")
            print(f"  Role: student")
            
            # Also update a staff account (StfID 5001) - Academic Affairs -> aro role
            cur.execute(
                "UPDATE staffs SET email = %s, password = %s, salt = %s WHERE StfID = 5001",
                (test_email, hashed_password, salt)
            )
            
            print(f"\n✓ Test staff account updated!")
            print(f"  Email: {test_email}")
            print(f"  Password: {test_password}")
            print(f"  User ID: 5001 (StfID)")
            print(f"  Role: aro (Academic Affairs)")
            
            # Also update a guardian account (GuaID 1000)
            cur.execute(
                "UPDATE guardians SET email = %s, password = %s, salt = %s WHERE GuaID = 1000",
                (test_email, hashed_password, salt)
            )
            
            print(f"\n✓ Test guardian account updated!")
            print(f"  Email: {test_email}")
            print(f"  Password: {test_password}")
            print(f"  User ID: 1000 (GuaID)")
            print(f"  Role: guardian")
            
            print(f"\n" + "="*50)
            print(f"Test Account Credentials:")
            print(f"  Email: {test_email}")
            print(f"  Password: {test_password}")
            print(f"\nYou can login with this account as:")
            print(f"  - Student (role: student)")
            print(f"  - Staff (role: aro)")
            print(f"  - Guardian (role: guardian)")
            print(f"="*50)
            
    finally:
        conn.close()

if __name__ == "__main__":
    setup_test_user()

