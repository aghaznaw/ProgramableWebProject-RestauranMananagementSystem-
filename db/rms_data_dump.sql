BEGIN TRANSACTION;
CREATE TABLE vendor(vendorId INTEGER  PRIMARY KEY AUTOINCREMENT,
		Name TEXT,
		address TEXT,
		email TEXt,
		phone TEXT
);
INSERT INTO `vendor` (vendorId,Name,address,email,phone) VALUES (1,'Prisma','Linnanma, Oulu, Finland','prisma.linnan@prisma.fi','04332255'),
 (2,'prisma','Jyvasentie 1, Jyvaskyla, Finland','prisma.jyvas@prisma.fi','044665555'),
 (3,'lidl','Salmirannantie 8, Jyvaskyla, Finland','lidl.jvas33@lidl.fi','044555544'),
 (4,'K SuperMareket','Linnanma, Oulu, Finland','ksupermarket@ksupermarket.fi','0455665555'),
 (5,'Presma','Salmirannantie 8, Jyvaskyla, Finland','presma','04665588665');
CREATE TABLE `user` (
	`userId`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`firstname`	TEXT,
	`lastname`	TEXT,
	`username`	TEXT,
	`email`	TEXT,
	`password`	TEXT,
	`phone`	TEXT,
	`dob`	TEXT
);
INSERT INTO `user` (userId,firstname,lastname,username,email,password,phone,dob) VALUES (1,'Ahmad','Ghaznawi','ahmad','ahamd.g@gmail.com','1234','0455566855','24-04-1989'),
 (2,'dat','le','datle','dat.le@gmail.com','2322','0456685558','02-03-1988'),
 (3,'andy','arulu','andyarulu','andy.arulu@gmail.com','45522','0455566555','01-05-1983'),
 (4,'shazi','xihin','shazixihin','shazi.xihin@gmail.com','jdijgy','011225546','05-01-1995');
CREATE TABLE `stock` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`price`	REAL,
	`quantity`	INTEGER,
	`quantityInStock`	INTEGER,
	`expireDate`	TEXT,
	`date`	TEXT,
	`transactionType`	TEXT,
	`vendorId`	INTEGER,
	`itemId`	INTEGER,
	`restaurantId`	INTEGER,
	`userId`	INTEGER,
	FOREIGN KEY(vendorId) references vendor(vendorId) ON DELETE CASCADE,
	FOREIGN KEY(itemId) references item(itemId) ON DELETE CASCADE,
	FOREIGN KEY(restaurantId) references restaurant(restaurantId) ON DELETE CASCADE,
	FOREIGN KEY(userId) references user(userId) ON DELETE CASCADE
);
INSERT INTO `stock` (id,price,quantity,quantityInStock,expireDate,date,transactionType,vendorId,itemId,restaurantId,userId) VALUES (1,2.79,20,20,'30-02-2018','20-02-2018','input',1,1,1,1),
 (2,3.2,10,10,'30-03-2019','20-02-2018','input',4,2,1,1),
 (3,2.99,5,5,'21-09-2018','20-02-2018','input',2,4,2,1),
 (4,4.0,3,2,'21-09-2018','20-02-2018','output',2,4,2,1),
 (5,2.99,10,12,'21-10-2019','20-02-2018','input',2,4,2,1),
 (6,100.0,10,10,'','21-02-2018','input',3,8,3,2),
 (7,120.0,4,6,'','21-02-2018','ourput',3,8,3,2);
CREATE TABLE `restaurantUser` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`userId`	INTEGER,
	`restaurantId`	INTEGER,
	FOREIGN KEY(userId) REFERENCES user(userId) ON DELETE CASCADE,
	FOREIGN KEY(restaurantId) REFERENCES restaurant(restaurantId) ON DELETE CASCADE
);
INSERT INTO `restaurantUser` (id,userId,restaurantId) VALUES (1,1,1),
 (2,1,2),
 (3,2,3),
 (4,3,4),
 (5,4,4);
CREATE TABLE `restaurant` (
	`restaurantId`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`restaurantName`	TEXT,
	`address`	TEXT,
	`phone`	TEXT
);
INSERT INTO `restaurant` (restaurantId,restaurantName,address,phone) VALUES (1,'Milano','Yliopistokatu 12, Oulu, Finland','0458885555'),
 (2,'Rodin','Keskustie, Jyvaskyla, Finland','0477765555'),
 (3,'FastPizza','Jyvasentie1, Jyvaskyla, Finland','0558866333'),
 (4,'Opera','Poistokatu, Oulu, Finland','0556633227');
CREATE TABLE "item" (
	`itemId`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`itemName`	TEXT,
	`description`	TEXT,
	`vendorId`	TEXT,
	FOREIGN KEY(`vendorId`) REFERENCES `vendor`(`vendorId`) ON DELETE CASCADE
);
INSERT INTO `item` (itemId,itemName,description,vendorId) VALUES (1,'coca cola','soft drink','1'),
 (2,'Jaffa','soft drink','1'),
 (3,'7up','soft drink','1'),
 (4,'coca cola','soft drink','2'),
 (5,'7up','soft drink','2'),
 (6,'broilari','pizza broilari','2'),
 (7,'kebab','well kebab','2'),
 (8,'pizza lattikko','punainen normali pizza lattikko','3'),
 (9,'Rulla lattikko','Musta iso rulla lattikko','3');
COMMIT;
