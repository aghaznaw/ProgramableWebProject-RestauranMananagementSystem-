BEGIN TRANSACTION;
CREATE TABLE vendor(vendorId INTEGER  PRIMARY KEY AUTOINCREMENT,
		Name TEXT,
		address TEXT,
		email TEXt,
		phont TEXT,
		restaurantId,
		FOREIGN KEY(restaurantId) references restaurant(restaurantId) ON DELETE CASCADE
);
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
CREATE TABLE `restaurant` (
	`restaurantId`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`restaurantName`	TEXT,
	`address`	TEXT,
	`phone`	TEXT
);
CREATE TABLE "item" (
	`itemId`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`itemName`	TEXT,
	`description`	TEXT,
	`restaurantId`	TEXT,
	FOREIGN KEY(`restaurantId`) REFERENCES `restaurant`(`restaurantId`) ON DELETE CASCADE
);
CREATE TABLE `` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`restaurantid`	INTEGER,
	`userid`	INTEGER, 
	FOREIGN KEY(userId) REFERENCES user(userId) ON DELETE CASCADE,
	FOREIGN KEY(restaurantId) REFERENCES restaurant(restaurantId) ON DELETE CASCADE
);
COMMIT;
