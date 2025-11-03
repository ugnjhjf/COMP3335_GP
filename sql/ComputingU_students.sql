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
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `StuID` int NOT NULL AUTO_INCREMENT,
  `last_name` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `gender` char(1) NOT NULL,
  `Id_No` varchar(20) NOT NULL,
  `address` text,
  `email` varchar(100) NOT NULL,
  `phone` char(8) NOT NULL,
  `enrollment_year` year NOT NULL,
  `GuaID` int DEFAULT NULL,
  `guardian_relation` varchar(50) NOT NULL,
  PRIMARY KEY (`StuID`),
  UNIQUE KEY `Id_No` (`Id_No`),
  KEY `GuaID` (`GuaID`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`GuaID`) REFERENCES `guardians` (`GuaID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (100,'Chow','Mia','F','U974628','Apartment 5, 12/F, Central Plaza, Sheung Wan','mia_chow@outlook.com','41831063',2023,1000,'Mother'),(101,'Ng','Jack','M','R864544','Unit 2, 25/F, Exchange Plaza, Admiralty','jack.ng@protonmail.com','41931511',2024,1001,'Father'),(102,'Wong','Noah','M','H961722','Flat C, 18/F, Hopewell Building, Central','noah_wong@zoho.com','62339391',2024,1002,'Mother'),(103,'Wong','Alice','M','U623481','Room 3, 20/F, Landmark Centre, Admiralty','alice_wong@hotmail.com','81586053',2022,1002,'Mother'),(104,'Lee','Chloe','F','S518801','Apartment 5, 12/F, Central Plaza, Sheung Wan','chloe_lee@zoho.com','49436733',2022,1003,'Grandparent'),(105,'Lau','Alice','M','V542666','Flat A, 15/F, Citibank Tower, Central','alicelau@gmail.com','28526544',2024,1004,'Father'),(106,'Lau','Iris','M','V855731','Flat C, 18/F, Hopewell Building, Central','iris_lau@mail.com','92070937',2023,1004,'Aunt'),(107,'Lau','Alice','F','A857168','Apartment 5, 12/F, Central Plaza, Sheung Wan','alicelau@protonmail.com','87187530',2022,1005,'Grandparent'),(108,'Lau','Noah','M','E492077','Unit 2, 25/F, Exchange Plaza, Admiralty','noah_lau@outlook.com','92394227',2025,1005,'Parent'),(109,'Yeung','Grace','F','H160738','Unit 2, 25/F, Exchange Plaza, Admiralty','grace_yeung@gmail.com','96149359',2021,1006,'Parent'),(110,'Yeung','Kate','M','E791798','Room 3, 20/F, Landmark Centre, Admiralty','yeung.kate@mail.com','93793389',2022,1006,'Mother'),(111,'Tang','Chloe','F','V781446','Apartment 5, 12/F, Central Plaza, Sheung Wan','chloe_tang@zoho.com','78800797',2025,1007,'Father'),(112,'Tang','Alice','F','A716886','Flat A, 15/F, Citibank Tower, Central','alice.tang@hotmail.com','50885476',2025,1007,'Guardian'),(113,'Lau','Alice','M','K174299','Flat A, 15/F, Citibank Tower, Central','alice.lau@gmail.com','51944441',2023,1008,'Uncle'),(114,'Chow','Chloe','F','H922733','Room 3, 20/F, Landmark Centre, Admiralty','chow.chloe@zoho.com','74634663',2022,1009,'Parent');
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
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
