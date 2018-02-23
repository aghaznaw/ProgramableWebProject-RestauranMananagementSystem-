'''
Created on 12.02.2018


Provides the database API to access the RMS persistent data.

@author: Dat Le
@author: Ahmad Shangan
'''

from datetime import datetime
import time, sqlite3, re, os
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/rms'
DEFAULT_SCHEMA = "db/rms_schema_dump.sql"
DEFAULT_DATA_DUMP = "db/rms_data_dump.sql"


class Engine(object):
    '''
    Abstraction of the database.

    It includes tools to create, configure,
    populate and connect to the sqlite file. You can access the Connection
    instance, and hence, to the database interface itself using the method
    :py:meth:`connection`.

    :Example:

    >>> engine = Engine()
    >>> con = engine.connect()

    :param db_path: The path of the database file (always with respect to the
        calling script. If not specified, the Engine will use the file located
        at *db/rms*

    '''
    def __init__(self, db_path=None):
        '''
        '''

        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    def connect(self):
        '''
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection

        '''
        return Connection(self.db_path)

    def remove_database(self):
        '''
        Removes the database file from the filesystem.

        '''
        if os.path.exists(self.db_path):
            #THIS REMOVES THE DATABASE STRUCTURE
            os.remove(self.db_path)

    def clear(self):
        '''
        Purge the database removing all records from the tables. However,
        it keeps the database schema (meaning the table structure)

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        #THIS KEEPS THE SCHEMA AND REMOVE VALUES
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        with con:
            cur = con.cursor()
            cur.execute("DELETE FROM vendor")
            cur.execute("DELETE FROM user")
            cur.execute("DELETE FROM stock")
            cur.execute("DELETE FROM restaurant")
            cur.execute("DELETE FROM item")
            #NOTE since we have ON DELETE CASCADE BOTH IN users_profile AND
            #friends, WE DO NOT HAVE TO WORRY TO CLEAR THOSE TABLES.

    #METHODS TO CREATE AND POPULATE A DATABASE USING DIFFERENT SCRIPTS
    def create_tables(self, schema=None):
        '''
        Create programmatically the tables from a schema file.

        :param schema: path to the .sql schema file. If this parmeter is
            None, then *db/rms_schema_dump.sql* is utilized.

        '''
        con = sqlite3.connect(self.db_path)
        if schema is None:
            schema = DEFAULT_SCHEMA
        try:
            with open(schema) as f:
                sql = f.read()
                cur = con.cursor()
                cur.executescript(sql)
        finally:
            con.close()

    def populate_tables(self, dump=None):
        '''
        Populate programmatically the tables from a dump file.

        :param dump:  path to the .sql dump file. If this parmeter is
            None, then *db/rms_data_dump.sql* is utilized.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        #Populate database from dump
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with open (dump) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)

    #METHODS TO CREATE THE TABLES PROGRAMMATICALLY WITHOUT USING SQL SCRIPT
    def create_user_table(self):
        '''
        Create the table ``item`` programmatically, without using .sql file.

        Print an error item in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE user(userId INTEGER PRIMARY KEY AUTOINCREMENT,\
                	firstname TEXT,\
                	lastname TEXT,\
                	username TEXT,\
                	email	TEXT,\
                	password	TEXT,\
                	phone	TEXT,\
                	dob	TEXT )'
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

    def create_vendor_table(self):
        '''
        Create the table ``vendor`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE vendor(`userId`	INTEGER PRIMARY KEY AUTOINCREMENT,\
    	`firstname`	TEXT,\
    	`lastname`	TEXT,\
    	`username`	TEXT,\
    	`email`	TEXT,\
    	`password`	TEXT,\
    	`phone`	TEXT,\
    	`dob`	TEXT)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

    def create_stock_table(self):
        '''
        Create the table ``stock`` programmatically, without using
        .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE stock(`id`	INTEGER PRIMARY KEY AUTOINCREMENT,\
    	`price`	REAL,\
    	`quantity`	INTEGER,\
    	`quantityInStock`	INTEGER,\
    	`expireDate`	TEXT,\
    	`date`	TEXT,\
    	`transactionType`	TEXT,\
    	`vendorId`	INTEGER,\
    	`itemId`	INTEGER,\
    	`restaurantId`	INTEGER,\
    	`userId`	INTEGER,\
    	FOREIGN KEY(vendorId) references vendor(vendorId) ON DELETE CASCADE,\
    	FOREIGN KEY(itemId) references item(itemId) ON DELETE CASCADE,\
    	FOREIGN KEY(restaurantId) references restaurant(restaurantId) ON DELETE CASCADE,\
    	FOREIGN KEY(userId) references user(userId) ON DELETE CASCADE )'
        con = sqlite3.connect(self.db_path)

        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

    def create_restaurant_table(self):
        '''
        Create the table ``friends`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE restaurant (`restaurantId`	INTEGER PRIMARY KEY AUTOINCREMENT,\
    	`restaurantName`	TEXT,\
    	`address`	TEXT,\
    	`phone`	TEXT)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print "Error %s:" % excp.args[0]
        return None

    def create_restaurantUser_table(self):
        '''
        Create the table ``friends`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE restaurantUser (`id`	INTEGER PRIMARY KEY AUTOINCREMENT,\
    	`restaurantid`	INTEGER,\
    	`userid`	INTEGER,\
    	FOREIGN KEY(userId) REFERENCES user(userId) ON DELETE CASCADE,\
    	FOREIGN KEY(restaurantId) REFERENCES restaurant(restaurantId) ON DELETE CASCADE)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print "Error %s:" % excp.args[0]
        return None

    def create_item_table(self):
        '''
        Create the table ``friends`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE item (`itemId`	INTEGER PRIMARY KEY AUTOINCREMENT,\
    	`itemName`	TEXT,\
    	`description`	TEXT,\
    	`vendorId`	TEXT,\
    	FOREIGN KEY(`vendorId`) REFERENCES `vendor`(`vendorId`) ON DELETE CASCADE)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print "Error %s:" % excp.args[0]
        return None

class Connection(object):
    '''
    API to access the Forum database.

    The sqlite3 connection instance is accessible to all the methods of this
    class through the :py:attr:`self.con` attribute.

    An instance of this class should not be instantiated directly using the
    constructor. Instead use the :py:meth:`Engine.connect`.

    Use the method :py:meth:`close` in order to close a connection.
    A :py:class:`Connection` **MUST** always be closed once when it is not going to be
    utilized anymore in order to release internal locks.

    :param db_path: Location of the database file.
    :type dbpath: str

    '''
    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)

    def close(self):
        '''
        Closes the database connection, commiting all changes.

        '''
        if self.con:
            self.con.commit()
            self.con.close()

    #FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        '''
        try:
            #Create a cursor to receive the database values
            cur = self.con.cursor()
            #Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            #We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            is_activated = data == (1,)
            print "Foreign Keys status: %s" % 'ON' if is_activated else 'OFF'
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            self.close()
            raise excp
        return is_activated

    def set_foreign_keys_support(self):
        '''
        Activate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, ON
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    def unset_foreign_keys_support(self):
        '''
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = OFF'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, OFF
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    #HELPERS
    #Here the helpers that transform database rows into dictionary. They work
    #similarly to ORM

    #Helpers for vendors
    def _create_vendor_object(self, row):
        vendor_id = 'v-' + str(row['vendorId'])
        vendor_name = row['Name']
        vendor_address = row['address']
        vendor_email = row['email']
        vendor_phone = row['phone']
        vendor = {'vendorId': vendor_id, 'email': vendor_email,
                   'phone': vendor_phone, 'name': vendor_name,
                   'address': vendor_address}
        return vendor

    def _create_vendor_list_object(self, row):

        vendor_name = row['Name']
        vendor_address = row['address']
        vendor_phone = row['phone']
        vendor = { 'phone': vendor_phone, 'name': vendor_name,
                  'address': vendor_address}
        return vendor

    #Helpers for Item
    def _create_item_object(self, row):
        item_id = 'it-' + str(row['itemId'])
        item_name = row['itemName']
        item_description = row['description']
        item_vendorId = row['vendorId']
        item = {'itemId': item_id, 'vendorId': item_vendorId,
                   'itemName': item_name,'desciption': item_description}
        return item

    def _create_item_list_object(self, row):
        item_name = row['itemName']
        item_description = row['description']
        item_vendorId = row['vendorId']
        return {'itemName': item_name,'desciption': item_description,'vendorId': item_vendorId}

    #Helpers for Stock
    def _create_stock_object(self, row):
        stock_id = 'st-' + str(row['id'])
        stock_price = row['price']
        stock_quantity = row['quantity']
        stock_quantityInStock = row['quanityInStock']
        stock_expireDate = row['expireDate']
        stock_date = row['date']
        stock_transactionType = row['transanctionType']
        stock_vendorID = row['vendorId']
        stock_itemId = row['itemId']
        stock_restaurantId = row['restaurantId']
        stock_userId = row['userId']
        stock = {'stockId': stock_id, 'quatityInStock': stock_quantityInStock,
                   'price': stock_price,'quantity': stock_quantity,
                 'expireDate': stock_expireDate, 'date': stock_date,
                 'transanctionType': stock_transactionType, 'vendorId': stock_vendorID,
                 'itemId': stock_itemId ,'restaurantId': stock_restaurantId, 'userId': stock_userId}
        return stock

    def _create_stock_list_object(self, row):
        stock_itemId = row['itemId']
        stock_quantityInStock = row['quanityInStock']
        stock_expireDate = row['expireDate']
        stock_date = row['date']
        stock_transactionType = row['transanctionType']
        stock_userId = row['userId']
        return {'itemId': stock_itemId,'quatityInStock': stock_quantityInStock,
                 'expireDate': stock_expireDate, 'date': stock_date,
                 'transanctionType': stock_transactionType, 'userId': stock_userId}


    #API ITSELF
    #Vendor Table API.
    def get_vendor(self, vendorid):
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the SQL Query
        query = 'SELECT * FROM vendor WHERE vendorId = ?'
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (vendorid,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        return self._create_vendor_object(row)

    def delete_vendor(self, vendorid):

        query = 'DELETE FROM vendor WHERE vendorId = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (vendorid,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def append_vendor(self, vendor):

       query1 = 'SELECT * from vendor WHERE Name = ?'
       query2 = 'INSERT INTO vendor(vendorId,Name,address,email,phone)\
                 VALUES(?,?,?,?,?)'

       _Name = vendor.get('Name', None)
       _address = vendor.get('address', None)
       _email = vendor.get('email', None)
       _phone = vendor.get('phone', None)
       #Activate foreign key support
       self.set_foreign_keys_support()
       #Cursor and row initialization
       self.con.row_factory = sqlite3.Row
       cur = self.con.cursor()
       #Execute the statement to extract the id associated to a nickname
       pvalue = (_Name,)
       cur.execute(query1, pvalue)
       #No value expected (no other user with that nickname expected)
       row = cur.fetchone()
       #If there is no user add rows in user and user profile
       if row is None:
           #Add the row in users table
           # Execute the statement
           lid = cur.lastrowid
           pvalue = (lid, _Name, _address, _email,_phone)
           cur.execute(query2, pvalue)
           self.con.commit()
           #We do not do any comprobation and return the nickname
           return _Name
       else:
           return None

    #Item Table API.
    def get_item(self, itemId):
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the SQL Query
        query = 'SELECT * FROM item WHERE itemId = ?'
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (itemId,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        return self._create_item_object(row)

    def delete_item(self, itemid):

        query = 'DELETE FROM item WHERE itemId = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (itemid,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def append_item(self, item):

        query1 = 'SELECT * from item WHERE itemName = ?'
        query2 = 'INSERT INTO item(itemId,itemName,description,vendorId)\
                  VALUES(?,?,?,?)'

        _itemName = item.get('itemName', None)
        _description = item.get('description', None)
        _vendorId = item.get('vendorId', None)
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a nickname
        pvalue = (_itemName,)
        cur.execute(query1, pvalue)
        #No value expected (no other user with that nickname expected)
        row = cur.fetchone()
        #If there is no user add rows in user and user profile
        if row is None:
            #Add the row in users table
            # Execute the statement
            lid = cur.lastrowid
            pvalue = (lid, _itemName, _description, _vendorId)
            cur.execute(query2, pvalue)
            self.con.commit()
            #We do not do any comprobation and return the nickname
            return _itemName
        else:
            return None

    #Stock Table API.
    def get_stock(self, stockId):
        match = re.match(r'st-(\d{1,3})', stockId)
        if match is None:
            raise ValueError("The itemID is malformed")
        stockId = int(match.group(1))
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the SQL Query
        query = 'SELECT * FROM stock WHERE stockId = ?'
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (stockId,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        return self._create_stock_object()

    def delete_stock(self, stockId):
       query = 'DELETE FROM stock WHERE stockId = ?'
       #Activate foreign key support
       self.set_foreign_keys_support()
       #Cursor and row initialization
       self.con.row_factory = sqlite3.Row
       cur = self.con.cursor()
       #Execute the statement to delete
       pvalue = (stockId,)
       cur.execute(query, pvalue)
       self.con.commit()
       #Check that it has been deleted
       if cur.rowcount < 1:
           return False
       return True

    def append_stock(self, stock):
       query1 = 'SELECT * from stock WHERE itemId = ? AND restaurantId = ?'
       query2 = 'INSERT INTO stock(id,price,quantity,quantityInStock,expireDate,date,transactionType,vendorId,itemId,restaurantId,userId)\
                   VALUES(?,?,?,?,?,?,?,?,?,?,?)'

       _price = stock.get('price', None)
       _quantity = stock.get('quantity', None)
       _quantityInStock = stock.get('quantityInStock', None)
       _expireDate = stock.get('expireDate', None)
       _date = datetime.now()
       _transactionType = stock.get('transactionType', None)
       _vendorId = stock.get('vendorId', None)
       _itemId = stock.get('itemId', None)
       _restaurantId = stock.get('restaurantId', None)
       _userId = stock.get('userId', None)

       # Activate foreign key support
       self.set_foreign_keys_support()
       # Cursor and row initialization
       self.con.row_factory = sqlite3.Row
       cur = self.con.cursor()
       # Execute the statement to extract the id associated to a itemId and restaurantId
       pvalue = (_itemId,_restaurantId)
       cur.execute(query1, pvalue)
       # No value expected (no other user with that itemId and restaurantId expected)
       row = cur.fetchone()
       if row is None:
           # Add the row in stock table
           # Execute the statement
           lid = cur.lastrowid
           pvalue = (lid, _price, _quantity, _quantityInStock, _expireDate, _date, _transactionType, _vendorId, _itemId, _restaurantId, _userId)
           cur.execute(query2, pvalue)
           self.con.commit()
           # We do not do any comprobation and return the nickname
           return _date
       else:
           return None
