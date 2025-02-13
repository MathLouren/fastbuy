-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: e_commerce
-- ------------------------------------------------------
-- Server version	8.0.41

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
-- Table structure for table `likes`
--

DROP TABLE IF EXISTS `likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `likes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `produto_id` int NOT NULL,
  `tipo` enum('like','dislike') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_vote` (`user_id`,`produto_id`),
  KEY `produto_id` (`produto_id`),
  CONSTRAINT `likes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `likes_ibfk_2` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `likes`
--

LOCK TABLES `likes` WRITE;
/*!40000 ALTER TABLE `likes` DISABLE KEYS */;
INSERT INTO `likes` VALUES (1,1,2,'like'),(2,1,1,'like'),(3,6,1,'like');
/*!40000 ALTER TABLE `likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produtos`
--

DROP TABLE IF EXISTS `produtos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produtos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome_produto` varchar(255) NOT NULL,
  `descricao` text NOT NULL,
  `preco` decimal(10,2) DEFAULT NULL,
  `imagem` varchar(255) NOT NULL,
  `user_id` int DEFAULT NULL,
  `likes` int DEFAULT '0',
  `dislikes` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `produtos_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produtos`
--

LOCK TABLES `produtos` WRITE;
/*!40000 ALTER TABLE `produtos` DISABLE KEYS */;
INSERT INTO `produtos` VALUES (1,'celular','Notebook com tela de 15,6 polegadas Full HD, processador Intel Core i5, 8 GB de RAM, 256 GB SSD e Windows 11.',2123232.00,'static\\uploads\\icon.png',1,12,0),(2,'Combo Z Flip6 (512GB) - Cinza + Galaxy Watch Ultra LTE 47mm - Titânio Cinza','O novo design suspenso do Galaxy Z Flip6 é moderno, fino e elegante, criando nosso smartphone mais compacto até agora.',13000.00,'static\\uploads\\D_NQ_NP_639188-MLU70705862697_072023-O.png',1,0,0),(3,'testestestes','testestestse',299.99,'static\\uploads\\D_NQ_NP_639188-MLU70705862697_072023-O.png',6,0,0);
/*!40000 ALTER TABLE `produtos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `telephone` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Matheus lourenco','lourencomatheus487@gmail.com','324242iu42','$2b$12$cZBnOi743QgQaRPTQ5jtiOt6A7DNwEMt7B0AeNsPj4R6AukJInY.S',''),(2,'Hardwell','teste@gmail.com','2198329832','$2b$12$GyUYBaygG/fyGf/88LUx.e9ufOsav0hc.N9/Um69IgNuL7f3KfAm2',''),(3,'sjabjdbajbdsjadbjabdj','nxjfbjfbajfba@gmail.com','(21) 99819-6861','$2b$12$6vjqJnNog3DFwEv3lZllOer5gnGgkR7cFn7ahRQoxDpmAPYzGxbjC',''),(5,'Matheus lourenco','lourencomatheus4879@gmail.com','(21) 99819-6862','$2b$12$xqRix4zMpjMIz/DNHLrr8ucK9fm339zZsydXgnE4NYwJ/FP25ovLa',''),(6,'fsdnfksnfskd','nfdjbfsd372@gmail.com','(32) 83928-3928','$2b$12$fa/TfQhF/jjwToZFAc0iNOi/k/xMqjwFh8z5z5F/njDgibyvnJsZm','kodskaok'),(7,'Rafael Soares','rafa@gmail.com','(21) 93829-8329','$2b$12$GlRj.mZUpqgjo/yn4MgmWO5kI271fSl0hdYIIxRbll/tafJ6ELmNm','rafa94383q');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-02-13  5:16:20
