create database shop;

use shop;

ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'admin';
FLUSH PRIVILEGES;

CREATE TABLE `product` (
 `id` int unsigned NOT NULL AUTO_INCREMENT,
 `name` varchar(255) NOT NULL,
 `code` varchar(255) NOT NULL,
 `image` text NOT NULL,
 `price` double NOT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;

CREATE TABLE users (
	userid varchar(255) NOT NULL,
    pass varchar(255) NOT NULL,
    PRIMARY KEY (userid)
);

CREATE TABLE admins (
	userid varchar(255) NOT NULL,
    pass varchar(255) NOT NULL,
    PRIMARY KEY (userid)
);

INSERT INTO users VALUES ('bratk9','290799');
INSERT INTO users VALUES ('hpeonix','110399');
INSERT INTO users VALUES ('roja','210500');

INSERT INTO admins VALUES ('admin1','default');
INSERT INTO admins VALUES ('admin2','default');

INSERT INTO `product` (`id`, `name`, `code`, `image`, `price`) VALUES
(1, 'Deeane London Woman\'s Wedges', 'DLW01', 'shoes/1.jpg', 799.00),
(2, 'Hush Puppies Men\'s Fuel Derby Formal Shoes', 'HPM02', 'shoes/2.jpg', 2950.00),
(3, 'Nike Men\'s Flex Contact 3 Running Shoes', 'NMF03', 'shoes/3.jpg', 3399.00),
(4, 'Nike Women\'s Quest Running Shoes', 'NWQ04', 'shoes/4.jpg', 3999.00),
(5, 'Puma Men\'s Movemax Running Shoes', 'PMM05', 'shoes/5.jpg', 1999.00),
(6, 'Skechers Women\'s Go Walk Walking Shoes', 'SWG06', 'shoes/6.jpg', 4299.00)