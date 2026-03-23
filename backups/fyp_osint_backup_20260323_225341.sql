-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: fyp_osint
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `breach_results`
--

DROP TABLE IF EXISTS `breach_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `breach_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `investigation_id` int NOT NULL,
  `breach_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `breach_date` date DEFAULT NULL,
  `data_exposed` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_investigation_id` (`investigation_id`),
  KEY `idx_breach_name` (`breach_name`),
  KEY `idx_breach_date` (`breach_date`),
  CONSTRAINT `breach_results_ibfk_1` FOREIGN KEY (`investigation_id`) REFERENCES `investigation_logs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=385 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `breach_results`
--

LOCK TABLES `breach_results` WRITE;
/*!40000 ALTER TABLE `breach_results` DISABLE KEYS */;
INSERT INTO `breach_results` VALUES (369,1,'EduForumDemo','2024-02-11','Email addresses, Passwords'),(370,2,'ShopLink','2023-08-03','Email addresses, Passwords, Full names'),(371,2,'PayTrack','2022-11-19','Financial Information, Phone numbers'),(372,2,'RewardsPortal','2021-01-14','Passwords, Date of birth'),(373,4,'MyJobPortal-MY','2024-05-28','Email addresses, Phone numbers, Address'),(374,5,'LocalTelco-Leaked','2023-04-02','Phone numbers, Address, Date of birth'),(375,6,'E-Wallet-Mega-Breach','2025-01-07','Financial Information, Passwords, Full names, Phone numbers'),(376,7,'LinkedIn-RegionalDump','2021-06-24','Email addresses, Full names, Usernames'),(377,8,'NewsletterHub','2021-11-07','Email addresses, Usernames'),(378,9,'Shoppe-Marketplace','2024-09-16','Email addresses, Phone numbers'),(379,9,'MyJobPortal-MY','2023-12-01','Phone numbers, Address, Date of birth'),(380,10,'LocalTelco-Leaked','2023-10-09','Phone numbers, Address'),(381,10,'E-Wallet-Mega-Breach','2025-01-07','Phone numbers, Financial Information'),(382,11,'Shoppe-Marketplace','2024-09-16','Phone numbers, Email addresses'),(383,11,'MyJobPortal-MY','2023-12-01','Phone numbers, Address, Date of birth'),(384,11,'LocalTelco-Leaked','2023-06-21','Phone numbers, Address');
/*!40000 ALTER TABLE `breach_results` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `investigation_logs`
--

DROP TABLE IF EXISTS `investigation_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `investigation_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone_number` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `breach_count` int NOT NULL,
  `risk_score` int NOT NULL,
  `risk_level` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `checked_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `source_mode` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `checked_by` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `checked_by_email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_checked_at` (`checked_at`),
  KEY `idx_risk_level` (`risk_level`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `investigation_logs`
--

LOCK TABLES `investigation_logs` WRITE;
/*!40000 ALTER TABLE `investigation_logs` DISABLE KEYS */;
INSERT INTO `investigation_logs` VALUES (1,'fildza@ur.unirazak.edu.my',NULL,1,45,'MEDIUM','2026-03-23 18:52:57',NULL,NULL,NULL),(2,'amin.demo@gmail.com',NULL,3,95,'HIGH','2026-03-23 18:52:57',NULL,NULL,NULL),(3,'nur.safe@example.com',NULL,0,10,'LOW','2026-03-23 18:52:57',NULL,NULL,NULL),(4,'amir.jobseek@gmail.com',NULL,1,55,'MEDIUM','2026-03-23 18:52:57',NULL,NULL,NULL),(5,'siti.telco@outlook.com',NULL,1,70,'MEDIUM','2026-03-23 18:52:57',NULL,NULL,NULL),(6,'farid.wallet@yahoo.com',NULL,1,90,'HIGH','2026-03-23 18:52:57',NULL,NULL,NULL),(7,'intan.professional@proton.me',NULL,1,83,'HIGH','2026-03-23 18:52:57',NULL,NULL,NULL),(8,'hafiz.lowrisk@example.com',NULL,1,20,'LOW','2026-03-23 18:52:57',NULL,NULL,NULL),(9,'mfildxza@gmail.com','+601136005936',2,68,'MEDIUM','2026-03-23 18:52:57',NULL,NULL,NULL),(10,NULL,'+60135550011',2,82,'HIGH','2026-03-23 18:52:57',NULL,NULL,NULL),(11,'mfildxza@gmail.com','+601136005936',3,68,'MEDIUM','2026-03-23 18:54:01',NULL,NULL,NULL);
/*!40000 ALTER TABLE `investigation_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `investigation_sessions`
--

