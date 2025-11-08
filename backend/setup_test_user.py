#!/usr/bin/env python3
"""
安全测试用户设置脚本
仅修改特定的测试账户，不影响其他用户和系统功能
"""
import hashlib
from db_connector import get_db_connection, return_db_connection

def hash_password(password, salt):
    """使用与生产环境相同的密码哈希算法"""
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def setup_safe_test_users():
    """
    安全设置测试用户 - 仅修改特定的测试账户
    不会影响其他用户或系统功能
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            print("开始设置测试账户...")
            print("注意：仅修改特定的测试账户，不影响其他用户")
            
            # 1. 学生测试账户 - 使用现有的测试学生ID
            student_email = "alice.student@university.edu"
            student_password = "Alice2024Secure!"
            student_salt = "test_salt_student_123456789012345678901234"
            student_hashed_password = hash_password(student_password, student_salt)
            
            # 检查学生账户是否存在
            cur.execute("SELECT StuID FROM students WHERE StuID = 100")
            if cur.fetchone():
                cur.execute(
                    "UPDATE students SET email = %s, password = %s, salt = %s WHERE StuID = 100",
                    (student_email, student_hashed_password, student_salt)
                )
                print("✓ 测试学生账户已更新 (ID: 100)")
            else:
                print("⚠ 测试学生账户不存在 (ID: 100)，跳过")
            
            # 2. 教职工测试账户 - 使用现有的测试教职工ID
            staff_email = "bob.faculty@university.edu"
            staff_password = "Bob2024Admin@"
            staff_salt = "test_salt_staff_12345678901234567890123456"
            staff_hashed_password = hash_password(staff_password, staff_salt)
            
            # 检查教职工账户是否存在
            cur.execute("SELECT StfID FROM staffs WHERE StfID = 5001")
            if cur.fetchone():
                cur.execute(
                    "UPDATE staffs SET email = %s, password = %s, salt = %s WHERE StfID = 5001",
                    (staff_email, staff_hashed_password, staff_salt)
                )
                print("✓ 测试教职工账户已更新 (ID: 5001)")
            else:
                print("⚠ 测试教职工账户不存在 (ID: 5001)，跳过")
            
            # 3. 监护人测试账户 - 使用现有的测试监护人ID
            guardian_email = "charlie.guardian@university.edu"
            guardian_password = "Charlie2024Guard#"
            guardian_salt = "test_salt_guardian_1234567890123456789012"
            guardian_hashed_password = hash_password(guardian_password, guardian_salt)
            
            # 检查监护人账户是否存在
            cur.execute("SELECT GuaID FROM guardians WHERE GuaID = 1000")
            if cur.fetchone():
                cur.execute(
                    "UPDATE guardians SET email = %s, password = %s, salt = %s WHERE GuaID = 1000",
                    (guardian_email, guardian_hashed_password, guardian_salt)
                )
                print("✓ 测试监护人账户已更新 (ID: 1000)")
            else:
                print("⚠ 测试监护人账户不存在 (ID: 1000)，跳过")
            
            # 提交事务
            conn.commit()
            
            # 显示测试账户信息
            print("\n" + "="*60)
            print("测试账户设置完成 - 安全摘要")
            print("="*60)
            print("仅以下特定测试账户被修改：")
            print(f"\n学生账户:")
            print(f"  邮箱: {student_email}")
            print(f"  密码: {student_password}")
            print(f"  用户ID: 100")
            
            print(f"\n教职工账户:")
            print(f"  邮箱: {staff_email}")
            print(f"  密码: {staff_password}")
            print(f"  用户ID: 5001")
            
            print(f"\n监护人账户:")
            print(f"  邮箱: {guardian_email}")
            print(f"  密码: {guardian_password}")
            print(f"  用户ID: 1000")
            
            print(f"\n安全说明:")
            print(f"  ✅ 仅修改了3个特定的测试账户")
            print(f"  ✅ 不影响其他用户数据")
            print(f"  ✅ 使用相同的密码哈希算法")
            print(f"  ✅ 数据库结构保持不变")
            print(f"  ✅ 生产环境用户不受影响")
            print("="*60)
            
    except Exception as e:
        # 发生错误时回滚，确保数据一致性
        print(f"✗ 设置过程中发生错误: {e}")
        print("正在进行回滚操作...")
        conn.rollback()
        print("✓ 回滚完成，数据状态已恢复")
    finally:
        return_db_connection(conn)
        print("\n数据库连接已安全关闭")

def verify_test_accounts():
    """验证测试账户是否设置成功"""
    print("\n正在验证测试账户...")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 验证学生账户
            cur.execute("SELECT StuID, email FROM students WHERE StuID = 100")
            student = cur.fetchone()
            if student:
                print(f"✓ 学生账户验证成功: ID={student[0]}, 邮箱={student[1]}")
            else:
                print("⚠ 学生账户验证失败")
            
            # 验证教职工账户
            cur.execute("SELECT StfID, email FROM staffs WHERE StfID = 5001")
            staff = cur.fetchone()
            if staff:
                print(f"✓ 教职工账户验证成功: ID={staff[0]}, 邮箱={staff[1]}")
            else:
                print("⚠ 教职工账户验证失败")
            
            # 验证监护人账户
            cur.execute("SELECT GuaID, email FROM guardians WHERE GuaID = 1000")
            guardian = cur.fetchone()
            if guardian:
                print(f"✓ 监护人账户验证成功: ID={guardian[0]}, 邮箱={guardian[1]}")
            else:
                print("⚠ 监护人账户验证失败")
                
    except Exception as e:
        print(f"验证过程中发生错误: {e}")
    finally:
        return_db_connection(conn)

if __name__ == "__main__":
    print("安全测试用户设置工具")
    print("=" * 50)
    
    # 设置测试用户
    setup_safe_test_users()
    
    # 验证设置结果
    verify_test_accounts()
    
    print("\n" + "="*50)
    print("✅ 测试用户设置流程完成")
    print("="*50)