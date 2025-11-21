-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: croprec_db
-- ------------------------------------------------------
-- Server version	8.0.42

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
-- Current Database: `croprec_db`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `croprec_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `croprec_db`;

--
-- Table structure for table `crop_predictions`
--

DROP TABLE IF EXISTS `crop_predictions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `crop_predictions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nitrogen` float NOT NULL,
  `phosphorous` float NOT NULL,
  `potassium` float NOT NULL,
  `temperature` float NOT NULL,
  `rainfall` float NOT NULL,
  `humidity` float NOT NULL,
  `prediction` json NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crop_predictions`
--

LOCK TABLES `crop_predictions` WRITE;
/*!40000 ALTER TABLE `crop_predictions` DISABLE KEYS */;
INSERT INTO `crop_predictions` VALUES (1,180,48,31,24,439,64,'{\"dt\": \"rice\", \"ev\": \"rice\", \"rf\": \"rice\", \"gbm\": \"rice\"}','2025-10-31 22:56:03');
/*!40000 ALTER TABLE `crop_predictions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `crops`
--

DROP TABLE IF EXISTS `crops`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `crops` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `nitrogen` decimal(10,2) NOT NULL,
  `phosphorous` decimal(10,2) NOT NULL,
  `potassium` decimal(10,2) NOT NULL,
  `rainfall` decimal(10,2) NOT NULL,
  `temperature` decimal(10,2) NOT NULL,
  `humidity` decimal(10,2) NOT NULL,
  `prediction` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `crops_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crops`
--

