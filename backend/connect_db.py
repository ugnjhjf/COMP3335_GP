import pymysql
import sys

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',      # Database host address
    'port': 3306,             # Database port
    'user': 'root',           # Database username 
    'password': 'supersecurepassword',            # Database password 
    'database': 'university',  # Database name
    'charset': 'utf8mb4'      # Character set
}


def connect_to_database():
    try:
        # Establish database connection
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor  # Return results as dictionary
        )
        
        print("✓ Successfully connected to MySQL database!")
        print(f"  Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"  Database: {DB_CONFIG['database']}")
        
        return connection
        
    except pymysql.Error as e:
        print(f"✗ Database connection failed: {e}")
        return None
    except Exception as e:
        print(f"✗ Unknown error occurred: {e}")
        return None


def query_courses(connection):
    """
    Query all courses from the courses table

    """
    try:
        with connection.cursor() as cursor:
            # Execute SQL query
            sql = "SELECT CID, course_name FROM courses"
            cursor.execute(sql)
            
            # Fetch all results
            results = cursor.fetchall()
            
            print("\nCourse List:")
            print("-" * 40)
            for row in results:
                print(f"Course ID: {row['CID']}, Course Name: {row['course_name']}")
            print("-" * 40)
            print(f"Total {len(results)} courses")
            
    except pymysql.Error as e:
        print(f"Query failed: {e}")


def main():
    """
    Main function
    """
    # Connect to database
    connection = connect_to_database()
    
    if connection is None:
        print("\nPlease check:")
        print("1. MySQL service is running")
        print("2. Database configuration is correct (username, password, etc.)")
        print("3. Database is created")
        sys.exit(1)
    
    try:
        # Execute sample query
        query_courses(connection)
        
    finally:
        # Close database connection
        connection.close()
        print("\n✓ Database connection closed")


if __name__ == "__main__":
    main()

