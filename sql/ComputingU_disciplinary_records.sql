-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: ComputingU
-- ------------------------------------------------------
-- Server version	8.0.43-34

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `disciplinary_records`
--

DROP TABLE IF EXISTS `disciplinary_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `disciplinary_records` (
  `DrID` int NOT NULL AUTO_INCREMENT,
  `StuID` int NOT NULL,
  `date` date NOT NULL,
  `StfID` int NOT NULL,
  `descriptions` text,
  PRIMARY KEY (`DrID`),
  KEY `StuID` (`StuID`),
  KEY `StfID` (`StfID`),
  CONSTRAINT `disciplinary_records_ibfk_1` FOREIGN KEY (`StuID`) REFERENCES `students` (`StuID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `disciplinary_records_ibfk_2` FOREIGN KEY (`StfID`) REFERENCES `staffs` (`StfID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4012 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disciplinary_records`
--

LOCK TABLES `disciplinary_records` WRITE;
/*!40000 ALTER TABLE `disciplinary_records` DISABLE KEYS */;
INSERT INTO `disciplinary_records` VALUES (4001,100,'2025-06-26',5007,'Incomplete homework submission'),(4002,100,'2025-09-23',5001,'Assignment not submitted on time'),(4003,101,'2025-09-15',5009,'Failure to bring required materials'),(4004,104,'2025-09-26',5008,'Use of mobile phone during class'),(4005,104,'2025-06-09',5010,'Violation of school uniform policy'),(4006,105,'2025-05-27',5009,'Late arrival to school - 3 instances'),(4007,105,'2025-06-12',5008,'Minor classroom disruption'),(4008,106,'2025-07-07',5005,'Incomplete homework submission'),(4009,106,'2025-05-20',5005,'Use of mobile phone during class'),(4010,110,'2025-08-22',5006,'Violation of school uniform policy'),(4011,111,'2025-09-25',5003,'Incomplete homework submission');
/*!40000 ALTER TABLE `disciplinary_records` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-01 13:05:39