LOCK TABLES `crops` WRITE;
/*!40000 ALTER TABLE `crops` DISABLE KEYS */;
INSERT INTO `crops` VALUES (1,4,25.00,40.00,20.00,100.00,30.00,50.00,'common beans','2025-08-01 17:00:00','2025-08-01 17:00:00'),(2,4,25.00,40.00,20.00,100.00,30.00,50.00,'common beans','2025-08-01 17:22:22','2025-08-01 17:22:22'),(3,4,125.00,140.00,120.00,100.00,30.00,50.00,'wheat','2025-08-01 17:31:18','2025-08-01 17:31:18'),(4,4,300.00,140.00,120.00,100.00,30.00,50.00,'wheat','2025-08-02 14:01:32','2025-08-02 14:01:32'),(5,4,300.00,140.00,120.00,100.00,30.00,50.00,'wheat','2025-08-02 14:22:11','2025-08-02 14:22:11'),(6,4,300.00,140.00,120.00,100.00,30.00,50.00,'wheat','2025-08-22 13:49:38','2025-08-22 13:49:38'),(9,6,45.00,55.00,60.00,120.00,30.00,75.00,'potato','2025-10-28 11:00:11','2025-10-28 11:00:11'),(10,6,45.00,55.00,60.00,120.00,30.00,75.00,'potato','2025-10-30 03:46:32','2025-10-30 03:46:32'),(11,6,45.00,55.00,60.00,120.00,30.00,75.00,'potato','2025-10-30 04:04:55','2025-10-30 04:04:55'),(12,6,45.00,55.00,60.00,12.00,30.00,75.00,'potato','2025-10-30 04:05:01','2025-10-30 04:05:01'),(13,6,45.00,55.00,60.00,120.00,30.00,75.00,'potato','2025-10-30 04:05:10','2025-10-30 04:05:10'),(14,6,45.00,55.00,60.00,120.00,30.00,75.00,'potato','2025-10-30 04:05:11','2025-10-30 04:05:11'),(15,6,45.00,55.00,60.00,120.00,30.00,75.00,'potato','2025-10-30 04:05:12','2025-10-30 04:05:12'),(16,6,45.00,55.00,60.00,120.00,30.00,75.00,'potato','2025-10-30 04:07:50','2025-10-30 04:07:50'),(17,6,45.00,55.00,60.00,120.00,301.00,75.00,'potato','2025-10-30 04:07:53','2025-10-30 04:07:53'),(18,6,45.00,55.00,60.00,120.00,301.00,75.00,'potato','2025-10-30 04:07:55','2025-10-30 04:07:55'),(19,6,45.00,55.00,60.00,120.00,301.00,75.00,'potato','2025-10-30 04:07:56','2025-10-30 04:07:56'),(20,6,45.00,55.00,60.00,120.00,301.00,75.00,'potato','2025-10-30 04:07:57','2025-10-30 04:07:57'),(21,6,45.00,55.00,60.00,120.00,301.00,75.00,'potato','2025-10-30 04:13:10','2025-10-30 04:13:10'),(22,6,68.00,105.00,90.00,2000.00,300.00,75.00,'potato','2025-10-30 04:13:33','2025-10-30 04:13:33'),(23,6,68.00,105.00,90.00,200.00,300.00,75.00,'potato','2025-10-30 04:13:43','2025-10-30 04:13:43'),(24,6,222.00,105.00,90.00,200.00,300.00,75.00,'potato','2025-10-30 04:13:51','2025-10-30 04:13:51'),(25,6,222.00,105.00,94.00,200.00,300.00,75.00,'potato','2025-10-30 04:13:57','2025-10-30 04:13:57');
/*!40000 ALTER TABLE `crops` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `seed_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `total_amount` decimal(10,2) NOT NULL,
  `payment_status` enum('pending','completed','failed') DEFAULT 'pending',
  `payment_method` enum('esewa','cash_on_delivery') DEFAULT 'esewa',
  `transaction_id` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `seed_id` (`seed_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`seed_id`) REFERENCES `seeds` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seeds`
--

DROP TABLE IF EXISTS `seeds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `seeds` (
  `id` int NOT NULL AUTO_INCREMENT,
  `crop_name` varchar(100) NOT NULL,
  `description` text,
  `price` decimal(10,2) NOT NULL,
  `stock` int DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seeds`
--

LOCK TABLES `seeds` WRITE;
/*!40000 ALTER TABLE `seeds` DISABLE KEYS */;
INSERT INTO `seeds` VALUES (1,'Rice','High quality rice seeds',120.00,50,'2025-10-28 09:06:22','2025-10-28 09:06:22'),(2,'Wheat','Premium wheat seeds',100.00,50,'2025-10-28 09:06:22','2025-10-28 09:06:22'),(3,'Barley','Healthy barley seeds',90.00,40,'2025-10-28 09:06:22','2025-10-28 09:06:22'),(4,'Buckwheat','Organic buckwheat seeds',110.00,30,'2025-10-28 09:06:22','2025-10-28 09:06:22'),(5,'Millet','Nutritious millet seeds',95.00,40,'2025-10-28 09:06:22','2025-10-28 09:06:22'),(6,'Sugarcane','Sugarcane seeds for high yield',150.00,20,'2025-10-28 09:06:22','2025-10-28 09:06:22'),(7,'Potato','High yield potato seeds',80.00,60,'2025-10-28 09:06:22','2025-10-28 09:06:22'),(8,'Peanuts','Peanut seeds for local cultivation',250.00,20,'2025-10-28 09:06:22','2025-10-28 09:06:22'),(9,'Ginger','Fresh ginger rhizome seeds',200.00,25,'2025-10-28 09:06:22','2025-10-28 09:06:22'),(10,'Common beans','Common beans seeds',130.00,30,'2025-10-28 09:06:22','2025-10-28 09:06:22'),(11,'Field peas','Field peas seeds',110.00,35,'2025-10-28 09:06:22','2025-10-28 09:06:22');
/*!40000 ALTER TABLE `seeds` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `role` enum('user','admin') NOT NULL DEFAULT 'user',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Mandib1','$2b$12$GhHCiKwaib1Yn13XoUn8A.fhf8xqwgw3xy7jlt9Czlgwx7Ug1yxTa','mandibchaulagain@gmail.com','2025-07-31 12:57:16','2025-07-31 12:57:16','user'),(2,'john_doe123','$2b$12$5prP9zNtrbRSkma6clVEO.O32zSvYFcAeHB0snbt3AOFMKF8MA4te','user@example.com','2025-07-31 13:13:05','2025-07-31 13:13:05','user'),(4,'john_doe69','$2b$12$x8oDANvjuyki2DdE2Ex62eoslj9twALuuuD7lzpS3.9AiuiYq0C.a','user@gmail.com','2025-07-31 13:28:41','2025-08-01 15:19:49','admin'),(6,'Mandib2','$2b$12$APKxMIAeJ6tWcaE.qiV.7uTBvEZaWcQJjBUZgmD58x6SBydeU9RWq','manu@example.com','2025-10-28 10:40:37','2025-10-28 10:40:37','user');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'croprec_db'
--

--
-- Dumping routines for database 'croprec_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-21 15:14:39
