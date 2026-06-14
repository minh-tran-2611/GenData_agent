-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: siupo_db
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `addresses`
--

DROP TABLE IF EXISTS `addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addresses` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `address` varchar(255) NOT NULL,
  `district` varchar(100) NOT NULL,
  `province` varchar(100) NOT NULL,
  `receiver_name` varchar(100) NOT NULL,
  `receiver_phone` varchar(11) NOT NULL,
  `ward` varchar(100) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_address_full_content` (`user_id`,`address`,`ward`,`district`,`province`,`receiver_name`,`receiver_phone`),
  CONSTRAINT `FK1fa36y2oqhao3wgg2rw1pi459` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `addresses`
--

--
-- Table structure for table `banners`
--

DROP TABLE IF EXISTS `banners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banners` (
  `position` varchar(255) DEFAULT NULL,
  `id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FKqx4gpamdfr4m5al6c1sq41ktg` FOREIGN KEY (`id`) REFERENCES `images` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `banners`
--

LOCK TABLES `banners` WRITE;
/*!40000 ALTER TABLE `banners` DISABLE KEYS */;
INSERT INTO `banners` VALUES ('Home2',97),('Menu1',99),('Menu2',100),('Menu3',101),('Menu4',102),('AboutUs2',104),('AboutUs3',105),('AboutUs4',106),('AboutUs5',107),('PlaceTable1',108);
/*!40000 ALTER TABLE `banners` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `price` double DEFAULT NULL,
  `quantity` bigint DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `cart_id` bigint DEFAULT NULL,
  `combo_id` bigint DEFAULT NULL,
  `product_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKpcttvuq4mxppo8sxggjtn5i2c` (`cart_id`),
  KEY `FKehppwg68060786o4y7l1hl109` (`combo_id`),
  KEY `FK1re40cjegsfvw58xrkdp6bac6` (`product_id`),
  CONSTRAINT `FK1re40cjegsfvw58xrkdp6bac6` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `FKehppwg68060786o4y7l1hl109` FOREIGN KEY (`combo_id`) REFERENCES `combos` (`id`),
  CONSTRAINT `FKpcttvuq4mxppo8sxggjtn5i2c` FOREIGN KEY (`cart_id`) REFERENCES `carts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--


--
-- Table structure for table `carts`
--

DROP TABLE IF EXISTS `carts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `total_price` double DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK64t7ox312pqal3p7fg9o503c2` (`user_id`),
  CONSTRAINT `FKb5o626f86h46m4s7ms6ginnop` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carts`
--


--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `image_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UKt8o6pivur7nn124jehx7cygw5` (`name`),
  UNIQUE KEY `UK6b3bn760mqxmhflt089q8ba00` (`image_id`),
  CONSTRAINT `FKqhmw54g2p4xu0k71mblvlqfvi` FOREIGN KEY (`image_id`) REFERENCES `images` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Appetizers',137),(2,'Main Course',138),(3,'Desserts',139),(4,'Beverages',140),(5,'Seafood',141),(6,'Pasta',142),(7,'Salads',143),(8,'Burgers',144),(9,'Starter Menu',145),(10,'Drink',146);
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cod_payments`
--

