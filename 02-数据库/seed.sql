USE test;
SET FOREIGN_KEY_CHECKS=0;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: test
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
INSERT INTO `cart` (`id`, `user_id`, `created_at`, `updated_at`) VALUES (4,4,'2026-06-03 10:34:38','2026-06-03 10:34:38'),(5,5,'2026-06-03 10:34:50','2026-06-03 10:34:50'),(6,6,'2026-06-04 16:56:21','2026-06-04 16:56:21'),(7,7,'2026-07-01 12:45:24','2026-07-01 12:45:24'),(8,8,'2026-07-25 12:19:26','2026-07-25 12:19:26'),(10,14,'2026-10-08 15:23:37','2026-10-08 15:23:37'),(11,15,'2026-11-23 11:40:02','2026-11-23 11:40:02');
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `cart_item`
--

LOCK TABLES `cart_item` WRITE;
/*!40000 ALTER TABLE `cart_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `order`
--

LOCK TABLES `order` WRITE;
/*!40000 ALTER TABLE `order` DISABLE KEYS */;
INSERT INTO `order` (`id`, `user_id`, `created_at`, `status`, `total_price`) VALUES (25,5,'2026-06-03 11:00:39','paid',100),(26,5,'2026-06-03 11:02:19','paid',100),(27,4,'2026-06-03 11:11:10','paid',100),(28,4,'2026-06-03 11:15:33','paid',100),(29,4,'2026-06-03 11:16:05','paid',100),(30,5,'2026-06-04 15:35:04','pending',100),(31,6,'2026-06-04 16:57:25','paid',100),(32,6,'2026-06-04 17:00:16','paid',20000),(33,6,'2026-06-04 17:00:49','pending',80200),(34,6,'2026-06-04 17:04:34','paid',20000),(35,4,'2026-07-01 12:02:00','paid',200),(36,4,'2026-07-01 12:02:31','paid',20000),(37,4,'2026-07-01 12:05:15','paid',200),(38,4,'2026-07-01 12:30:34','paid',200),(39,7,'2026-07-01 12:46:00','paid',20044),(40,7,'2026-07-01 15:51:02','paid',10022),(41,7,'2026-07-01 15:53:16','pending',10022),(42,7,'2026-07-01 16:00:52','paid',10022),(43,7,'2026-07-01 16:03:22','paid',10022),(44,5,'2026-09-03 08:43:56','paid',10022),(45,14,'2026-10-08 15:27:45','pending',10022);
/*!40000 ALTER TABLE `order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `order_item`
--

LOCK TABLES `order_item` WRITE;
/*!40000 ALTER TABLE `order_item` DISABLE KEYS */;
INSERT INTO `order_item` (`id`, `order_id`, `product_id`, `product_name`, `price`, `quantity`, `subtotal`, `image_url`, `created_at`) VALUES (31,25,4,'Updated Product',100,1,100,NULL,'2026-06-03 11:00:39'),(32,26,4,'Updated Product',100,1,100,NULL,'2026-06-03 11:02:19'),(33,27,4,'Updated Product',100,1,100,NULL,'2026-06-03 11:11:10'),(34,28,4,'Updated Product',100,1,100,NULL,'2026-06-03 11:15:33'),(35,29,4,'Updated Product',100,1,100,NULL,'2026-06-03 11:16:05'),(36,30,4,'Updated Product',100,1,100,NULL,'2026-06-04 15:35:04'),(37,31,4,'Updated Product',100,1,100,NULL,'2026-06-04 16:57:25'),(39,33,6,'zxc',200,1,200,NULL,'2026-06-04 17:00:49'),(42,35,6,'zxc',200,1,200,NULL,'2026-07-01 12:02:00'),(44,37,6,'zxc',200,1,200,NULL,'2026-07-01 12:05:15'),(45,38,6,'zxc',200,1,200,NULL,'2026-07-01 12:30:34'),(46,39,7,'test_product_seller',10022,2,20044,'/static/uploads/20260701124229_png','2026-07-01 12:46:00'),(47,40,7,'test_product_seller',10022,1,10022,'/static/uploads/20260701124229_png','2026-07-01 15:51:02'),(48,41,7,'test_product_seller',10022,1,10022,'/static/uploads/20260701124229_png','2026-07-01 15:53:16'),(49,42,7,'test_product_seller',10022,1,10022,'/static/uploads/20260701124229_png','2026-07-01 16:00:52'),(50,43,7,'test_product_seller',10022,1,10022,'/static/uploads/20260701124229_png','2026-07-01 16:03:22'),(51,44,7,'test_product_seller',10022,1,10022,'/static/uploads/20260701124229_png','2026-09-03 08:43:56'),(52,45,7,'test_product_seller',10022,1,10022,'/static/uploads/20260701124229_png','2026-10-08 15:27:45');
/*!40000 ALTER TABLE `order_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `product`
--

LOCK TABLES `product` WRITE;
/*!40000 ALTER TABLE `product` DISABLE KEYS */;
INSERT INTO `product` (`id`, `name`, `description`, `price`, `status`, `seller_id`, `image_url`, `created_at`, `updated_at`) VALUES (4,'Updated Product_1111','Updated Description',10000,'active',2,NULL,'2026-06-03 10:40:27','2026-07-01 15:46:13'),(6,'zxc','wiu',200,'active',2,NULL,'2026-06-04 16:58:46','2026-06-04 16:58:46'),(7,'test_product_seller','wu',10022,'active',4,'/static/uploads/20260701124229_png','2026-07-01 12:42:16','2026-07-01 12:42:29');
/*!40000 ALTER TABLE `product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `seller`
--

LOCK TABLES `seller` WRITE;
/*!40000 ALTER TABLE `seller` DISABLE KEYS */;
INSERT INTO `seller` (`id`, `username`, `password`, `address`, `phone`, `is_active`, `role`, `permissions`, `failed_attempts`, `lock_until`, `created_at`, `updated_at`) VALUES (2,'seller_1','$2b$12$hJnKnS9a2x2fdrZ8ID8h9OO0Wi8Jg78saFMfBcC9mZgFBWf2xvW1.',NULL,NULL,1,'seller',NULL,0,NULL,'2026-06-03 10:35:02','2026-06-03 10:35:02'),(3,'seller_2','$2b$12$D6fW3sBE2qmOO8GAU44BWOfw4ZMRyEpmk618qkUtdU4wEykf01QsC',NULL,NULL,1,'seller',NULL,0,NULL,'2026-06-03 10:35:15','2026-06-03 10:35:15'),(4,'seller_test','$2b$12$kxA5deK99y11B95uz5BvOOA665HNzXfxnJwrb45S3M0hgmsd8EgVa',NULL,NULL,1,'seller',NULL,0,NULL,'2026-07-01 12:41:13','2026-07-01 12:41:13');
/*!40000 ALTER TABLE `seller` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `staff`
--

LOCK TABLES `staff` WRITE;
/*!40000 ALTER TABLE `staff` DISABLE KEYS */;
INSERT INTO `staff` (`id`, `username`, `password`, `role`, `permissions`, `is_active`, `failed_attempts`, `lock_until`, `totp_secret_enc`, `totp_enabled`, `recovery_hashes`, `last_totp_step`, `created_at`, `updated_at`) VALUES (1,'admin1','$2b$12$5.Fpv27COIsMJaBU6FNFLO4gmAVR6G3AbzX8WvCb6C9N07.//.Ziu','admin',NULL,1,0,NULL,'8aff6dc437343d8273299f71a8dd16ca:53616c7465645f5ff9887fe6f3eab32f09093d628ba4ca2dd34f00d23ab7ba4adb9c7c5a8a7f07436ac6b21366dac4d246fec5a5303d62e56ffdb48581384bf3',1,'[\"cfc6c671a0522967a68c41ac01c918623d83e7aba90a5b0213d7d7e0285fc88a\", \"5120ed3e26c06341ff048d6216c9de8a86a5fb7ba54c19a31f63374ffd1fb929\", \"35043e68fccc253be1c0a79804725a3a0ad6385e81420aad219b787d7ab5e521\", \"c5665ec1d387899da7ea67d52bb293d8138548a4b0f03c834041aad7238dedd4\", \"bd901897a1c8f3e824cea97a70227d49841522ce1baf0d833992f885ed67bed9\", \"b478370a383fbb969e4ce66b804b701fb94fc9a7d15abec33cf813f489b18c77\", \"3f4c23ec94a4976aff473e7d256f8b9227e62e128e8111fc96888276dc2e4ece\", \"55e6771006a5e30375a3f97963ae46f2aee234174eb4ed371e0c0bdc897fdb3f\"]',NULL,'2026-09-03 16:30:09','2026-11-21 07:13:35'),(2,'audit1','$2b$12$Y.NpwUCJdKaFeCi7q9EtpuGWZdCKq5sVun5aW0j2QRIzqgkKCsEVi','auditor',NULL,1,0,NULL,'c13ada931575682b48d231046d71335d:53616c7465645f5f9f95fea5f37912735107d8f1f994e65fb43e1f602403f58e517672cb8ac3da211b50cefa454aee8de4311a76dc68924afc51db50b843447b',1,'[\"175cf564808970bee440ce9e02cea5493f684dc898e8870b378867358dba9c24\", \"c86389eb513b2c999ff106f710e2121cfdd63c9a54ba07a986719f2fc22f4b42\", \"db9aef80f45f2d466836a0c0a0b60539178514967c8977ba992b350ea8efbd6e\", \"74a7fe61c87ab7bc28c3902671f3f79ef5698e74c9b61be12b601d9b5a535461\", \"f06c89dfed1866188cb3db332ee9610510bdc195d2b68a8cfb6a5243e21d5c04\", \"4f17a22114edb0cd8ca5d081de77b4059bcd310995a513fddd63e794c93da6d5\", \"5ecb42b7a485c63c2177891a8f346b3e016fbaf3e659a962221ccaa34e6b9633\"]',59838826,'2026-09-03 16:30:10','2026-11-20 08:53:11');
/*!40000 ALTER TABLE `staff` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` (`id`, `username`, `password`, `is_active`, `role`, `permissions`, `failed_attempts`, `lock_until`, `created_at`, `updated_at`) VALUES (4,'user_1','$2b$12$DwddAy/p2gXWij9mrVleSuoLHNHNH3YrXV/6BCky6i1i3QR2LnU.u',1,'user',NULL,0,NULL,'2026-06-03 10:34:38','2026-10-29 11:03:03'),(5,'user_2','$2b$12$aixV2VYnoQa77nms/4qrduM1l9jGDifNzxJv0SLYHzck1VMo4I5xe',1,'user',NULL,0,NULL,'2026-06-03 10:34:50','2026-09-03 13:29:42'),(6,'user_3','$2b$12$RiukZfKikvtI/1X3bsKoNeXUfUAb2fEy3S15vSHZNIWmnJEZZHJna',1,'user',NULL,0,NULL,'2026-06-04 16:56:21','2026-06-04 16:56:21'),(7,'user_3_','$2b$12$Be.GKD0sU4mJbvKr4teFYuIWrZ0Up81VFfrH4/ZJPZr7Zuh.yKd.O',0,'user',NULL,0,NULL,'2026-07-01 12:45:24','2026-09-09 07:33:00'),(8,'assswd','$2b$12$T1ibjrWW455FAoInWkJ4Te5hKtmrwaeisSgXujLidVyB5XnsjzC3i',1,'user',NULL,0,NULL,'2026-07-25 12:19:26','2026-09-04 02:27:53'),(14,'kali_test1','$2b$12$XSOWjEgmEMQvRxere4T0AOtPuk8bWhULUaHadY.2vlsxbbAOwLymC',0,'user',NULL,0,NULL,'2026-10-08 15:23:37','2026-10-15 03:15:11'),(15,'user_1234','$2b$12$S7tot522JOVAOTrHWgQda.1ShKstUw2UXJV0XbNEBcV8cyV/ADMe6',1,'user',NULL,0,NULL,'2026-11-23 11:40:02','2026-11-23 11:40:02');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-23 14:53:25
SET FOREIGN_KEY_CHECKS=1;
