USE ComputingU;

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
SET @OLD_TIME_ZONE=@@TIME_ZONE; SET TIME_ZONE='+00:00';
SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0;
SET NAMES utf8mb4;

DROP TABLE IF EXISTS guardians;
CREATE TABLE guardians (
GuaID int NOT NULL AUTO_INCREMENT,
last_name varchar(50) NOT NULL,
first_name varchar(50) NOT NULL,
email varchar(100) NOT NULL,
phone varbinary(64) NOT NULL,
password varchar(255) NOT NULL,
salt varchar(64) NOT NULL,
PRIMARY KEY (GuaID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES guardians WRITE;
INSERT INTO guardians VALUES
(1000,'Chow','David','davidchow@protonmail.com','69364231','a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2','salt_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz'),
(1001,'Ng','David','david1975@outlook.com','62132899','b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3','salt_bcd234efg567hij890klm123nop456qrs789tuv012wxy345zab678cde901fgh'),
(1002,'Wong','Margaret','wong.margaret@hotmail.com','61780798','c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4','salt_cde345fgh678ijk901lmn234opq567rst890uvw123xyz456abc789def012ghi'),
(1003,'Lee','Linda','lindalee@zoho.com','90145908','d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5','salt_def456ghi789jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456jkl'),
(1004,'Lau','William','williamlau@gmail.com','88361172','e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6','salt_efg567hij890klm123nop456qrs789tuv012wxy345zab678cde901fgh234ijk567lmn'),
(1005,'Lau','James','james_lau@yahoo.com','66859215','f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7','salt_fgh678ijk901lmn234opq567rst890uvw123xyz456abc789def012ghi345jkl678mno'),
(1006,'Yeung','David','david_yeung@outlook.com','77751694','g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8','salt_ghi789jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456jkl789mno'),
(1007,'Tang','Margaret','margaret1915@zoho.com','65288191','h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9','salt_hij890klm123nop456qrs789tuv012wxy345zab678cde901fgh234ijk567lmn890opq'),
(1008,'Lau','Linda','lau.linda@yandex.com','72904268','i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0','salt_ijk901lmn234opq567rst890uvw123xyz456abc789def012ghi345jkl678mno901pqr'),
(1009,'Chow','David','david_chow@hotmail.com','65354748','j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1','salt_jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456jkl789mno012pqr345');
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
(2005,'Biology'),
(2006,'History'),
(2007,'Geography'),
(2008,'Computer Science');
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
email varchar(100) NOT NULL,
phone varbinary(64) NOT NULL,
department varchar(50) NOT NULL,
role varchar(50) NOT NULL,
PRIMARY KEY (StfID),
UNIQUE KEY Id_No (Id_No)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES staffs WRITE;
INSERT INTO staffs VALUES
(5001,'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2','salt_staff_5001_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz','Tang','Bob','F','N589710','Flat C, 18/F, Hopewell Building, Central','bob_tang@school.edu.hk','91651177','Academic Affairs','Accountant'),
(5002,'b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3','salt_staff_5002_bcd234efg567hij890klm123nop456qrs789tuv012wxy345zab','Chan','Frank','M','G662336','Room 3, 20/F, Landmark Centre, Admiralty','frankchan@school.edu.hk','92351868','Human Resources','Teacher'),
(5003,'c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4','salt_staff_5003_cde345fgh678ijk901lmn234opq567rst890uvw123xyz456abc','Ng','Elizabeth','M','O947272','Flat A, 15/F, Citibank Tower, Central','elizabethng@school.edu.hk','91642635','Academic Affairs','Technical Support'),
(5004,'d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5','salt_staff_5004_def456ghi789jkl012mno345pqr678stu901vwx234yz567abc','Chan','Alice','M','N609231','Room 3, 20/F, Landmark Centre, Admiralty','alicechan@school.edu.hk','93586084','Human Resources','Administrator'),
(5005,'e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6','salt_staff_5005_efg567hij890klm123nop456qrs789tuv012wxy345zab678cde','Tang','Catherine','F','I922157','Room 3, 20/F, Landmark Centre, Admiralty','catherine.tang@school.edu.hk','94785687','Human Resources','Technical Support'),
(5006,'f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7','salt_staff_5006_fgh678ijk901lmn234opq567rst890uvw123xyz456abc789def','Lee','Henry','F','G161324','Flat A, 15/F, Citibank Tower, Central','henrylee@school.edu.hk','99096526','Academic Affairs','Counselor'),
(5007,'g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8','salt_staff_5007_ghi789jkl012mno345pqr678stu901vwx234yz567abc890def','Wong','Alice','F','Q994141','Flat A, 15/F, Citibank Tower, Central','wong.alice@school.edu.hk','92641282','Academic Affairs','Technical Support'),
(5008,'h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9','salt_staff_5008_hij890klm123nop456qrs789tuv012wxy345zab678cde901fgh','Lee','Bob','M','V346629','Room 3, 20/F, Landmark Centre, Admiralty','bob.lee@school.edu.hk','92011363','IT Support','Teacher'),
(5009,'i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0','salt_staff_5009_ijk901lmn234opq567rst890uvw123xyz456abc789def012ghi','Chen','Jack','M','N789305','Flat A, 15/F, Citibank Tower, Central','jack.chen@school.edu.hk','99482934','IT Support','Counselor'),
(5010,'j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1','salt_staff_5010_jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456','Lau','Elizabeth','M','I515011','Unit 2, 25/F, Exchange Plaza, Admiralty','elizabeth_lau@school.edu.hk','95033115','Human Resources','Counselor');
UNLOCK TABLES;

DROP TABLE IF EXISTS students;
CREATE TABLE students (
StuID int NOT NULL AUTO_INCREMENT,
last_name varchar(50) NOT NULL,
first_name varchar(50) NOT NULL,
gender char(1) NOT NULL,
Id_No varbinary(255) NOT NULL,
address blob,
email varchar(100) NOT NULL,
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
INSERT INTO students VALUES
(100,'Chow','Mia','F','U974628','Apartment 5, 12/F, Central Plaza, Sheung Wan','mia_chow@outlook.com','41831063',2023,1000,'Mother','a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2','salt_stu_100_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz'),
(101,'Ng','Jack','M','R864544','Unit 2, 25/F, Exchange Plaza, Admiralty','jack.ng@protonmail.com','41931511',2024,1001,'Father','b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3','salt_stu_101_bcd234efg567hij890klm123nop456qrs789tuv012wxy345zab'),
(102,'Wong','Noah','M','H961722','Flat C, 18/F, Hopewell Building, Central','noah_wong@zoho.com','62339391',2024,1002,'Mother','c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4','salt_stu_102_cde345fgh678ijk901lmn234opq567rst890uvw123xyz456abc'),
(103,'Wong','Alice','M','U623481','Room 3, 20/F, Landmark Centre, Admiralty','alice_wong@hotmail.com','81586053',2022,1002,'Mother','d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5','salt_stu_103_def456ghi789jkl012mno345pqr678stu901vwx234yz567abc'),
(104,'Lee','Chloe','F','S518801','Apartment 5, 12/F, Central Plaza, Sheung Wan','chloe_lee@zoho.com','49436733',2022,1003,'Grandparent','e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6','salt_stu_104_efg567hij890klm123nop456qrs789tuv012wxy345zab678cde'),
(105,'Lau','Alice','M','V542666','Flat A, 15/F, Citibank Tower, Central','alicelau@gmail.com','28526544',2024,1004,'Father','f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7','salt_stu_105_fgh678ijk901lmn234opq567rst890uvw123xyz456abc789def'),
(106,'Lau','Iris','M','V855731','Flat C, 18/F, Hopewell Building, Central','iris_lau@mail.com','92070937',2023,1004,'Aunt','g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8','salt_stu_106_ghi789jkl012mno345pqr678stu901vwx234yz567abc890def'),
(107,'Lau','Alice','F','A857168','Apartment 5, 12/F, Central Plaza, Sheung Wan','alicelau@protonmail.com','87187530',2022,1005,'Grandparent','h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9','salt_stu_107_hij890klm123nop456qrs789tuv012wxy345zab678cde901fgh'),
(108,'Lau','Noah','M','E492077','Unit 2, 25/F, Exchange Plaza, Admiralty','noah_lau@outlook.com','92394227',2025,1005,'Parent','i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0','salt_stu_108_ijk901lmn234opq567rst890uvw123xyz456abc789def012ghi'),
(109,'Yeung','Grace','F','H160738','Unit 2, 25/F, Exchange Plaza, Admiralty','grace_yeung@gmail.com','96149359',2021,1006,'Parent','j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1','salt_stu_109_jkl012mno345pqr678stu901vwx234yz567abc890def123ghi456'),
(110,'Yeung','Kate','M','E791798','Room 3, 20/F, Landmark Centre, Admiralty','yeung.kate@mail.com','93793389',2022,1006,'Mother','k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2','salt_stu_110_klm123nop456qrs789tuv012wxy345zab678cde901fgh234ijk567lmn890'),
(111,'Tang','Chloe','F','V781446','Apartment 5, 12/F, Central Plaza, Sheung Wan','chloe_tang@zoho.com','78800797',2025,1007,'Father','l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3','salt_stu_111_lmn234opq567rst890uvw123xyz456abc789def012ghi345jkl678mno901'),
(112,'Tang','Alice','F','A716886','Flat A, 15/F, Citibank Tower, Central','alice.tang@hotmail.com','50885476',2025,1007,'Guardian','m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4','salt_stu_112_mno345pqr678stu901vwx234yz567abc890def123ghi456jkl789mno012'),
(113,'Lau','Alice','M','K174299','Flat A, 15/F, Citibank Tower, Central','alice.lau@gmail.com','51944441',2023,1008,'Uncle','n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5','salt_stu_113_nop456qrs789tuv012wxy345zab678cde901fgh234ijk567lmn890opq123'),
(114,'Chow','Chloe','F','H922733','Room 3, 20/F, Landmark Centre, Admiralty','chow.chloe@zoho.com','74634663',2022,1009,'Parent','o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6','salt_stu_114_opq567rst890uvw123xyz456abc789def012ghi345jkl678mno901pqr234');
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
(3005,101,2001,'202526S1','A-','Solid understanding of concepts'),
(3006,101,2005,'202425S1','A-','Solid understanding of concepts'),
(3007,101,2005,'202526S1','F','Needs more practice in problem-solving'),
(3008,102,2006,'202425S2','B-','Some difficulty with advanced topics'),
(3009,102,2005,'202425S1','A-','Demonstrates good grasp of material'),
(3010,102,2005,'202425S1','A','Requires additional tutoring'),
(3011,102,2003,'202526S1','B+','Some difficulty with advanced topics'),
(3012,102,2007,'202425S1','A-','Good work, minor areas for improvement'),
(3013,103,2003,'202425S1','C+','Solid understanding of concepts'),
(3014,103,2007,'202425S2','A','Strong participation in class discussions'),
(3015,103,2006,'202425S1','C+','Needs more practice in problem-solving'),
(3016,103,2004,'202425S1','C+','Demonstrates good grasp of material'),
(3017,103,2003,'202425S2','B+','Solid understanding of concepts'),
(3018,104,2001,'202425S2','C+','Demonstrates good grasp of material'),
(3019,104,2004,'202526S1','B+','Good work, minor areas for improvement'),
(3020,104,2007,'202425S1','C-','Needs more practice in problem-solving'),
(3021,104,2004,'202526S2','C+','Strong participation in class discussions'),
(3022,105,2004,'202425S1','B','Demonstrates good grasp of material'),
(3023,105,2006,'202526S1','A-','Strong participation in class discussions'),
(3024,105,2006,'202526S2','D','Requires additional tutoring'),
(3025,106,2002,'202526S1','B+','Strong participation in class discussions'),
(3026,106,2001,'202425S1','F','Demonstrates good grasp of material'),
(3027,106,2006,'202526S1','C','Good work, minor areas for improvement'),
(3028,107,2004,'202526S1','A','Demonstrates good grasp of material'),
(3029,107,2001,'202425S2','C+','Demonstrates good grasp of material'),
(3030,107,2002,'202526S1','F','Requires additional tutoring'),
(3031,107,2002,'202526S1','D','Strong participation in class discussions'),
(3032,108,2007,'202526S1','C','Strong participation in class discussions'),
(3033,108,2003,'202425S2','C','Demonstrates good grasp of material'),
(3034,108,2003,'202526S1','C','Excellent performance, consistent effort'),
(3035,108,2005,'202526S1','B','Demonstrates good grasp of material'),
(3036,108,2006,'202526S2','C-','Some difficulty with advanced topics'),
(3037,109,2004,'202526S2','B+','Good work, minor areas for improvement'),
(3038,109,2005,'202526S1','A-','Needs more practice in problem-solving'),
(3039,109,2005,'202425S2','B','Solid understanding of concepts'),
(3040,109,2001,'202425S1','B','Some difficulty with advanced topics'),
(3041,109,2002,'202526S2','C','Needs more practice in problem-solving');
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
(4001,100,'2025-06-26',5007,'Incomplete homework submission'),
(4002,100,'2025-09-23',5001,'Assignment not submitted on time'),
(4003,101,'2025-09-15',5009,'Failure to bring required materials'),
(4004,104,'2025-09-26',5008,'Use of mobile phone during class'),
(4005,104,'2025-06-09',5010,'Violation of school uniform policy'),
(4006,105,'2025-05-27',5009,'Late arrival to school - 3 instances'),
(4007,105,'2025-06-12',5008,'Minor classroom disruption'),
(4008,106,'2025-07-07',5005,'Incomplete homework submission'),
(4009,106,'2025-05-20',5005,'Use of mobile phone during class'),
(4010,110,'2025-08-22',5006,'Violation of school uniform policy'),
(4011,111,'2025-09-25',5003,'Incomplete homework submission');
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

SET TIME_ZONE=@OLD_TIME_ZONE;
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
SET SQL_NOTES=@OLD_SQL_NOTES;