create database shop;

use shop;



CREATE TABLE product (
 id int unsigned NOT NULL AUTO_INCREMENT,
 itemname varchar(255) NOT NULL,
 image text NOT NULL,
 price double NOT NULL,
 PRIMARY KEY (id)
);


create table orderlist(
oid int unsigned not null auto_increment,
sid int unsigned not null,
iid int unsigned not null,
quantity int unsigned,
trackStatus int unsigned default(0),
primary key(oid)
);

create table shopper(
id int unsigned not null auto_increment,
username varchar(255) not null unique,
pword varchar(255) not null,
is_admin bool not null default(false),
primary key(id,username)
);

INSERT INTO `product` ( `itemname`, `image`, `price`) VALUES
( 'Deeane London Woman\'s Wedges', 'shoes/1.jpg', 799.00),
( 'Hush Puppies Men\'s Fuel Derby Formal Shoes', 'shoes/2.jpg', 2950.00),
( 'Nike Men\'s Flex Contact 3 Running Shoes', 'shoes/3.jpg', 3399.00),
( 'Nike Women\'s Quest Running Shoes', 'shoes/4.jpg', 3999.00),
( 'Puma Men\'s Movemax Running Shoes', 'shoes/5.jpg', 1999.00),
('Skechers Women\'s Go Walk Walking Shoes', 'shoes/6.jpg', 4299.00);

ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH PRIVILEGES;