DROP TABLE IF EXISTS `investigation_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `investigation_sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `investigation_id` int NOT NULL,
  `operator_id` int DEFAULT NULL,
  `target_bank_account_input` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `normalized_bank_account` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `api_mode` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'auto',
  `effective_data_mode` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Mock',
  `telegram_test_sent` tinyint(1) NOT NULL DEFAULT '0',
  `notes` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_session_investigation_id` (`investigation_id`),
  KEY `idx_session_operator_id` (`operator_id`),
  CONSTRAINT `investigation_sessions_ibfk_1` FOREIGN KEY (`investigation_id`) REFERENCES `investigation_logs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `investigation_sessions_ibfk_2` FOREIGN KEY (`operator_id`) REFERENCES `test_operators` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `investigation_sessions`
--

LOCK TABLES `investigation_sessions` WRITE;
/*!40000 ALTER TABLE `investigation_sessions` DISABLE KEYS */;
/*!40000 ALTER TABLE `investigation_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login_logs`
--

DROP TABLE IF EXISTS `login_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_address` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_agent` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_login_logs_username` (`username`),
  KEY `idx_login_logs_action` (`action`),
  KEY `idx_login_logs_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_logs`
--

LOCK TABLES `login_logs` WRITE;
/*!40000 ALTER TABLE `login_logs` DISABLE KEYS */;
INSERT INTO `login_logs` VALUES (1,'unknown','admin','logout','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-19 21:17:40'),(2,'admin','guest','failed_login','127.0.0.1','Copilot-Login-Test/1.0','2026-03-19 21:18:45'),(3,'admin','admin','login','127.0.0.1','Copilot-Login-Test/1.0','2026-03-19 21:18:45'),(4,'admin','admin','logout','127.0.0.1','Copilot-Login-Test/1.0','2026-03-19 21:18:45'),(5,'unknown','admin','logout','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-19 21:21:09'),(6,'admin','admin','login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-19 21:21:12'),(7,'admin','admin','logout','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-19 21:21:59'),(8,'test','guest','failed_login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-19 21:22:22'),(9,'fildza','guest','failed_login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-19 21:22:46'),(10,'test account','guest','failed_login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-19 21:22:58'),(11,'admin','guest','failed_login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-19 21:23:35'),(12,'admin','guest','failed_login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-19 21:23:47'),(13,'admin','admin','login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-19 21:23:54'),(14,'admin','admin','logout','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-19 21:45:09'),(15,'admin','admin','login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-19 21:45:30'),(16,'anyname','guest','failed_login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-19 21:55:44'),(17,'wrongusername','guest','failed_login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-19 21:55:56'),(18,'admin','admin','logout','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-19 21:56:12'),(19,'Ammara','guest','failed_login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-19 21:56:29'),(20,'Nuha','guest','failed_login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-19 21:56:53'),(21,'admin','admin','login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-20 12:59:43'),(22,'HERMAWAN','guest','failed_login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-23 17:29:49'),(23,'admin','admin','login','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Code/1.112.0 Chrome/142.0.7444.265 Electron/39.8.0 Safari/537.36','2026-03-23 17:30:21');
/*!40000 ALTER TABLE `login_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_operators`
--

DROP TABLE IF EXISTS `test_operators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `test_operators` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `university_email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role_label` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Student Tester',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_operator_student_id` (`student_id`),
  UNIQUE KEY `uq_operator_email` (`university_email`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_operators`
--

LOCK TABLES `test_operators` WRITE;
/*!40000 ALTER TABLE `test_operators` DISABLE KEYS */;
INSERT INTO `test_operators` VALUES (1,'Fildza','FYP2026-001','fildza@student.unirazak.edu.my','FYP Presenter','2026-03-19 11:16:48'),(2,'Amin Demo User','FYP2026-002','amin.demo@unirazak.edu.my','Demo Assistant','2026-03-19 11:16:48');
/*!40000 ALTER TABLE `test_operators` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-23 22:53:41
