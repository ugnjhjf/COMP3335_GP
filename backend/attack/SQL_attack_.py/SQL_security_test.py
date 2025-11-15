#!/usr/bin/env python3
"""
MySQL 数据库安全性测试脚本
用于检测SQL注入漏洞和其他安全问题
"""
import mysql.connector
import re
import requests
from bs4 import BeautifulSoup

class MySQLSecurityTester:
    def __init__(self, db_config):
        self.db_config = db_config
        self.results = []
    
    def test_sql_injection(self, url, form_data):
        """测试Web表单的SQL注入漏洞"""
        print("正在测试SQL注入漏洞...")
        
        # SQL注入测试向量
        injection_vectors = [
            {"field": "' OR '1'='1", "description": "基础布尔注入"},
            {"field": "' OR '1'='1' --", "description": "注释符注入"},
            {"field": "'; DROP TABLE users; --", "description": "破坏性注入"},
            {"field": "' UNION SELECT username, password FROM users --", "description": "联合查询注入"},
            {"field": "' OR SLEEP(5) --", "description": "时间盲注"},
            {"field": "test@test.com' AND 1=1 --", "description": "永真条件注入"}
        ]
        
        for vector in injection_vectors:
            print(f"测试: {vector['description']}")
            
            # 复制原始表单数据并注入payload
            test_data = form_data.copy()
            for key in test_data:
                if isinstance(test_data[key], str):
                    test_data[key] = vector["field"]
            
            try:
                response = requests.post(url, data=test_data, timeout=10)
                
                # 检查响应中的可疑模式（MySQL特定）
                suspicious_patterns = [
                    "you have an error in your sql syntax",
                    "warning: mysql",
                    "mysql_fetch_array",
                    "mysql_num_rows",
                    "database error",
                    "query failed"
                ]
                
                for pattern in suspicious_patterns:
                    if pattern.lower() in response.text.lower():
                        self.results.append(f"❌ 发现SQL注入漏洞: {vector['description']}")
                        print(f"  ❌ 检测到数据库错误信息")
                        break
                else:
                    # 检查是否成功绕过认证
                    if "登录成功" in response.text or "welcome" in response.text.lower():
                        self.results.append(f"❌ 认证绕过漏洞: {vector['description']}")
                        print(f"  ❌ 成功绕过认证")
                    else:
                        print(f"  ✅ 未发现明显漏洞")
                        
            except requests.exceptions.Timeout:
                self.results.append(f"⚠️ 可能的时间盲注: {vector['description']}")
                print(f"  ⚠️ 请求超时，可能存在时间盲注")
            except Exception as e:
                print(f"  ⚠️ 请求错误: {e}")

    def test_database_permissions(self):
        """测试数据库用户权限"""
        print("\n正在测试数据库用户权限...")
        
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 检查当前用户权限
            cursor.execute("SELECT CURRENT_USER()")
            current_user = cursor.fetchone()[0]
            print(f"  数据库用户: {current_user}")
            
            # 检查用户权限
            cursor.execute("SHOW GRANTS FOR CURRENT_USER()")
            grants = cursor.fetchall()
            
            dangerous_privileges = ['ALL PRIVILEGES', 'DROP', 'CREATE USER', 'FILE', 'PROCESS', 'SUPER']
            
            for grant in grants:
                grant_statement = grant[0]
                print(f"  权限: {grant_statement}")
                
                for privilege in dangerous_privileges:
                    if privilege in grant_statement.upper():
                        self.results.append(f"❌ 危险权限: {privilege}")
            
            # 测试危险操作权限
            dangerous_operations = [
                ("DROP TABLE IF EXISTS test_security_check", "删除表权限"),
                ("CREATE USER 'attacker'@'localhost'", "创建用户权限"),
                ("SELECT * FROM mysql.user INTO OUTFILE '/tmp/users.csv'", "文件写入权限")
            ]
            
            for operation, description in dangerous_operations:
                try:
                    cursor.execute(operation)
                    self.results.append(f"❌ 危险权限: {description}")
                    conn.rollback()  # 回滚任何更改
                except mysql.connector.Error as e:
                    print(f"  ✅ 无权限: {description} - 错误: {e}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"  数据库连接错误: {e}")

    def test_parameterized_queries(self):
        """测试参数化查询的使用"""
        print("\n正在测试参数化查询安全性...")
        
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 测试安全查询
            test_email = "test@example.com"
            test_password = "password123"
            
            # 安全的方式：参数化查询
            try:
                cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", 
                             (test_email, test_password))
                print("  ✅ 参数化查询工作正常")
            except Exception as e:
                print(f"  ✅ 参数化查询安全（预期错误: {e}）")
            
            # 测试危险的方式：字符串拼接（应该避免）
            dangerous_query = f"SELECT * FROM users WHERE email = '{test_email}'"
            print(f"  ⚠️ 注意：避免使用字符串拼接: {dangerous_query}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"  测试错误: {e}")

    def test_input_validation(self, html_file_path):
        """测试前端输入验证"""
        print("\n正在分析前端输入验证...")
        
        try:
            with open(html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 检查表单输入限制
            forms = soup.find_all('form')
            for i, form in enumerate(forms):
                print(f"  分析表单 #{i+1}")
                
                inputs = form.find_all('input')
                for input_field in inputs:
                    input_type = input_field.get('type', 'text')
                    input_name = input_field.get('name', '无名字段')
                    
                    # 检查输入限制
                    maxlength = input_field.get('maxlength')
                    pattern = input_field.get('pattern')
                    required = input_field.get('required')
                    
                    if maxlength:
                        print(f"    ✅ 字段 '{input_name}' 有长度限制: {maxlength}")
                    else:
                        self.results.append(f"⚠️ 字段 '{input_name}' 无长度限制")
                    
                    if pattern:
                        print(f"    ✅ 字段 '{input_name}' 有输入模式验证")
                    else:
                        print(f"    ⚠️ 字段 '{input_name}' 无输入模式验证")
                        
        except FileNotFoundError:
            print(f"  ⚠️ 无法找到HTML文件: {html_file_path}")
        except Exception as e:
            print(f"  HTML分析错误: {e}")

    def generate_report(self):
        """生成安全测试报告"""
        print("\n" + "="*60)
        print("MySQL 安全测试报告")
        print("="*60)
        
        if not self.results:
            print("✅ 未发现明显安全问题")
        else:
            for result in self.results:
                print(result)
        
        print("="*60)

def main():
    # MySQL 数据库连接配置（使用测试环境！）
    db_config = {
        'host': 'localhost',
        'database': 'security_test',  # 使用测试数据库
        'user': 'test_user',
        'password': 'test123',
        'port': 3306  # MySQL 默认端口
    }
    
    # Web应用测试配置
    test_url = "http://localhost:5000/login"  # 替换为你的应用登录URL
    form_data = {
        'email': 'test@test.com',
        'password': 'test123'
    }
    
    html_file_path = "path/to/your/login.html"  # 替换为你的HTML文件路径
    
    # 创建测试器并运行测试
    tester = MySQLSecurityTester(db_config)
    
    print("开始 MySQL 安全性测试...")
    print("="*60)
    
    # 运行各项测试
    tester.test_sql_injection(test_url, form_data)
    tester.test_database_permissions()
    tester.test_parameterized_queries()
    tester.test_input_validation(html_file_path)
    
    # 生成报告
    tester.generate_report()

if __name__ == "__main__":
    main()