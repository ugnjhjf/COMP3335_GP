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
-- Table structure for table `grades`
--

DROP TABLE IF EXISTS `grades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grades` (
  `GradeID` int NOT NULL AUTO_INCREMENT,
  `StuID` int NOT NULL,
  `CID` int NOT NULL,
  `term` varchar(10) NOT NULL,
  `grade` varchar(5) NOT NULL,
  `comments` text,
  PRIMARY KEY (`GradeID`),
  KEY `StuID` (`StuID`),
  KEY `CID` (`CID`),
  CONSTRAINT `grades_ibfk_1` FOREIGN KEY (`StuID`) REFERENCES `students` (`StuID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `grades_ibfk_2` FOREIGN KEY (`CID`) REFERENCES `courses` (`CID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3042 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grades`
--

LOCK TABLES `grades` WRITE;
/*!40000 ALTER TABLE `grades` DISABLE KEYS */;
INSERT INTO `grades` VALUES (3001,100,2001,'202526S2','F','Good work, minor areas for improvement'),(3002,100,2002,'202425S2','D','Strong participation in class discussions'),(3003,100,2003,'202526S1','A-','Needs more practice in problem-solving'),(3004,101,2005,'202425S2','C-','Strong participation in class discussions'),(3005,101,2001,'202526S1','A-','Solid understanding of concepts'),(3006,101,2005,'202425S1','A-','Solid understanding of concepts'),(3007,101,2005,'202526S1','F','Needs more practice in problem-solving'),(3008,102,2006,'202425S2','B-','Some difficulty with advanced topics'),(3009,102,2005,'202425S1','A-','Demonstrates good grasp of material'),(3010,102,2005,'202425S1','A','Requires additional tutoring'),(3011,102,2003,'202526S1','B+','Some difficulty with advanced topics'),(3012,102,2007,'202425S1','A-','Good work, minor areas for improvement'),(3013,103,2003,'202425S1','C+','Solid understanding of concepts'),(3014,103,2007,'202425S2','A','Strong participation in class discussions'),(3015,103,2006,'202425S1','C+','Needs more practice in problem-solving'),(3016,103,2004,'202425S1','C+','Demonstrates good grasp of material'),(3017,103,2003,'202425S2','B+','Solid understanding of concepts'),(3018,104,2001,'202425S2','C+','Demonstrates good grasp of material'),(3019,104,2004,'202526S1','B+','Good work, minor areas for improvement'),(3020,104,2007,'202425S1','C-','Needs more practice in problem-solving'),(3021,104,2004,'202526S2','C+','Strong participation in class discussions'),(3022,105,2004,'202425S1','B','Demonstrates good grasp of material'),(3023,105,2006,'202526S1','A-','Strong participation in class discussions'),(3024,105,2006,'202526S2','D','Requires additional tutoring'),(3025,106,2002,'202526S1','B+','Strong participation in class discussions'),(3026,106,2001,'202425S1','F','Demonstrates good grasp of material'),(3027,106,2006,'202526S1','C','Good work, minor areas for improvement'),(3028,107,2004,'202526S1','A','Demonstrates good grasp of material'),(3029,107,2001,'202425S2','C+','Demonstrates good grasp of material'),(3030,107,2002,'202526S1','F','Requires additional tutoring'),(3031,107,2002,'202526S1','D','Strong participation in class discussions'),(3032,108,2007,'202526S1','C','Strong participation in class discussions'),(3033,108,2003,'202425S2','C','Demonstrates good grasp of material'),(3034,108,2003,'202526S1','C','Excellent performance, consistent effort'),(3035,108,2005,'202526S1','B','Demonstrates good grasp of material'),(3036,108,2006,'202526S2','C-','Some difficulty with advanced topics'),(3037,109,2004,'202526S2','B+','Good work, minor areas for improvement'),(3038,109,2005,'202526S1','A-','Needs more practice in problem-solving'),(3039,109,2005,'202425S2','B','Solid understanding of concepts'),(3040,109,2001,'202425S1','B','Some difficulty with advanced topics'),(3041,109,2002,'202526S2','C','Needs more practice in problem-solving');
/*!40000 ALTER TABLE `grades` ENABLE KEYS */;
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
