DROP DATABASE IF EXISTS ComputingU;
CREATE DATABASE ComputingU;
USE ComputingU;

DROP USER IF EXISTS 'auth_user'@'localhost';
DROP USER IF EXISTS 'auth_user'@'%';
DROP USER IF EXISTS 'student'@'localhost';
DROP USER IF EXISTS 'student'@'%';
DROP USER IF EXISTS 'guardian'@'localhost';
DROP USER IF EXISTS 'guardian'@'%';
DROP USER IF EXISTS 'aro'@'localhost';
DROP USER IF EXISTS 'aro'@'%';
DROP USER IF EXISTS 'dro'@'localhost';
DROP USER IF EXISTS 'dro'@'%';

CREATE USER 'auth_user'@'localhost' IDENTIFIED BY 'auth_user_password';
CREATE USER 'auth_user'@'%' IDENTIFIED BY 'auth_user_password';
CREATE USER 'student'@'localhost' IDENTIFIED BY 'student_password';
CREATE USER 'student'@'%' IDENTIFIED BY 'student_password';
CREATE USER 'guardian'@'localhost' IDENTIFIED BY 'guardian_password';
CREATE USER 'guardian'@'%' IDENTIFIED BY 'guardian_password';
CREATE USER 'aro'@'localhost' IDENTIFIED BY 'aro_password';
CREATE USER 'aro'@'%' IDENTIFIED BY 'aro_password';
CREATE USER 'dro'@'localhost' IDENTIFIED BY 'dro_password';
CREATE USER 'dro'@'%' IDENTIFIED BY 'dro_password';


SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
SET @OLD_TIME_ZONE=@@TIME_ZONE; SET TIME_ZONE='+00:00';
SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0;
SET NAMES utf8mb4;


SET @encryption_key = 'c29a02b23662ced73f8c007c877a85c8aab576b1b7f888ac37c364b5a75a681b';

