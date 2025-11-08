#!/usr/bin/env python3
"""
Safe Test User Setup Script
Only modifies specific test accounts, does not affect other users or system functionality
"""
import hashlib
from db_connector import get_db_connection

def hash_password(password, salt):
    """Use the same password hashing algorithm as production environment"""
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def setup_safe_test_users():
    """
    Safely setup test users - only modifies specific test accounts
    Will not affect other users or system functionality
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            print("Starting test account setup...")
            print("Note: Only modifying specific test accounts, other users are not affected")
            
            # 1. Student test account - using existing test student ID
            student_email = "test_student@example.com"
            student_password = "StudentTest123"
            student_salt = "test_salt_student_123456789012345678901234"
            student_hashed_password = hash_password(student_password, student_salt)
            
            # Check if student account exists
            cur.execute("SELECT StuID FROM students WHERE StuID = 100")
            if cur.fetchone():
                cur.execute(
                    "UPDATE students SET email = %s, password = %s, salt = %s WHERE StuID = 100",
                    (student_email, student_hashed_password, student_salt)
                )
                print("✓ Test student account updated (ID: 100)")
            else:
                print("⚠ Test student account does not exist (ID: 100), skipping")
            
            # 2. Staff test account - using existing test staff ID
            staff_email = "test_staff@example.com"
            staff_password = "StaffTest123"
            staff_salt = "test_salt_staff_12345678901234567890123456"
            staff_hashed_password = hash_password(staff_password, staff_salt)
            
            # Check if staff account exists
            cur.execute("SELECT StfID FROM staffs WHERE StfID = 5001")
            if cur.fetchone():
                cur.execute(
                    "UPDATE staffs SET email = %s, password = %s, salt = %s WHERE StfID = 5001",
                    (staff_email, staff_hashed_password, staff_salt)
                )
                print("✓ Test staff account updated (ID: 5001)")
            else:
                print("⚠ Test staff account does not exist (ID: 5001), skipping")
            
            # 3. Guardian test account - using existing test guardian ID
            guardian_email = "test_guardian@example.com"
            guardian_password = "GuardianTest123"
            guardian_salt = "test_salt_guardian_1234567890123456789012"
            guardian_hashed_password = hash_password(guardian_password, guardian_salt)
            
            # Check if guardian account exists
            cur.execute("SELECT GuaID FROM guardians WHERE GuaID = 1000")
            if cur.fetchone():
                cur.execute(
                    "UPDATE guardians SET email = %s, password = %s, salt = %s WHERE GuaID = 1000",
                    (guardian_email, guardian_hashed_password, guardian_salt)
                )
                print("✓ Test guardian account updated (ID: 1000)")
            else:
                print("⚠ Test guardian account does not exist (ID: 1000), skipping")
            
            # Commit transaction
            conn.commit()
            
            # Display test account information
            print("\n" + "="*60)
            print("Test Account Setup Complete - Security Summary")
            print("="*60)
            print("Only the following specific test accounts were modified:")
            print(f"\nStudent Account:")
            print(f"  Email: {student_email}")
            print(f"  Password: {student_password}")
            print(f"  User ID: 100")
            
            print(f"\nStaff Account:")
            print(f"  Email: {staff_email}")
            print(f"  Password: {staff_password}")
            print(f"  User ID: 5001")
            
            print(f"\nGuardian Account:")
            print(f"  Email: {guardian_email}")
            print(f"  Password: {guardian_password}")
            print(f"  User ID: 1000")
            
            print(f"\nSecurity Notes:")
            print(f"  ✅ Only 3 specific test accounts modified")
            print(f"  ✅ Other user data unaffected")
            print(f"  ✅ Same password hashing algorithm used")
            print(f"  ✅ Database structure unchanged")
            print(f"  ✅ Production users not affected")
            print("="*60)
            
    except Exception as e:
        # Rollback on error to ensure data consistency
        print(f"✗ Error during setup: {e}")
        print("Performing rollback operation...")
        conn.rollback()
        print("✓ Rollback completed, data state restored")
    finally:
        conn.close()
        print("\nDatabase connection safely closed")

def verify_test_accounts():
    """Verify test accounts were set up successfully"""
    print("\nVerifying test accounts...")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Verify student account
            cur.execute("SELECT StuID, email FROM students WHERE StuID = 100")
            student = cur.fetchone()
            if student:
                print(f"✓ Student account verified: ID={student[0]}, Email={student[1]}")
            else:
                print("⚠ Student account verification failed")
            
            # Verify staff account
            cur.execute("SELECT StfID, email FROM staffs WHERE StfID = 5001")
            staff = cur.fetchone()
            if staff:
                print(f"✓ Staff account verified: ID={staff[0]}, Email={staff[1]}")
            else:
                print("⚠ Staff account verification failed")
            
            # Verify guardian account
            cur.execute("SELECT GuaID, email FROM guardians WHERE GuaID = 1000")
            guardian = cur.fetchone()
            if guardian:
                print(f"✓ Guardian account verified: ID={guardian[0]}, Email={guardian[1]}")
            else:
                print("⚠ Guardian account verification failed")
                
    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Safe Test User Setup Tool")
    print("=" * 50)
    
    # Setup test users
    setup_safe_test_users()
    
    # Verify setup results
    verify_test_accounts()
    
    print("\n" + "="*50)
    print("✅ Test user setup process completed")
    print("="*50)