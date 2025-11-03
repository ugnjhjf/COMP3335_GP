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
-- Table structure for table `staffs`
--

DROP TABLE IF EXISTS `staffs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staffs` (
  `StfID` int NOT NULL AUTO_INCREMENT,
  `password` varchar(255) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `gender` char(1) NOT NULL,
  `Id_No` varchar(20) NOT NULL,
  `address` text,
  `email` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `department` varchar(50) NOT NULL,
  `role` varchar(50) NOT NULL,
  PRIMARY KEY (`StfID`),
  UNIQUE KEY `Id_No` (`Id_No`)
) ENGINE=InnoDB AUTO_INCREMENT=5011 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staffs`
--

LOCK TABLES `staffs` WRITE;
/*!40000 ALTER TABLE `staffs` DISABLE KEYS */;
INSERT INTO `staffs` VALUES (5001,'hashed_pwd_1','Tang','Bob','F','N589710','Flat C, 18/F, Hopewell Building, Central','bob_tang@school.edu.hk','91651177','Academic Affairs','Accountant'),(5002,'hashed_pwd_2','Chan','Frank','M','G662336','Room 3, 20/F, Landmark Centre, Admiralty','frankchan@school.edu.hk','92351868','Human Resources','Teacher'),(5003,'hashed_pwd_3','Ng','Elizabeth','M','O947272','Flat A, 15/F, Citibank Tower, Central','elizabethng@school.edu.hk','91642635','Academic Affairs','Technical Support'),(5004,'hashed_pwd_4','Chan','Alice','M','N609231','Room 3, 20/F, Landmark Centre, Admiralty','alicechan@school.edu.hk','93586084','Human Resources','Administrator'),(5005,'hashed_pwd_5','Tang','Catherine','F','I922157','Room 3, 20/F, Landmark Centre, Admiralty','catherine.tang@school.edu.hk','94785687','Human Resources','Technical Support'),(5006,'hashed_pwd_6','Lee','Henry','F','G161324','Flat A, 15/F, Citibank Tower, Central','henrylee@school.edu.hk','99096526','Academic Affairs','Counselor'),(5007,'hashed_pwd_7','Wong','Alice','F','Q994141','Flat A, 15/F, Citibank Tower, Central','wong.alice@school.edu.hk','92641282','Academic Affairs','Technical Support'),(5008,'hashed_pwd_8','Lee','Bob','M','V346629','Room 3, 20/F, Landmark Centre, Admiralty','bob.lee@school.edu.hk','92011363','IT Support','Teacher'),(5009,'hashed_pwd_9','Chen','Jack','M','N789305','Flat A, 15/F, Citibank Tower, Central','jack.chen@school.edu.hk','99482934','IT Support','Counselor'),(5010,'hashed_pwd_10','Lau','Elizabeth','M','I515011','Unit 2, 25/F, Exchange Plaza, Admiralty','elizabeth_lau@school.edu.hk','95033115','Human Resources','Counselor');
/*!40000 ALTER TABLE `staffs` ENABLE KEYS */;
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