DROP TABLE IF EXISTS `cod_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cod_payments` (
  `note` varchar(255) DEFAULT NULL,
  `id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FKo6muf5be5eo3iftxaag3ylxtk` FOREIGN KEY (`id`) REFERENCES `payments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cod_payments`
--


--
-- Table structure for table `combo_images`
--

DROP TABLE IF EXISTS `combo_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `combo_images` (
  `id` bigint NOT NULL,
  `combo_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKcg76x8tdnnyxq4c92bnb5yw5b` (`combo_id`),
  CONSTRAINT `FKcg76x8tdnnyxq4c92bnb5yw5b` FOREIGN KEY (`combo_id`) REFERENCES `combos` (`id`),
  CONSTRAINT `FKox74yi8fdu4gh2krg5pxrihuq` FOREIGN KEY (`id`) REFERENCES `images` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `combo_images`
--

LOCK TABLES `combo_images` WRITE;
/*!40000 ALTER TABLE `combo_images` DISABLE KEYS */;
INSERT INTO `combo_images` VALUES (130,1),(134,2),(136,3),(147,4),(148,5),(149,6);
/*!40000 ALTER TABLE `combo_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `combo_items`
--

DROP TABLE IF EXISTS `combo_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `combo_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `display_order` int NOT NULL,
  `quantity` int NOT NULL,
  `combo_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK48h944x1aynyjkgfxa1tu5n32` (`combo_id`),
  KEY `FKp7wjg7ht16w8bfu0623pcwqp0` (`product_id`),
  CONSTRAINT `FK48h944x1aynyjkgfxa1tu5n32` FOREIGN KEY (`combo_id`) REFERENCES `combos` (`id`),
  CONSTRAINT `FKp7wjg7ht16w8bfu0623pcwqp0` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `combo_items`
--

LOCK TABLES `combo_items` WRITE;
/*!40000 ALTER TABLE `combo_items` DISABLE KEYS */;
INSERT INTO `combo_items` VALUES (1,0,1,1,1),(2,1,1,1,3),(3,2,1,1,2),(4,3,1,1,6),(5,4,1,1,7),(21,0,1,2,1),(22,1,1,2,3),(23,2,1,2,5),(24,3,1,2,7),(25,4,1,2,6),(31,0,1,3,2),(32,1,1,3,5),(33,2,1,3,3),(34,3,1,3,7),(35,0,1,4,5),(36,1,1,4,6),(37,2,1,4,1),(38,3,4,4,28),(39,0,1,5,13),(40,1,1,5,9),(41,2,2,5,30),(42,0,1,6,21),(43,1,1,6,9),(44,2,1,6,39);
/*!40000 ALTER TABLE `combo_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `combos`
--

DROP TABLE IF EXISTS `combos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `combos` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `base_price` double NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `description` varchar(2000) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `status` enum('AVAILABLE','DELETED','UNAVAILABLE') NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `combos`
--

LOCK TABLES `combos` WRITE;
/*!40000 ALTER TABLE `combos` DISABLE KEYS */;
INSERT INTO `combos` VALUES (1,200,'2025-12-17 12:31:45.117918','hádhasjdhkashd','12321312','DELETED','2025-12-17 17:52:56.553251'),(2,200,'2025-12-17 12:39:03.989868','ád23123213awdaqwd','adasdasdasdasd','DELETED','2025-12-17 17:52:58.252814'),(3,1111,'2025-12-17 12:40:29.676553','22222222222','11111111111111111111','DELETED','2025-12-17 17:53:00.064537'),(4,75,'2025-12-17 17:54:03.000000','Combo thịnh soạn dành cho gia đình 4 người gồm Steak, Ribs, Salad và đồ uống.','Family Feast Combo','AVAILABLE','2025-12-17 17:54:03.000000'),(5,45,'2025-12-17 17:54:03.000000','Combo lãng mạn cho 2 người với Pasta, Seafood và rượu vang/nước trái cây.','Romantic Date Night','AVAILABLE','2025-12-17 17:54:03.000000'),(6,30,'2025-12-17 17:54:03.000000','Lựa chọn lành mạnh với Salad, Cá hồi áp chảo và nước ép tươi.','Green Life Combo','AVAILABLE','2025-12-17 17:54:03.000000');
/*!40000 ALTER TABLE `combos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `images`
--

DROP TABLE IF EXISTS `images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `images` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `url` varchar(2000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=150 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `images`
--

LOCK TABLES `images` WRITE;
/*!40000 ALTER TABLE `images` DISABLE KEYS */;
INSERT INTO `images` VALUES (1,NULL,'Caesar Salad 1',NULL,'https://images.unsplash.com/photo-1546793665-c74683f339c1?w=800'),(2,NULL,'Caesar Salad 2',NULL,'https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=800'),(3,NULL,'Caesar Salad 3',NULL,'https://images.unsplash.com/photo-1512852939750-1305098529bf?w=800'),(4,NULL,'Chicken Wings 1',NULL,'https://images.unsplash.com/photo-1608039755401-742074f0548d?w=800'),(5,NULL,'Chicken Wings 2',NULL,'https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=800'),(6,NULL,'Chicken Wings 3',NULL,'https://images.unsplash.com/photo-1567620832903-9fc6debc209f?w=800'),(8,NULL,'Mozzarella Sticks 1',NULL,'https://images.unsplash.com/photo-1531749668029-2db88e4276c7?w=800'),(9,NULL,'Mozzarella Sticks 2',NULL,'https://images.unsplash.com/photo-1548340748-6d2b7d7da280?w=800'),(10,NULL,'Bruschetta 1',NULL,'https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?w=800'),(11,NULL,'Bruschetta 2',NULL,'https://images.unsplash.com/photo-1506280754576-f6fa8a873550?w=800'),(12,NULL,'Bruschetta 3',NULL,'https://images.unsplash.com/photo-1529042410759-befb1204b468?w=800'),(13,NULL,'Ribeye Steak 1',NULL,'https://images.unsplash.com/photo-1588168333986-5078d3ae3976?w=800'),(14,NULL,'Ribeye Steak 2',NULL,'https://images.unsplash.com/photo-1546964124-0cce460f38ef?w=800'),(15,NULL,'Ribeye Steak 3',NULL,'https://images.unsplash.com/photo-1603360946369-dc9bb6258143?w=800'),(16,NULL,'Ribeye Steak 4',NULL,'https://images.unsplash.com/photo-1558030006-450675393462?w=800'),(17,NULL,'BBQ Ribs 1',NULL,'https://images.unsplash.com/photo-1544025162-d76694265947?w=800'),(18,NULL,'BBQ Ribs 2',NULL,'https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?w=800'),(20,NULL,'Roasted Chicken 1',NULL,'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=800'),(21,NULL,'Roasted Chicken 2',NULL,'https://images.unsplash.com/photo-1594221708779-94832f4320d1?w=800'),(22,NULL,'Lamb Chops 1',NULL,'https://images.unsplash.com/photo-1595777216528-071e0127ccbf?w=800'),(25,NULL,'Lamb Chops 4',NULL,'https://images.unsplash.com/photo-1600891964599-f61ba0e24092?w=800'),(26,NULL,'Grilled Salmon 1',NULL,'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=800'),(28,NULL,'Grilled Salmon 3',NULL,'https://images.unsplash.com/photo-1485921325833-c519f76c4927?w=800'),(29,NULL,'Shrimp Scampi 1',NULL,'https://images.unsplash.com/photo-1633237308525-cd587cf71926?w=800'),(30,NULL,'Shrimp Scampi 2',NULL,'https://images.unsplash.com/photo-1604909052743-94e838986d24?w=800'),(33,NULL,'Fish and Chips 3',NULL,'https://images.unsplash.com/photo-1580217593608-61931cefc821?w=800'),(34,NULL,'Fish and Chips 4',NULL,'https://images.unsplash.com/photo-1563865436874-9aef32095fad?w=800'),(36,NULL,'Lobster Tail 2',NULL,'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=800'),(37,NULL,'Spaghetti Carbonara 1',NULL,'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800'),(38,NULL,'Spaghetti Carbonara 2',NULL,'https://images.unsplash.com/photo-1600803907087-f56d462fd26b?w=800'),(39,NULL,'Spaghetti Carbonara 3',NULL,'https://images.unsplash.com/photo-1588013273468-315fd88ea34c?w=800'),(40,NULL,'Fettuccine Alfredo 1',NULL,'https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=800'),(41,NULL,'Fettuccine Alfredo 2',NULL,'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800'),(43,NULL,'Fettuccine Alfredo 4',NULL,'https://images.unsplash.com/photo-1619895092538-128341789043?w=800'),(44,NULL,'Lasagna 1',NULL,'https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=800'),(45,NULL,'Lasagna 2',NULL,'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800'),(48,NULL,'Penne Arrabbiata 3',NULL,'https://images.unsplash.com/photo-1608219992759-8d74ed8d76eb?w=800'),(49,NULL,'Cheeseburger 1',NULL,'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800'),(50,NULL,'Cheeseburger 2',NULL,'https://images.unsplash.com/photo-1550547660-d9450f859349?w=800'),(51,NULL,'Cheeseburger 3',NULL,'https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=800'),(52,NULL,'Cheeseburger 4',NULL,'https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=800'),(53,NULL,'Bacon Burger 1',NULL,'https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=800'),(54,NULL,'Bacon Burger 2',NULL,'https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=800'),(55,NULL,'Bacon Burger 3',NULL,'https://images.unsplash.com/photo-1565299507177-b0ac66763828?w=800'),(57,NULL,'Mushroom Burger 2',NULL,'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=800'),(58,NULL,'Veggie Burger 1',NULL,'https://images.unsplash.com/photo-1520072959219-c595dc870360?w=800'),(59,NULL,'Veggie Burger 2',NULL,'https://images.unsplash.com/photo-1585238342024-78d387f4a707?w=800'),(62,NULL,'Greek Salad 1',NULL,'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800'),(63,NULL,'Greek Salad 2',NULL,'https://images.unsplash.com/photo-1580013759032-c96505e24c1f?w=800'),(64,NULL,'Greek Salad 3',NULL,'https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=800'),(66,NULL,'Cobb Salad 2',NULL,'https://images.unsplash.com/photo-1505576399279-565b52d4ac71?w=800'),(67,NULL,'Caprese Salad 1',NULL,'https://images.unsplash.com/photo-1592417817098-8fd3d9eb14a5?w=800'),(70,NULL,'Caprese Salad 4',NULL,'https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?w=800'),(71,NULL,'Chocolate Lava Cake 1',NULL,'https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=800'),(73,NULL,'Chocolate Lava Cake 3',NULL,'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=800'),(74,NULL,'Tiramisu 1',NULL,'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=800'),(79,NULL,'Cheesecake 2',NULL,'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800'),(80,NULL,'Apple Pie 1',NULL,'https://images.unsplash.com/photo-1535920527002-b35e96722eb9?w=800'),(81,NULL,'Apple Pie 2',NULL,'https://images.unsplash.com/photo-1590841609987-4ac211afdde1?w=800'),(84,NULL,'Orange Juice 1',NULL,'https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=800'),(85,NULL,'Orange Juice 2',NULL,'https://images.unsplash.com/photo-1613478223719-2ab802602423?w=800'),(87,NULL,'Iced Coffee 1',NULL,'https://images.unsplash.com/photo-1517487881594-2787fef5ebf7?w=800'),(88,NULL,'Iced Coffee 2',NULL,'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=800'),(89,NULL,'Mojito 1',NULL,'https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=800'),(90,NULL,'Mojito 2',NULL,'https://images.unsplash.com/photo-1546171753-97d7676e4602?w=800'),(91,NULL,'Mojito 3',NULL,'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=800'),(93,NULL,'Strawberry Smoothie 1',NULL,'https://images.unsplash.com/photo-1505252585461-04db1eb84625?w=800'),(94,NULL,'Strawberry Smoothie 2',NULL,'https://images.unsplash.com/photo-1638176066666-ffb2f013c7dd?w=800'),(95,NULL,'Strawberry Smoothie 3',NULL,'https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?w=800'),(97,NULL,'image_hero_mobile',NULL,'https://res.cloudinary.com/delsqnlsu/image/upload/v1763289566/products/syt7oukjbnreqvwfqguh.png'),(99,NULL,'image_salad',NULL,'https://res.cloudinary.com/delsqnlsu/image/upload/v1763289582/products/cgwudwpgm06ildn3f1fw.png'),(100,NULL,'image_cupcake',NULL,'https://res.cloudinary.com/delsqnlsu/image/upload/v1763289598/products/ckbouav0hm9wg01gy475.png'),(101,NULL,'image_cocktail',NULL,'https://res.cloudinary.com/delsqnlsu/image/upload/v1763289612/products/kipyiogt8vxs4spylae5.png'),(102,NULL,'image_burger',NULL,'https://res.cloudinary.com/delsqnlsu/image/upload/v1763289628/products/l6peauxgtfndana2fbf8.png'),(104,NULL,'image_about_us_staff',NULL,'https://res.cloudinary.com/delsqnlsu/image/upload/v1763288047/products/e78n46vzmwtu82qx85yx.png'),(105,NULL,'image_about_us_6',NULL,'https://res.cloudinary.com/delsqnlsu/image/upload/v1763288654/products/dxqpfzh72perw2g5ezwd.png'),(106,NULL,'image_about_us_client',NULL,'https://res.cloudinary.com/delsqnlsu/image/upload/v1763288739/products/mzgdrhrecuf69nxxxosw.png'),(107,NULL,'image_about_us_4',NULL,'https://res.cloudinary.com/delsqnlsu/image/upload/v1763289398/products/ccnvg5jpwjutckoxzeqh.png'),(108,NULL,'image_place_table.png',NULL,'https://res.cloudinary.com/delsqnlsu/image/upload/v1763289656/products/pjygqb5eir9cmgxn2dok.jpg'),(109,NULL,'Spring Rolls 1',NULL,'https://www.thespruceeats.com/thmb/LAD6HCmf0MFSpV3JDJgM9n7REos=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/SES-thai-fresh-rolls-with-vegetarian-option-3217706-hero-A-3bdb04a8ee2444a2ab6873810a334642.jpg'),(110,NULL,'Spring Rolls 2',NULL,'https://www.thesavorychopstick.com/wp-content/uploads/2022/08/Spring-Rolls.jpg'),(111,NULL,'Spring Rolls 3',NULL,'https://www.thelittlekitchen.net/wp-content/uploads/2021/07/vietnamese-spring-rolls-the-little-kitchen-398.jpg'),(112,NULL,'Fried Calamari 1',NULL,'https://www.seriouseats.com/thmb/RLHQFr_lp9-HTIWBikzVwu4M17s=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/__opt__aboutcom__coeus__resources__content_migration__serious_eats__seriouseats.com__2020__11__20201125-fried-calamari-vicky-wasik-10-9cee3a081e96476b89e29b331d30be61.jpg'),(113,NULL,'Fried Calamari 2',NULL,'https://www.mygreekdish.com/wp-content/uploads/2014/02/Crispy-Fried-Squid-Calamari-recipe-Kalamarakia-Tiganita-1-scaled.jpg'),(114,NULL,'Stuffed Mushrooms 1',NULL,'https://thedizzycook.com/wp-content/uploads/2023/11/Boursin-Stuffed-Mushrooms-Main.jpg'),(115,NULL,'Stuffed Mushrooms 2',NULL,'https://www.allrecipes.com/thmb/7I7cUkGvyoC_wA6V5F6Yvnd95zU=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/AR-JF-15184-Mouth-Watering-Mushrooms-ddmfs-4x3-86b91d21dcd44c738f0391eaeab12857.jpg'),(116,NULL,'Stuffed Mushrooms 3',NULL,'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQesX3wILjYx2XRM5HORdoXLi9piQkDEXju_Q&s'),(117,NULL,'Prawn Cocktail 1',NULL,'https://www.deliciousmagazine.co.uk/wp-content/uploads/2018/09/334546-1-eng-GB_7186.jpg'),(118,NULL,'Prawn Cocktail 2',NULL,'https://bitesinthewild.com/wp-content/uploads/2022/12/Prawn-cocktail-salad-on-a-glass-feature-image-1.jpg'),(119,NULL,'Lemonade 1',NULL,'https://www.jocooks.com/wp-content/uploads/2023/05/lemonade-1-28.jpg'),(120,NULL,'Lemonade 2',NULL,'https://www.allrecipes.com/thmb/x6zdkHlYGSloSRUDYC4cR7Blk-8=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/445156_Vintage-Lemonade-4x3-195c79927325479bb7848ece5cab897f.jpg'),(121,NULL,'Lemonade 3',NULL,'https://www.simplyrecipes.com/thmb/ZOXgJKuuMMYQGUJ8Co1eooL37tw=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Simply-Recipes-Perfect-Lemonade-LEAD-06-B-a488322e63604cd6a1442de661722553.jpg'),(122,NULL,'Mango Lassi 1',NULL,'https://shivanilovesfood.com/wp-content/uploads/2023/03/Healthy-Mango-Lassi-7.jpg'),(123,NULL,'Mango Lassi 2',NULL,'https://minimalistbaker.com/wp-content/uploads/2020/05/Mango-Lassi-Smoothie-SQUARE.jpg'),(124,NULL,'Green Tea 1',NULL,'https://domf5oio6qrcr.cloudfront.net/medialibrary/8468/conversions/Tea-thumb.jpg'),(125,NULL,'Green Tea 2',NULL,'https://assets.epicurious.com/photos/5887d21b5f76684c78cf57db/16:9/w_2560%2Cc_limit/green_tea_24012017.jpg'),(126,NULL,'Green Tea 3',NULL,'https://static.toiimg.com/thumb/imgsize-23456,msid-121996789,width-600,resizemode-4/765u6g.jpg'),(127,NULL,'Passion Fruit Juice 1',NULL,'https://www.thevgnway.com/wp-content/uploads/2023/07/DB57498B-B1AD-48B7-9D20-113434B950C9.jpeg'),(128,NULL,'Passion Fruit Juice 2',NULL,'https://media.istockphoto.com/id/1608041307/photo/refreshing-passion-fruit-drink-with-mint-and-vodka.jpg?s=612x612&w=0&k=20&c=8ym0omuy83kxeSvqAtrv8qUWFaHpvMv2j7d1P2Li1L8='),(129,NULL,'Passion Fruit Juice 3',NULL,'https://emilylaurae.com/wp-content/uploads/2022/08/passion-fruit-juice-2.jpg'),(130,'2025-12-17 12:31:45.130219',NULL,'2025-12-17 12:31:45.130219','https://res.cloudinary.com/delsqnlsu/image/upload/v1765949503/products/p7mf26jlf8c63n7c9bac.png'),(134,'2025-12-17 12:39:04.004543',NULL,'2025-12-17 12:39:04.004543','https://res.cloudinary.com/delsqnlsu/image/upload/v1765949941/products/lf2mqegofensjg0yix7x.png'),(136,'2025-12-17 12:40:29.695312',NULL,'2025-12-17 12:40:29.695312','https://res.cloudinary.com/delsqnlsu/image/upload/v1765950027/products/iqkzyqkdjqpo1zsvckvv.png'),(137,'2025-12-17 17:51:08.000000','Img_Appetizers','2025-12-17 17:51:08.000000','https://images.unsplash.com/photo-1541529086526-db283c563270?w=400'),(138,'2025-12-17 17:51:08.000000','Img_MainCourse','2025-12-17 17:51:08.000000','https://images.unsplash.com/photo-1544025162-d76694265947?w=400'),(139,'2025-12-17 17:51:08.000000','Img_Desserts','2025-12-17 17:51:08.000000','https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400'),(140,'2025-12-17 17:51:08.000000','Img_Beverages','2025-12-17 17:51:08.000000','https://voca-land.sgp1.cdn.digitaloceanspaces.com/-1/1635862845034/2020-trends-to-watch-in-US-beverage.jpeg'),(141,'2025-12-17 17:51:08.000000','Img_Seafood','2025-12-17 17:51:08.000000','https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400'),(142,'2025-12-17 17:51:08.000000','Img_Pasta','2025-12-17 17:51:08.000000','https://images.unsplash.com/photo-1473093226795-af9932fe5856?w=400'),(143,'2025-12-17 17:51:08.000000','Img_Salads','2025-12-17 17:51:08.000000','https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400'),(144,'2025-12-17 17:51:08.000000','Img_Burgers','2025-12-17 17:51:08.000000','https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400'),(145,'2025-12-17 17:51:08.000000','Img_Starter','2025-12-17 17:51:08.000000','https://images.immediate.co.uk/production/volatile/sites/30/2024/03/Jamon-and-wild-garlic-croquetas-50f2d2f.jpg'),(146,'2025-12-17 17:51:08.000000','Img_Drink','2025-12-17 17:51:08.000000','https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=400'),(147,'2025-12-17 17:54:03.000000','Img_Combo_Family','2025-12-17 17:54:03.000000','https://images.unsplash.com/photo-1547573854-74d2a71d0826?w=800'),(148,'2025-12-17 17:54:03.000000','Img_Combo_Couple','2025-12-17 17:54:03.000000','https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800'),(149,'2025-12-17 17:54:03.000000','Img_Combo_Healthy','2025-12-17 17:54:03.000000','https://images.unsplash.com/photo-1543339308-43e59d6b73a6?w=800');
/*!40000 ALTER TABLE `images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `momo_payments`
--

DROP TABLE IF EXISTS `momo_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `momo_payments` (
  `request_id` bigint DEFAULT NULL,
  `result_code` int DEFAULT NULL,
  `transaction_id` bigint DEFAULT NULL,
  `id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FKq2cced778rnsem3yhc7mk5ihl` FOREIGN KEY (`id`) REFERENCES `payments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `momo_payments`
--

LOCK TABLES `momo_payments` WRITE;
/*!40000 ALTER TABLE `momo_payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `momo_payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification_read_status`
--

DROP TABLE IF EXISTS `notification_read_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification_read_status` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `status` enum('DELETED','READ','UNREAD') NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `notification_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UKnr3mk9n4ciss0ctnb6va2ocss` (`notification_id`,`user_id`),
  KEY `FKj6blgxfciweykabjg3ox9o5u5` (`user_id`),
  CONSTRAINT `FK8ipersthumeeb5lh26l6fer5w` FOREIGN KEY (`notification_id`) REFERENCES `user_notifications` (`id`),
  CONSTRAINT `FKj6blgxfciweykabjg3ox9o5u5` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification_read_status`
--


--
-- Table structure for table `order_at_table`
--

DROP TABLE IF EXISTS `order_at_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_at_table` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `table_id` bigint NOT NULL,
  `status` enum('CANCELED','COMPLETED','CONFIRMED','DELIVERED','PENDING','SHIPPING','WAITING_FOR_PAYMENT') NOT NULL,
  `total_price` double DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `payment_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK76p9jxxafp1u52jxgxjpbwjrh` (`payment_id`),
  KEY `FKinh6kc2vjwfx5n9t4ggd1mrk3` (`table_id`),
  CONSTRAINT `FKinh6kc2vjwfx5n9t4ggd1mrk3` FOREIGN KEY (`table_id`) REFERENCES `tables` (`id`),
  CONSTRAINT `FKmuxfj6fth4v79whrlv7fd0pxa` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_at_table`
--


--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `price` double DEFAULT NULL,
  `quantity` bigint DEFAULT NULL,
  `reviewed` bit(1) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `combo_id` bigint DEFAULT NULL,
  `order_id` bigint DEFAULT NULL,
  `order_at_table_id` bigint DEFAULT NULL,
  `place_table_id` bigint DEFAULT NULL,
  `product_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK406a8m2k9pylvb0rynoxx4o43` (`combo_id`),
  KEY `FKbioxgbv59vetrxe0ejfubep1w` (`order_id`),
  KEY `FKqx5wmin9v5qo90p15xnrm6y1j` (`order_at_table_id`),
  KEY `FK7ouhlrhmrubycbrcxg13d0j86` (`place_table_id`),
  KEY `FKocimc7dtr037rh4ls4l95nlfi` (`product_id`),
  CONSTRAINT `FK406a8m2k9pylvb0rynoxx4o43` FOREIGN KEY (`combo_id`) REFERENCES `combos` (`id`),
  CONSTRAINT `FK7ouhlrhmrubycbrcxg13d0j86` FOREIGN KEY (`place_table_id`) REFERENCES `place_table_customers` (`id`),
  CONSTRAINT `FKbioxgbv59vetrxe0ejfubep1w` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `FKocimc7dtr037rh4ls4l95nlfi` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `FKqx5wmin9v5qo90p15xnrm6y1j` FOREIGN KEY (`order_at_table_id`) REFERENCES `order_at_table` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `discount_amount` double DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `district` varchar(255) DEFAULT NULL,
  `is_default` bit(1) DEFAULT NULL,
  `province` varchar(255) DEFAULT NULL,
  `receiver_name` varchar(255) DEFAULT NULL,
  `receiver_phone` varchar(255) DEFAULT NULL,
  `ward` varchar(255) DEFAULT NULL,
  `shipping_fee` double DEFAULT NULL,
  `status` enum('CANCELED','COMPLETED','CONFIRMED','DELIVERED','PENDING','SHIPPING','WAITING_FOR_PAYMENT') DEFAULT NULL,
  `total_price` double DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `vat` double DEFAULT NULL,
  `payment_id` bigint DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  `voucher_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK8aol9f99s97mtyhij0tvfj41f` (`payment_id`),
  KEY `FK32ql8ubntj5uh44ph9659tiih` (`user_id`),
  KEY `FKdimvsocblb17f45ikjr6xn1wj` (`voucher_id`),
  CONSTRAINT `FK32ql8ubntj5uh44ph9659tiih` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `FK8aol9f99s97mtyhij0tvfj41f` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`),
  CONSTRAINT `FKdimvsocblb17f45ikjr6xn1wj` FOREIGN KEY (`voucher_id`) REFERENCES `vouchers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--


--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount` double DEFAULT NULL,
  `payment_date` datetime(6) DEFAULT NULL,
  `payment_info` varchar(255) DEFAULT NULL,
  `payment_message` varchar(255) DEFAULT NULL,
  `payment_method` enum('COD','MOMO') DEFAULT NULL,
  `status` enum('CANCELED','FAIL','PAID','PROCESSING','REFUND') DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--


--
-- Table structure for table `place_table_customers`
--

DROP TABLE IF EXISTS `place_table_customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `place_table_customers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `member` int DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `phone_number` varchar(20) NOT NULL,
  `started_at` datetime(6) DEFAULT NULL,
  `status` enum('COMPLETED','CONFIRMED','DENIED','PENDING') DEFAULT NULL,
  `total_price` double DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `payment_id` bigint DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK7hfradinnee6rf8tnnga875ry` (`payment_id`),
  KEY `FKt2k8rur3q6rg20d8ntdvw4t79` (`user_id`),
  CONSTRAINT `FKfr5q2q8wx9mi7xptwp5p6w4gq` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`),
  CONSTRAINT `FKt2k8rur3q6rg20d8ntdvw4t79` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `place_table_customers`
--


--
-- Table structure for table `place_table_guests`
--

DROP TABLE IF EXISTS `place_table_guests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `place_table_guests` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `fullname` varchar(100) NOT NULL,
  `member_int` int NOT NULL,
  `note` varchar(500) DEFAULT NULL,
  `phone_number` varchar(20) NOT NULL,
  `started_at` datetime(6) NOT NULL,
  `status` enum('COMPLETED','CONFIRMED','DENIED','PENDING') NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `place_table_guests`
--


--
-- Table structure for table `product_images`
--

DROP TABLE IF EXISTS `product_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_images` (
  `id` bigint NOT NULL,
  `product_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKqnq71xsohugpqwf3c9gxmsuy` (`product_id`),
  CONSTRAINT `FKhf6x81rw90r56j8wohrrnd63p` FOREIGN KEY (`id`) REFERENCES `images` (`id`),
  CONSTRAINT `FKqnq71xsohugpqwf3c9gxmsuy` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_images`
--

LOCK TABLES `product_images` WRITE;
/*!40000 ALTER TABLE `product_images` DISABLE KEYS */;
INSERT INTO `product_images` VALUES (1,1),(2,1),(3,1),(4,2),(5,2),(6,2),(8,3),(9,3),(10,4),(11,4),(12,4),(13,5),(14,5),(15,5),(16,5),(17,6),(18,6),(20,7),(21,7),(22,8),(25,8),(26,9),(28,9),(29,10),(30,10),(33,11),(34,11),(36,12),(37,13),(38,13),(39,13),(40,14),(41,14),(43,14),(44,15),(45,15),(48,16),(49,17),(50,17),(51,17),(52,17),(53,18),(54,18),(55,18),(57,19),(58,20),(59,20),(62,21),(63,21),(64,21),(66,22),(67,23),(70,23),(71,24),(73,24),(74,25),(79,26),(80,27),(81,27),(84,28),(85,28),(87,29),(88,29),(89,30),(90,30),(91,30),(93,31),(94,31),(95,31),(109,32),(110,32),(111,32),(112,33),(113,33),(114,34),(115,34),(116,34),(117,35),(118,35),(119,36),(120,36),(121,36),(122,37),(123,37),(124,38),(125,38),(126,38),(127,39),(128,39),(129,39);
/*!40000 ALTER TABLE `product_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_tags`
--

DROP TABLE IF EXISTS `product_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_tags` (
  `product_id` bigint NOT NULL,
  `tag_id` bigint NOT NULL,
  PRIMARY KEY (`product_id`,`tag_id`),
  KEY `FKpur2885qb9ae6fiquu77tcv1o` (`tag_id`),
  CONSTRAINT `FK5rk6s19k3risy7q7wqdr41uss` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `FKpur2885qb9ae6fiquu77tcv1o` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_tags`
--

LOCK TABLES `product_tags` WRITE;
/*!40000 ALTER TABLE `product_tags` DISABLE KEYS */;
INSERT INTO `product_tags` VALUES (2,1),(20,2),(1,3),(1,4),(9,5),(12,5),(5,6),(2,7),(5,8);
/*!40000 ALTER TABLE `product_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `description` varchar(2000) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `price` double DEFAULT NULL,
  `status` enum('AVAILABLE','DELETED','UNAVAILABLE') DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `category_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKog2rp4qthbtt2lfyhfo32lsw9` (`category_id`),
  CONSTRAINT `FKog2rp4qthbtt2lfyhfo32lsw9` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,NULL,'Fresh romaine lettuce, crispy croutons, parmesan cheese, and classic Caesar dressing','Caesar Salad',8.99,'UNAVAILABLE','2025-12-27 21:42:56.996400',1),(2,NULL,'Crispy fried chicken wings tossed in your choice of buffalo, BBQ, or honey garlic sauce','Chicken Wings',12.99,'AVAILABLE',NULL,1),(3,NULL,'Golden fried mozzarella cheese served with marinara sauce','Mozzarella Sticks',7.99,'AVAILABLE',NULL,1),(4,NULL,'Toasted Italian bread topped with fresh tomatoes, basil, garlic, and olive oil','Bruschetta',9.99,'AVAILABLE',NULL,1),(5,NULL,'Premium 12oz ribeye steak grilled to perfection, served with roasted vegetables and mashed potatoes','Grilled Ribeye Steak',29.99,'AVAILABLE',NULL,2),(6,NULL,'Tender pork ribs slow-cooked and glazed with our signature BBQ sauce, served with coleslaw and fries','BBQ Ribs',24.99,'AVAILABLE',NULL,2),(7,NULL,'Herb-roasted half chicken with crispy skin, served with seasonal vegetables and rice','Roasted Chicken',18.99,'AVAILABLE',NULL,2),(8,NULL,'Grilled lamb chops with rosemary and garlic, served with mint sauce and roasted potatoes','Lamb Chops',32.99,'AVAILABLE',NULL,2),(9,NULL,'Fresh Atlantic salmon fillet with lemon butter sauce, served with asparagus and quinoa','Grilled Salmon',26.99,'AVAILABLE',NULL,5),(10,NULL,'Succulent shrimp sautéed in garlic butter and white wine, served over linguine','Shrimp Scampi',22.99,'AVAILABLE',NULL,5),(11,NULL,'Beer-battered cod fillet served with crispy fries, tartar sauce, and coleslaw','Fish and Chips',16.99,'AVAILABLE',NULL,5),(12,NULL,'Grilled lobster tail with drawn butter, served with corn on the cob and garlic bread','Lobster Tail',38.99,'AVAILABLE',NULL,5),(13,NULL,'Classic Italian pasta with pancetta, eggs, parmesan, and black pepper','Spaghetti Carbonara',15.99,'AVAILABLE',NULL,6),(14,NULL,'Creamy alfredo sauce tossed with fettuccine pasta and topped with parmesan','Fettuccine Alfredo',14.99,'AVAILABLE',NULL,6),(15,NULL,'Layers of pasta, meat sauce, béchamel, and melted cheese baked to perfection','Lasagna Bolognese',17.99,'AVAILABLE',NULL,6),(16,NULL,'Spicy tomato sauce with garlic and red chili peppers tossed with penne pasta','Penne Arrabbiata',13.99,'AVAILABLE',NULL,6),(17,NULL,'Juicy beef patty with cheddar cheese, lettuce, tomato, onion, and pickles on a toasted bun','Classic Cheeseburger',13.99,'AVAILABLE',NULL,8),(18,NULL,'Premium beef burger topped with crispy bacon, cheddar cheese, and BBQ sauce','Bacon Burger',15.99,'AVAILABLE',NULL,8),(19,NULL,'Grilled burger with sautéed mushrooms and melted Swiss cheese','Mushroom Swiss Burger',14.99,'AVAILABLE',NULL,8),(20,NULL,'House-made veggie patty with avocado, sprouts, and chipotle mayo','Veggie Burger',12.99,'AVAILABLE',NULL,8),(21,NULL,'Fresh vegetables, feta cheese, olives, and oregano with olive oil dressing','Greek Salad',10.99,'AVAILABLE',NULL,7),(22,NULL,'Mixed greens with grilled chicken, bacon, avocado, eggs, and blue cheese','Cobb Salad',13.99,'AVAILABLE',NULL,7),(23,NULL,'Fresh mozzarella, tomatoes, and basil with balsamic glaze','Caprese Salad',11.99,'AVAILABLE',NULL,7),(24,NULL,'Warm chocolate cake with a molten center, served with vanilla ice cream','Chocolate Lava Cake',8.99,'AVAILABLE',NULL,3),(25,NULL,'Classic Italian dessert with layers of coffee-soaked ladyfingers and mascarpone cream','Tiramisu',7.99,'AVAILABLE',NULL,3),(26,NULL,'New York style cheesecake with graham cracker crust and berry compote','Cheesecake',8.49,'AVAILABLE',NULL,3),(27,NULL,'Homemade apple pie with cinnamon and served warm with vanilla ice cream','Apple Pie',7.49,'AVAILABLE',NULL,3),(28,NULL,'Freshly squeezed orange juice','Fresh Orange Juice',4.99,'AVAILABLE',NULL,4),(29,NULL,'Cold brew coffee served over ice with milk','Iced Coffee',4.49,'AVAILABLE',NULL,4),(30,NULL,'Refreshing mint cocktail with rum, lime, sugar, and soda water','Mojito',9.99,'AVAILABLE',NULL,4),(31,NULL,'Blended strawberries, banana, yogurt, and honey','Strawberry Smoothie',6.99,'AVAILABLE',NULL,4),(32,NULL,'Crispy Vietnamese spring rolls filled with vegetables and pork, served with sweet chili sauce','Spring Rolls',9.99,'AVAILABLE',NULL,9),(33,NULL,'Tender calamari rings lightly breaded and fried, served with spicy aioli and lemon wedges','Fried Calamari',11.99,'AVAILABLE',NULL,9),(34,NULL,'Button mushrooms stuffed with cream cheese, garlic, herbs and breadcrumbs, baked until golden','Stuffed Mushrooms',10.49,'AVAILABLE',NULL,9),(35,NULL,'Succulent prawns served on a bed of crisp lettuce with Marie Rose sauce and lemon','Prawn Cocktail',12.49,'AVAILABLE',NULL,9),(36,NULL,'Freshly squeezed lemon juice with sparkling water and a touch of honey','Lemonade',5.49,'AVAILABLE',NULL,10),(37,NULL,'Traditional Indian drink made with mango, yogurt, and cardamom','Mango Lassi',6.49,'AVAILABLE',NULL,10),(38,NULL,'Premium Japanese green tea served hot or iced','Green Tea',3.99,'AVAILABLE',NULL,10),(39,NULL,'Refreshing tropical passion fruit juice with pulp','Passion Fruit Juice',5.99,'AVAILABLE',NULL,10);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `refresh_tokens`
--

DROP TABLE IF EXISTS `refresh_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `refresh_tokens` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `expiry_date` datetime(6) NOT NULL,
  `revoked` bit(1) NOT NULL,
  `token` varchar(255) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UKghpmfn23vmxfu3spu3lfg4r2d` (`token`),
  KEY `FK1lih5y2npsf8u5o3vhdb9y0os` (`user_id`),
  CONSTRAINT `FK1lih5y2npsf8u5o3vhdb9y0os` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `refresh_tokens`
--

--
-- Table structure for table `review_images`
--

DROP TABLE IF EXISTS `review_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `review_images` (
  `id` bigint NOT NULL,
  `review_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK3aayo5bjciyemf3bvvt987hkr` (`review_id`),
  CONSTRAINT `FK3aayo5bjciyemf3bvvt987hkr` FOREIGN KEY (`review_id`) REFERENCES `reviews` (`id`),
  CONSTRAINT `FKrfnwjx1lk61xgwd0pwy9s3gsr` FOREIGN KEY (`id`) REFERENCES `images` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `review_images`
--

LOCK TABLES `review_images` WRITE;
/*!40000 ALTER TABLE `review_images` DISABLE KEYS */;
/*!40000 ALTER TABLE `review_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `content` varchar(2000) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `rate` double DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `order_item_id` bigint DEFAULT NULL,
  `product_id` bigint DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK96f6ovfc9wn4579incehx4gra` (`order_item_id`),
  KEY `FKpl51cejpw4gy5swfar8br9ngi` (`product_id`),
  KEY `FKcgy7qjc1r99dp117y9en6lxye` (`user_id`),
  CONSTRAINT `FK2x2x74lnliqmt91bc1w95ll8n` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`id`),
  CONSTRAINT `FKcgy7qjc1r99dp117y9en6lxye` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `FKpl51cejpw4gy5swfar8br9ngi` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tables`
--

DROP TABLE IF EXISTS `tables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tables` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `qr` varchar(255) DEFAULT NULL,
  `seat` int DEFAULT NULL,
  `table_number` varchar(255) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tables`
--


--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tags` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UKt48xdq560gs3gap9g7jg36kgc` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES (1,'2025-12-17 17:51:08.000000','Món ăn có vị cay nồng, kích thích vị giác','Spicy','2025-12-17 17:51:08.000000'),(2,'2025-12-17 17:51:08.000000','Món ăn thuần thực vật, phù hợp cho người ăn chay','Vegetarian','2025-12-17 17:51:08.000000'),(3,'2025-12-17 17:51:08.000000','Sản phẩm được khách hàng yêu thích nhất','Best Seller','2025-12-17 17:51:08.000000'),(4,'2025-12-17 17:51:08.000000','Món ăn giàu dinh dưỡng, ít calo','Healthy','2025-12-17 17:51:08.000000'),(5,'2025-12-17 17:51:08.000000','Món mới vừa được thêm vào thực đơn','New','2025-12-17 17:51:08.000000'),(6,'2025-12-17 17:51:08.000000','Món ăn mang phong cách riêng đặc biệt của nhà hàng','Signature','2025-12-17 17:51:08.000000'),(7,'2025-12-17 17:51:08.000000','Món ăn được chế biến phù hợp cho khẩu vị trẻ nhỏ','Kids Friendly','2025-12-17 17:51:08.000000'),(8,'2025-12-17 17:51:08.000000','Món ăn do chính bếp trưởng đề xuất','Chef Recommendation','2025-12-17 17:51:08.000000');
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_notifications`
--

DROP TABLE IF EXISTS `user_notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_notifications` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `content` varchar(2000) DEFAULT NULL,
  `is_global` bit(1) NOT NULL,
  `sent_at` datetime(6) DEFAULT NULL,
  `status` enum('DELETED','READ','UNREAD') DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK9f86wonnl11hos1cuf5fibutl` (`user_id`),
  CONSTRAINT `FK9f86wonnl11hos1cuf5fibutl` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_notifications`
--


--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `role` varchar(31) NOT NULL,
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `email` varchar(255) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `gender` enum('FEMALE','MALE','OTHER') DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `phone_number` varchar(255) DEFAULT NULL,
  `status` enum('ACTIVE','DELETED','INACTIVE','SUSPENDED') NOT NULL,
  `total_spent` double DEFAULT NULL,
  `avatar_id` bigint DEFAULT NULL,
  `default_address_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK6dotkott2kjsp8vw4d0m25fb7` (`email`),
  UNIQUE KEY `UK9q63snka3mdh91as4io72espi` (`phone_number`),
  UNIQUE KEY `UKrsulcn2gynjy3cddpwmosv881` (`avatar_id`),
  UNIQUE KEY `UKfrcgyn274s2b8mlsyogj68k84` (`default_address_id`),
  CONSTRAINT `FK2lttmx8vn9eecykig5sch3v0h` FOREIGN KEY (`avatar_id`) REFERENCES `images` (`id`),
  CONSTRAINT `FK87ccnpkij6d1sorog5li3sq8x` FOREIGN KEY (`default_address_id`) REFERENCES `addresses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--


--
-- Table structure for table `vnpay_payments`
--

DROP TABLE IF EXISTS `vnpay_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vnpay_payments` (
  `bank` varchar(255) DEFAULT NULL,
  `transaction_number` varchar(255) DEFAULT NULL,
  `vnp_response_code` varchar(255) DEFAULT NULL,
  `id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK9gm229846930irfpjkwk992nh` FOREIGN KEY (`id`) REFERENCES `payments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vnpay_payments`
--

LOCK TABLES `vnpay_payments` WRITE;
/*!40000 ALTER TABLE `vnpay_payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `vnpay_payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voucher_usages`
--

DROP TABLE IF EXISTS `voucher_usages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voucher_usages` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `discount_amount` double DEFAULT NULL,
  `used_at` datetime(6) DEFAULT NULL,
  `order_id` bigint DEFAULT NULL,
  `user_id` bigint NOT NULL,
  `voucher_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UKp6oa0unmdk69fka8d97jsvwqm` (`order_id`),
  KEY `FKayocv8v53p94c3jr2ookjd4jq` (`user_id`),
  KEY `FKguvf95urdn2namu0hgiasgttx` (`voucher_id`),
  CONSTRAINT `FKayocv8v53p94c3jr2ookjd4jq` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `FKc6ctsyf63q19vkjb6k3lrecev` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `FKguvf95urdn2namu0hgiasgttx` FOREIGN KEY (`voucher_id`) REFERENCES `vouchers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voucher_usages`
--

LOCK TABLES `voucher_usages` WRITE;
/*!40000 ALTER TABLE `voucher_usages` DISABLE KEYS */;
/*!40000 ALTER TABLE `voucher_usages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vouchers`
--

DROP TABLE IF EXISTS `vouchers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vouchers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `discount_value` double NOT NULL,
  `end_date` datetime(6) NOT NULL,
  `is_public` bit(1) DEFAULT NULL,
  `max_discount_amount` double DEFAULT NULL,
  `min_order_value` double DEFAULT NULL,
  `name` varchar(200) NOT NULL,
  `start_date` datetime(6) NOT NULL,
  `status` enum('ACTIVE','EXPIRED','INACTIVE') NOT NULL,
  `type` enum('FIXED_AMOUNT','FREE_SHIPPING','PERCENTAGE') NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `usage_limit` int NOT NULL,
  `usage_limit_per_user` int DEFAULT NULL,
  `used_count` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK30ftp2biebbvpik8e49wlmady` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vouchers`
--

LOCK TABLES `vouchers` WRITE;
/*!40000 ALTER TABLE `vouchers` DISABLE KEYS */;
INSERT INTO `vouchers` VALUES (1,'WELCOME10','2025-12-17 18:44:46.000000','Get 10% off your first order. Valid for orders over $30',10,'2026-12-31 23:59:59.000000',_binary '',15,30,'Welcome New Customer','2025-12-01 00:00:00.000000','ACTIVE','PERCENTAGE','2025-12-17 18:44:46.000000',1000,1,0),(2,'HOLIDAY25','2025-12-17 18:44:46.000000','Enjoy 25% off during holiday season. Maximum discount $50',25,'2026-01-15 23:59:59.000000',_binary '',50,50,'Holiday Season Sale','2025-12-15 00:00:00.000000','ACTIVE','PERCENTAGE','2025-12-17 18:44:46.000000',500,3,0),(3,'BIGORDER15','2025-12-17 18:44:46.000000','Save 15% on orders over $120. Max discount $40',15,'2026-06-30 23:59:59.000000',_binary '',40,120,'Big Order Discount','2025-12-01 00:00:00.000000','ACTIVE','PERCENTAGE','2025-12-17 18:44:46.000000',300,5,0),(4,'SAVE10','2025-12-17 18:44:46.000000','Get $10 off on orders over $80',10,'2026-03-31 23:59:59.000000',_binary '',NULL,80,'Save $10 Discount','2025-12-01 00:00:00.000000','ACTIVE','FIXED_AMOUNT','2025-12-17 18:44:46.000000',200,2,0),(5,'MEGA25','2025-12-17 18:44:46.000000','Save $25 on orders over $200. Special promotion!',25,'2026-01-31 23:59:59.000000',_binary '',NULL,200,'Mega Discount $25','2025-12-10 00:00:00.000000','ACTIVE','FIXED_AMOUNT','2025-12-17 18:44:46.000000',100,1,0),(6,'HAPPY5','2025-12-17 18:44:46.000000','Instant $5 off for orders over $40',5,'2026-12-31 23:59:59.000000',_binary '',NULL,40,'Happy Day $5 Off','2025-12-01 00:00:00.000000','ACTIVE','FIXED_AMOUNT','2025-12-17 18:44:46.000000',500,3,0),(7,'FREESHIP','2025-12-17 18:44:46.000000','Free shipping for orders over $35',0,'2026-12-31 23:59:59.000000',_binary '',10,35,'Free Shipping Voucher','2025-12-01 00:00:00.000000','ACTIVE','FREE_SHIPPING','2025-12-17 18:44:46.000000',1000,NULL,0),(8,'SHIPFREE20','2025-12-17 18:44:46.000000','Free shipping on all orders over $20',0,'2026-02-28 23:59:59.000000',_binary '',8,20,'Free Ship For All','2025-12-15 00:00:00.000000','ACTIVE','FREE_SHIPPING','2025-12-17 18:44:46.000000',800,5,0),(9,'VIP50PERCENT','2025-12-17 18:44:46.000000','Exclusive 50% off for VIP customers. Max discount $120',50,'2026-12-31 23:59:59.000000',_binary '\0',120,100,'VIP Customer Exclusive','2025-12-01 00:00:00.000000','ACTIVE','PERCENTAGE','2025-12-17 18:44:46.000000',50,2,0),(10,'VIPFREE50','2025-12-17 18:44:46.000000','Get $50 off for VIP members. Minimum order $150',50,'2026-06-30 23:59:59.000000',_binary '\0',NULL,150,'VIP Fixed Discount','2025-12-01 00:00:00.000000','ACTIVE','FIXED_AMOUNT','2025-12-17 18:44:46.000000',30,1,0),(11,'EXPIRED20','2025-11-01 00:00:00.000000','This voucher has expired',20,'2025-11-30 23:59:59.000000',_binary '',20,25,'Expired Sale Event','2025-11-01 00:00:00.000000','EXPIRED','PERCENTAGE','2025-12-01 00:00:00.000000',100,2,45),(12,'INACTIVE15','2025-12-17 18:44:46.000000','Temporarily inactive voucher',15,'2026-06-30 23:59:59.000000',_binary '\0',18,35,'Inactive Promotion','2025-12-01 00:00:00.000000','ACTIVE','PERCENTAGE','2025-12-17 20:59:45.424948',200,3,0),(13,'WEEKEND20','2025-12-17 18:44:46.000000','Get 20% off on weekend orders over $60',20,'2026-03-31 23:59:59.000000',_binary '',30,60,'Weekend Special','2025-12-20 00:00:00.000000','ACTIVE','PERCENTAGE','2025-12-17 20:59:46.718120',400,2,0),(14,'COMBO7','2025-12-17 18:44:46.000000','Save $7 on combo meals. Valid for orders over $45',7,'2026-12-31 23:59:59.000000',_binary '\0',NULL,45,'Combo Meal Discount','2025-12-01 00:00:00.000000','INACTIVE','FIXED_AMOUNT','2025-12-17 21:02:35.490438',600,4,0),(15,'BDAY12','2025-12-17 18:44:46.000000','Birthday special: $12 off on orders over $55',12,'2026-12-31 23:59:59.000000',_binary '',NULL,55,'Birthday Special Gift','2025-12-01 00:00:00.000000','ACTIVE','FIXED_AMOUNT','2025-12-17 21:01:56.759101',365,1,0);
/*!40000 ALTER TABLE `vouchers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlist_items`
--

DROP TABLE IF EXISTS `wishlist_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishlist_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `product_id` bigint NOT NULL,
  `wishlist_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FKqxj7lncd242b59fb78rqegyxj` (`product_id`),
  KEY `FKkem9l8vd14pk3cc4elnpl0n00` (`wishlist_id`),
  CONSTRAINT `FKkem9l8vd14pk3cc4elnpl0n00` FOREIGN KEY (`wishlist_id`) REFERENCES `wishlists` (`id`),
  CONSTRAINT `FKqxj7lncd242b59fb78rqegyxj` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlist_items`
--

LOCK TABLES `wishlist_items` WRITE;
/*!40000 ALTER TABLE `wishlist_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `wishlist_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlists`
--

DROP TABLE IF EXISTS `wishlists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishlists` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UKobh8c909a28dx3aqh4cbdhh25` (`user_id`),
  CONSTRAINT `FK330pyw2el06fn5g28ypyljt16` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlists`
--

LOCK TABLES `wishlists` WRITE;
/*!40000 ALTER TABLE `wishlists` DISABLE KEYS */;
/*!40000 ALTER TABLE `wishlists` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'siupo_db'
--

--
-- Dumping routines for database 'siupo_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-27 22:34:10