DROP TABLE IF EXISTS guardians;
CREATE TABLE guardians (
GuaID int NOT NULL AUTO_INCREMENT,
last_name varchar(50) NOT NULL,
first_name varchar(50) NOT NULL,
email varchar(100) NOT NULL UNIQUE,
phone varbinary(64) NOT NULL,
password varchar(255) NOT NULL,
salt varchar(64) NOT NULL,
PRIMARY KEY (GuaID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES guardians WRITE;
INSERT INTO guardians (GuaID, last_name, first_name, email, phone, password, salt) VALUES
(1000,'Chow','David','test_guardian@example.com',AES_ENCRYPT('69364231', @encryption_key),'c3682fb45354d4c4586fb632f5a0ab7923224873e110007437b324ed05482650','test_salt_guardian_1234567890123456789012'),
(1001,'Ng','David','david1975@outlook.com',AES_ENCRYPT('62132899', @encryption_key),'b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3','salt_bcd234efg567hij890klm123nop456qrs789tuv012wxy345zab678cde901fgh'),
(1002,'Wong','Margaret','wong.margaret@hotmail.com',AES_ENCRYPT('61780798', @encryption_key),'c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4','salt_cde345fgh678ijk901lmn234opq567rst890uvw123xyz456abc789def012ghi'),
(1003,'Lee','Linda','lindalee@zoho.com',AES_ENCRYPT('90145908', @encryption_key),'d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5','salt_def456ghi789jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456jkl'),
(1004,'Lau','William','williamlau@gmail.com',AES_ENCRYPT('88361172', @encryption_key),'e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6','salt_efg567hij890klm123nop456qrs789tuv012wxy345zab678cde901fgh234ijk567lmn');
UNLOCK TABLES;

DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
CID int NOT NULL AUTO_INCREMENT,
course_name varchar(100) NOT NULL,
PRIMARY KEY (CID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES courses WRITE;
INSERT INTO courses VALUES
(2001,'Mathematics'),
(2002,'English'),
(2003,'Physics'),
(2004,'Chemistry'),
(2005,'Biology');
UNLOCK TABLES;

DROP TABLE IF EXISTS staffs;
CREATE TABLE staffs (
StfID int NOT NULL AUTO_INCREMENT,
password varchar(255) NOT NULL,
salt varchar(64) NOT NULL,
last_name varchar(50) NOT NULL,
first_name varchar(50) NOT NULL,
gender char(1) NOT NULL,
Id_No varbinary(255) NOT NULL,
address blob,
email varchar(100) NOT NULL UNIQUE,
phone varbinary(64) NOT NULL,
department varchar(50) NOT NULL,
role varchar(50) NOT NULL,
PRIMARY KEY (StfID),
UNIQUE KEY Id_No (Id_No)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES staffs WRITE;
INSERT INTO staffs (StfID, password, salt, last_name, first_name, gender, Id_No, address, email, phone, department, role) VALUES
(5001,'ffd184f832c88502a23b06482a20b925f5769ab08b175be775733f1b5f09dbaa','test_salt_staff_12345678901234567890123456','Tang','Bob','F',AES_ENCRYPT('N589710', @encryption_key),AES_ENCRYPT('Flat C, 18/F, Hopewell Building, Central', @encryption_key),'test_staff@example.com',AES_ENCRYPT('91651177', @encryption_key),'Academic Affairs','Accountant'),
(5002,'b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3','salt_staff_5002_bcd234efg567hij890klm123nop456qrs789tuv012wxy345zab','Chan','Frank','M',AES_ENCRYPT('G662336', @encryption_key),AES_ENCRYPT('Room 3, 20/F, Landmark Centre, Admiralty', @encryption_key),'frankchan@school.edu.hk',AES_ENCRYPT('92351868', @encryption_key),'Human Resources','Teacher'),
(5003,'c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4','salt_staff_5003_cde345fgh678ijk901lmn234opq567rst890uvw123xyz456abc','Ng','Elizabeth','M',AES_ENCRYPT('O947272', @encryption_key),AES_ENCRYPT('Flat A, 15/F, Citibank Tower, Central', @encryption_key),'elizabethng@school.edu.hk',AES_ENCRYPT('91642635', @encryption_key),'Academic Affairs','Technical Support'),
(5004,'d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5','salt_staff_5004_def456ghi789jkl012mno345pqr678stu901vwx234yz567abc','Chan','Alice','M',AES_ENCRYPT('N609231', @encryption_key),AES_ENCRYPT('Room 3, 20/F, Landmark Centre, Admiralty', @encryption_key),'alicechan@school.edu.hk',AES_ENCRYPT('93586084', @encryption_key),'Human Resources','Administrator'),
(5005,'e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6','salt_staff_5005_efg567hij890klm123nop456qrs789tuv012wxy345zab678cde','Tang','Catherine','F',AES_ENCRYPT('I922157', @encryption_key),AES_ENCRYPT('Room 3, 20/F, Landmark Centre, Admiralty', @encryption_key),'catherine.tang@school.edu.hk',AES_ENCRYPT('94785687', @encryption_key),'Human Resources','Technical Support');
UNLOCK TABLES;

DROP TABLE IF EXISTS students;
CREATE TABLE students (
StuID int NOT NULL AUTO_INCREMENT,
last_name varchar(50) NOT NULL,
first_name varchar(50) NOT NULL,
gender char(1) NOT NULL,
Id_No varbinary(255) NOT NULL,
address blob,
email varchar(100) NOT NULL UNIQUE,
phone varbinary(64) NOT NULL,
enrollment_year year NOT NULL,
GuaID int DEFAULT NULL,
guardian_relation varchar(50) NOT NULL,
password varchar(255) NOT NULL,
salt varchar(64) NOT NULL,
PRIMARY KEY (StuID),
UNIQUE KEY Id_No (Id_No),
KEY GuaID (GuaID),
CONSTRAINT students_ibfk_1 FOREIGN KEY (GuaID) REFERENCES guardians (GuaID) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES students WRITE;
INSERT INTO students (StuID, last_name, first_name, gender, Id_No, address, email, phone, enrollment_year, GuaID, guardian_relation, password, salt) VALUES
(100,'Chow','Mia','F',AES_ENCRYPT('U974628', @encryption_key),AES_ENCRYPT('Apartment 5, 12/F, Central Plaza, Sheung Wan', @encryption_key),'test_student@example.com',AES_ENCRYPT('41831063', @encryption_key),2023,1000,'Mother','f1c26a2dbc7d9f6d932c6199f1501f61c92a59b214545eca3b5cc1bc86bcf2a1','test_salt_student_123456789012345678901234'),
(101,'Ng','Jack','M',AES_ENCRYPT('R864544', @encryption_key),AES_ENCRYPT('Unit 2, 25/F, Exchange Plaza, Admiralty', @encryption_key),'jack.ng@protonmail.com',AES_ENCRYPT('41931511', @encryption_key),2024,1001,'Father','b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3','salt_stu_101_bcd234efg567hij890klm123nop456qrs789tuv012wxy345zab'),
(102,'Wong','Noah','M',AES_ENCRYPT('H961722', @encryption_key),AES_ENCRYPT('Flat C, 18/F, Hopewell Building, Central', @encryption_key),'noah_wong@zoho.com',AES_ENCRYPT('62339391', @encryption_key),2024,1002,'Mother','c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4','salt_stu_102_cde345fgh678ijk901lmn234opq567rst890uvw123xyz456abc'),
(103,'Wong','Alice','M',AES_ENCRYPT('U623481', @encryption_key),AES_ENCRYPT('Room 3, 20/F, Landmark Centre, Admiralty', @encryption_key),'alice_wong@hotmail.com',AES_ENCRYPT('81586053', @encryption_key),2022,1002,'Mother','d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5','salt_stu_103_def456ghi789jkl012mno345pqr678stu901vwx234yz567abc'),
(104,'Lee','Chloe','F',AES_ENCRYPT('S518801', @encryption_key),AES_ENCRYPT('Apartment 5, 12/F, Central Plaza, Sheung Wan', @encryption_key),'chloe_lee@zoho.com',AES_ENCRYPT('49436733', @encryption_key),2022,1003,'Grandparent','e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6','salt_stu_104_efg567hij890klm123nop456qrs789tuv012wxy345zab678cde');
UNLOCK TABLES;

DROP TABLE IF EXISTS grades;
CREATE TABLE grades (
GradeID int NOT NULL AUTO_INCREMENT,
StuID int NOT NULL,
CID int NOT NULL,
term varchar(10) NOT NULL,
grade varchar(5) NOT NULL,
comments text,
PRIMARY KEY (GradeID),
KEY StuID (StuID),
KEY CID (CID),
CONSTRAINT grades_ibfk_1 FOREIGN KEY (StuID) REFERENCES students (StuID) ON DELETE RESTRICT ON UPDATE CASCADE,
CONSTRAINT grades_ibfk_2 FOREIGN KEY (CID) REFERENCES courses (CID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES grades WRITE;
INSERT INTO grades VALUES
(3001,100,2001,'202526S2','F','Good work, minor areas for improvement'),
(3002,100,2002,'202425S2','D','Strong participation in class discussions'),
(3003,100,2003,'202526S1','A-','Needs more practice in problem-solving'),
(3004,101,2005,'202425S2','C-','Strong participation in class discussions'),
(3005,101,2001,'202526S1','A-','Solid understanding of concepts');
UNLOCK TABLES;

DROP TABLE IF EXISTS disciplinary_records;
CREATE TABLE disciplinary_records (
DrID int NOT NULL AUTO_INCREMENT,
StuID int NOT NULL,
date date NOT NULL,
StfID int NOT NULL,
descriptions text,
PRIMARY KEY (DrID),
KEY StuID (StuID),
KEY StfID (StfID),
CONSTRAINT disciplinary_records_ibfk_1 FOREIGN KEY (StuID) REFERENCES students (StuID) ON DELETE RESTRICT ON UPDATE CASCADE,
CONSTRAINT disciplinary_records_ibfk_2 FOREIGN KEY (StfID) REFERENCES staffs (StfID) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES disciplinary_records WRITE;
INSERT INTO disciplinary_records VALUES
(4001,100,'2025-06-26',5002,'Incomplete homework submission'),
(4002,100,'2025-09-23',5001,'Assignment not submitted on time'),
(4003,101,'2025-09-15',5003,'Failure to bring required materials'),
(4004,104,'2025-09-26',5004,'Use of mobile phone during class'),
(4005,104,'2025-06-09',5005,'Violation of school uniform policy');
UNLOCK TABLES;


DROP TABLE IF EXISTS dataUpdateLog;
CREATE TABLE dataUpdateLog (
  LogID       BIGINT NOT NULL AUTO_INCREMENT,
  logged_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  user_id     VARCHAR(64) NOT NULL,
  user_role        VARCHAR(64) NOT NULL,
  sql_text    TEXT NOT NULL,
  PRIMARY KEY (LogID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS accountLog;
CREATE TABLE accountLog (
  logID       INT NOT NULL AUTO_INCREMENT,
  timestamp   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ip          VARCHAR(45) NOT NULL,
  user_id     VARCHAR(64),
  user_role   VARCHAR(64),
  logContent  TEXT NOT NULL,
  PRIMARY KEY (logID),
  INDEX idx_timestamp (timestamp),
  INDEX idx_user_id (user_id),
  INDEX idx_user_role (user_role),
  INDEX idx_ip (ip)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS audit_log;
CREATE TABLE audit_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  event_type VARCHAR(100) NOT NULL,
  user_id VARCHAR(50),
  user_role VARCHAR(50),
  ip_address VARCHAR(45),
  sql_statement TEXT,
  details TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_event_type (event_type),
  INDEX idx_user_id (user_id),
  INDEX idx_user_role (user_role),
  INDEX idx_timestamp (timestamp),
  INDEX idx_ip_address (ip_address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
  token VARCHAR(255) PRIMARY KEY,
  user_id VARCHAR(50) NOT NULL,
  role VARCHAR(50) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_expires_at (expires_at),
  INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

GRANT SELECT, UPDATE (StuID, email, password, salt, first_name, last_name) ON ComputingU.students TO 'auth_user'@'localhost', 'auth_user'@'%';
GRANT SELECT, UPDATE (GuaID, email, password, salt, first_name, last_name) ON ComputingU.guardians TO 'auth_user'@'localhost', 'auth_user'@'%';
GRANT SELECT, UPDATE (StfID, email, password, salt, role, department, first_name, last_name) ON ComputingU.staffs TO 'auth_user'@'localhost', 'auth_user'@'%';
 
GRANT INSERT ON ComputingU.audit_log TO 'auth_user'@'localhost', 'auth_user'@'%';
GRANT INSERT ON ComputingU.accountLog TO 'auth_user'@'localhost', 'auth_user'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON ComputingU.sessions TO 'auth_user'@'localhost', 'auth_user'@'%';

GRANT SELECT ON ComputingU.students TO 'student'@'localhost', 'student'@'%';
GRANT UPDATE (last_name, first_name, gender, Id_No, address, phone, email, guardian_relation) ON ComputingU.students TO 'student'@'localhost', 'student'@'%';
GRANT SELECT ON ComputingU.grades TO 'student'@'localhost', 'student'@'%';
GRANT SELECT ON ComputingU.disciplinary_records TO 'student'@'localhost', 'student'@'%';
GRANT SELECT ON ComputingU.courses TO 'student'@'localhost', 'student'@'%';
GRANT SELECT (StfID, first_name, last_name) ON ComputingU.staffs TO 'student'@'localhost', 'student'@'%';

GRANT SELECT ON ComputingU.guardians TO 'guardian'@'localhost', 'guardian'@'%';
GRANT UPDATE (last_name, first_name, email, phone) ON ComputingU.guardians TO 'guardian'@'localhost', 'guardian'@'%';
GRANT SELECT ON ComputingU.grades TO 'guardian'@'localhost', 'guardian'@'%';
GRANT SELECT ON ComputingU.disciplinary_records TO 'guardian'@'localhost', 'guardian'@'%';
GRANT SELECT ON ComputingU.courses TO 'guardian'@'localhost', 'guardian'@'%';
GRANT SELECT (StfID, first_name, last_name) ON ComputingU.staffs TO 'guardian'@'localhost', 'guardian'@'%';

GRANT SELECT, INSERT, UPDATE, DELETE ON ComputingU.grades TO 'aro'@'localhost', 'aro'@'%';
GRANT SELECT ON ComputingU.students TO 'aro'@'localhost', 'aro'@'%';
GRANT SELECT ON ComputingU.courses TO 'aro'@'localhost', 'aro'@'%';

GRANT SELECT, INSERT, UPDATE, DELETE ON ComputingU.disciplinary_records TO 'dro'@'localhost', 'dro'@'%';
GRANT SELECT ON ComputingU.students TO 'dro'@'localhost', 'dro'@'%';
GRANT SELECT ON ComputingU.staffs TO 'dro'@'localhost', 'dro'@'%';

GRANT INSERT ON ComputingU.audit_log TO 'student'@'localhost', 'student'@'%', 'guardian'@'localhost', 'guardian'@'%', 'aro'@'localhost', 'aro'@'%', 'dro'@'localhost', 'dro'@'%';
GRANT INSERT ON ComputingU.dataUpdateLog TO 'student'@'localhost', 'student'@'%', 'guardian'@'localhost', 'guardian'@'%', 'aro'@'localhost', 'aro'@'%', 'dro'@'localhost', 'dro'@'%';
GRANT INSERT ON ComputingU.accountLog TO 'student'@'localhost', 'student'@'%', 'guardian'@'localhost', 'guardian'@'%', 'aro'@'localhost', 'aro'@'%', 'dro'@'localhost', 'dro'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON ComputingU.sessions TO 'student'@'localhost', 'student'@'%', 'guardian'@'localhost', 'guardian'@'%', 'aro'@'localhost', 'aro'@'%', 'dro'@'localhost', 'dro'@'%';

FLUSH PRIVILEGES;

SET TIME_ZONE=@OLD_TIME_ZONE;
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
SET SQL_NOTES=@OLD_SQL_NOTES;