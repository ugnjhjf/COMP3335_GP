# Test Users

This document lists all test user accounts available in the system.

## Test User Accounts

### 1. Student Account
- **Email**: `test_student@example.com`
- **Password**: `StudentTest123`
- **User ID**: 100 (StuID)
- **Name**: Mia Chow
- **Role**: student
- **Purpose**: Used for testing student-related functionality and SQL injection tests

### 2. Guardian Account
- **Email**: `test_guardian@example.com`
- **Password**: `GuardianTest123`
- **User ID**: 1000 (GuaID)
- **Name**: David Chow
- **Role**: guardian
- **Purpose**: Used for testing guardian-related functionality

### 3. Staff Account
- **Email**: `test_staff@example.com`
- **Password**: `StaffTest123`
- **User ID**: 5001 (StfID)
- **Name**: Bob Tang
- **Role**: staff
- **Department**: Academic Affairs
- **Position**: Accountant
- **Purpose**: Used for testing staff-related functionality

## Usage Notes

- All test users are created in `load_sql/University.sql`
- Passwords are hashed using SHA256 with salt
- Test users are used in attack tests located in `backend/attack/` directory
- These accounts should only be used in development/testing environments

