'''
Created on 13.02.2013

Modified on 21.01.2018

Provides the database API to access the forum persistent data.

@author: ivan
@author: mika oja
'''

from datetime import datetime
import time, sqlite3, re, os
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/rms.db'
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
        at *db/forum.db*

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
            cur.execute("DELETE FROM messages")
            cur.execute("DELETE FROM users")
            #NOTE since we have ON DELETE CASCADE BOTH IN users_profile AND
            #friends, WE DO NOT HAVE TO WORRY TO CLEAR THOSE TABLES.

   

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

     #Helpers for users
    def _create_user_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {'firstname': firstname,
               'lastname': lastname',
               'email': 'email',
               'phone': 'phone',
               'username': 'username',
               'dob': 'dob',
               'residence': residence'
                }

            where:

            * ``username``: username of the user
            * ``firstanme``: given name of the user
            * ``lastname``: family name of the user
            * ``lastname``: family name of the user
            * ``dob``: date of birth of the user
            * ``email``: current email of the user          
	    * ``phone``: cellphone number of the user.

            Note that all values are string if they are not otherwise indicated.

        '''
	
        return {'firstname': row['firstname'],
               'lastname': row['lastname'],
               'email': row['email'],
               'phone': row['phone'],
               'username': row['username'],
               'dob': row['dob'],
                }
    
    #Helpers for restaurant
    def _create_restaurant_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {'restuaranOwner': { 'ownerName':'firstname',
			       'lastname': 'lastname',
			       'email': 'email',
			       'phone': 'uphone',
			       'username': 'username',
		       	       'dob': 'dob'},
		'restaurant': {'restaurantName': 'restaurantName',
			      'address': 'address',
			      'phone': 'rphone'
			     }
                }

            where:

            * ``username``: username of the restuarant owner
            * ``ownerName``: given name of the restaurant owner
            * ``lastname``: family name of the restaurant owner
            * ``dob``: date of birth of the restaurant owner 
            * ``email``: current email of the restaurant owner           
	    * ``uphone``: cellphone number of the restaurant owner
	    * ``rphone``: cellphone number of the restaurant
	    * ``restaurantname``: name of the restaurant
	    * ``address``: address of the restarant.

            Note that all values are string if they are not otherwise indicated.

        '''
	
        return {'restuaranOwner': { 'ownerName': row['firstname'],
			       'lastname': row['lastname'],
			       'email': row['email'],
			       'phone': row['uphone'],
			       'username': row['username'],
		       	       'dob': row['dob']},
		'restaurant': {'restaurantName': row['restaurantName'],
			      'address': row['address'],
			      'phone': row['rphone']
			     }
                }

    def _create_user_list_object(self, row):
        '''
        Same as :py:meth:`_create_user_list_object`. However, the resulting
        dictionary is targeted to build users in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``username``, ``username`` and
            ``lanstname``

        '''
        return {'username': row['username'], 'firstname': row['firstname'], 'lastname': row['lastname']}

    def _create_restaurant_list_object(self, row):
        '''
        Same as :py:meth:`_create_restaurant_list_object`. However, the resulting
        dictionary is targeted to build restaurant in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``restaurantName``, ``restaurant address`` and
            ``phone number``

        '''
        return {'restaurantName': row['restaurantName'], 'addess': row['address'], 'phone': row['phone']}

    def get_user(self, username):
        '''
        Extracts all the information of a user.

        :param str username: The username of the user to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_user_object`

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the user given a username
        query1 = 'SELECT * from user WHERE username = ?'
          #SQL Statement for retrieving the user information
               
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute SQL Statement to retrieve the id given a username
        pvalue = (username,)
        cur.execute(query1, pvalue)
       
        row = cur.fetchone()
        if row is None:
            return None

        # Execute the SQL Statement to retrieve the user invformation.
        # Create first the valuse
        
        return self._create_user_object(row)


    def get_restaurant(self, restaurant_name):
        '''
        Extracts all the information of a restaurant.

        :param str restaurantName: The name of the restaurant to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_restaurant_object`

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the restuarant information
        query = 'SELECT r.*, u.*, ru.position,u.phone as uphone, r.phone as rphone FROM restaurant r\
		 JOIN restaurantUser ru ON r.restaurantId = ru.restaurantId \
		 JOIN user u ON ru.userId = u.userId\
		 WHERE restaurantName = ?'

               
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute SQL Statement to retrieve the id given a username
        pvalue = (restaurant_name,)
        cur.execute(query, pvalue)
       
        row = cur.fetchone()
        if row is None:
            return None

        # Execute the SQL Statement to retrieve the restaurant  invformation.
        # Create first the valuse

        return self._create_restaurant_object(row)

    #ACCESSING THE USER table
    def get_users(self):
	'''
        Extracts all user from database.

        :param str username: The username of the user to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_user_list_object`

        '''
        #Create the SQL Statements
        #SQL Statement for retrieving the user given a username

        query = 'SELECT * FROM user'

        #SQL Statement for retrieving the user information
               
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        cur.execute(query)
        #Process the results
        rows = cur.fetchall()
        if rows is None:
            return None
        #Process the response.
        users = []
        for row in rows:
            users.append(self._create_user_list_object(row))
        return users


    def append_user(self, username, user):
        '''
        Create a new user in the database.

        :param str username: The username of the user to add
        :param dict user: a dictionary with the information to be added. The
                dictionary has the following structure:

                .. code-block:: javascript

                    {'username': 'ali', 'firstname': 'ali', 'lastname': 'hassani',
		    'phone': '0475556633', 'email': 'ali.hassani@yahoo.com', 
		    'password': '12335', 'dob': '22-02-2002'}

                where:

                * ``username``: username of the user
	        * ``firstanme``: given name of the user
       	        * ``lastname``: family name of the user
	        * ``lastname``: family name of the user
	        * ``dob``: date of birth of the user
	        * ``email``: current email of the user          
	        * ``password``: password of the user 
	        * ``phone``: cellphone number of the user.

            Note that all values are string if they are not otherwise indicated.

        :return: the username of the added user or None if the
            ``username`` passed as parameter is not  in the database.
        :raise ValueError: if the user argument is not well formed.

	dictionary template
          append_user(ali, {'username': 'ali', 'firstname': 'ali',
         'lastname': 'hassani', 'phone': '0475556633', 'email': 'ali.hassani@yahoo.com',
         'password': '12335', 'dob': '22-02-2002'})
        '''
	
        #Create the SQL Statements
          #SQL Statement for extracting the userid given a username
        query1 = 'SELECT userid from user WHERE username = ?'
          #SQL Statement to create the row in  users table
        query2 = 'INSERT INTO user(username, firstname, lastname, phone, email, password, dob)\
                  VALUES(?,?,?,?,?,?,?)'

	
	_username = username
	_firstname = user['firstname']
	_lastname = user['lastname']
	_phone = user['phone']
	_email = user['email']
	_password = user['password']
	_dob = user['dob']

        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a username
        pvalue = (username,)
        cur.execute(query1, pvalue)
        #No value expected (no other user with that username expected)
        row = cur.fetchone()
        #If there is no user add rows in user and user profile
        if row is None:
            #Add the row in users table
            # Execute the statement
            pvalue = (_username, _firstname, _lastname, _phone, _email, _password, _dob)
            cur.execute(query2, pvalue)

            self.con.commit()
            #We do not do any comprobation and return the username
            return _username
        else:
            return None

    def append_restaurant(self, restaurant):
        '''
        Create a new restaurant in the database.

        :param dict restaurant: a dictionary with the information to be added. The
                dictionary has the following structure:

                .. code-block:: javascript

                    {'restauratnName': 'name of the restaurant', 'address': 'address', 'phone': 'phone'}

                where:

                * ``restauratnName``: name of the restaurant
	        * ``address``: the address of the restaurant to be added
       	        * ``phone``: contact information for the new restaurant.

            Note that all values are string if they are not otherwise indicated.

        :return: the name of the added restaurant or None if the
        :raise ValueError: if the user argument is not well formed.

	dictionary template
          append_rastaurant( {'restaurantName': 'Sheraz', 'address': 'tuira, oulu, Finland', 'phone': '047555325'})
        '''
	
          #SQL Statement to create the row in  restaurant table
        query = 'INSERT INTO restaurant(restaurantName, address, phone)\
                  VALUES(?,?,?)'

	

	_restaurantName = restaurant['restaurantName']
	_address = restaurant['address']
	_phone = restaurant['phone']

        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
       
  
        pvalue = (_restaurantName, _address, _phone)
        cur.execute(query, pvalue)

        self.con.commit()
        #We do not do any comprobation and return the restaurant
        return _restaurantName


    def assign_user_to_restaurant(self, username, restaurantName, position):
        '''
        Create a new user in the database.

        :param str username: The username of the user to be assigned to the restaurant
        :param str restaurantName: The name of the restaurant which user should be added in
        :param str position: The position of user, can get value of owner or employee


            Note that all values are string if they are not otherwise indicated.

        :return: the true of the added user or False if the
            ``username`` and(or) restarant is not 
		passed as parameter is not  in the database.
        :raise ValueError: if the user argument is not well formed.

	dictionary template
          assign_user_to_restaurant(username, restaurant name, position)
        '''
	
        #Create the SQL Statements
          #SQL Statement for extracting the userid given a username
        query1 = 'SELECT userid from user WHERE username = ?'
          #SQL Statement for extracting the restaurantid given a restaurantName
        query2 = 'SELECT restaurantId from restaurant WHERE restaurantName = ?'
          #SQL Statement to create the row in  restaurantUser table
        query3 = 'INSERT INTO restaurantUser(userId, restaurantId, position)\
                  VALUES(?,?,?)'

        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a username
        pvalue = (username,)
        cur.execute(query1, pvalue)
        #No value expected (no other user with that username expected)
        row = cur.fetchone()

	#Execute the statement to extract the id associated to restaurant
	prvalue = (restaurantName,)
	cur.execute(query2, prvalue)
        #put result to row
	rowr = cur.fetchone()
	
	#check if the restaurant and user is exist in the database
	if row['userid'] !='' and rowr['restaurantId'] != '':
	    pvalue = (row['userid'], rowr['restaurantId'], position, )
	    cur.execute(query3, pvalue)
	    self.con.commit()	
	    return True
        else:
            return False

    def get_restaurants(self):
        '''
        Extracts all the information of a restaurant.

        :param str restaurantName: The name of the restaurant to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_restaurant_object`

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the user given a username
        query = 'SELECT * FROM restaurant'
          #SQL Statement for retrieving the user information
               
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute SQL Statement to retrieve the id given a username
        
        cur.execute(query)
       
        rows = cur.fetchall()
	restaurants = []
        for row in rows:
            # Execute the SQL Statement to retrieve the user invformation.
            # Create first the valuse
            restaurants.append(self._create_restaurant_list_object(row))
	return restaurants;



    def modify_user(self, username, user):
        '''
        Extracts all the information of a user.

        :param str username: The username of the user to search for.
        :param str user: The data of the user to be modifyed in database.
        :return: user if the user data is modifyed or None if not modifyed
	(ali, {'username': 'ali', 'firstname': 'ali',
        dictionary template 
	modify_user('ali', {'firstname': 'ali' ,'lastname': 'hassani', 'phone': '0475556633', 'email': 'ali.hassani@yahoo.com','dob': '22-02-2002'})
        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the username given a username
        query1 = 'SELECT username from user WHERE username = ?'
          #SQL Statement for retrieving the user information
               
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute SQL Statement to retrieve the username given a username
        pvalue = (username,)
        cur.execute(query1, pvalue)
       
        row = cur.fetchone()
        if row is None:
            return None

        query2 = 'UPDATE user SET firstname = ?, lastname = ?, phone = ?, email = ?, dob =? WHERE username = ?'

	
	_username = username
	_firstname = user['firstname']
	_lastname = user['lastname']
	_phone = user['phone']
	_email = user['email']
	_dob = user['dob']

        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a username
        pvalue = (username,)
        cur.execute(query1, pvalue)
        #No value expected (no other user with that username expected)
        row = cur.fetchone()
        #If there is no user add rows in user and user profile
        if row is not None:
            #Add the row in users table
            # Execute the statement
            pvalue = (_firstname, _lastname, _phone, _email, _dob, _username)
            cur.execute(query2, pvalue)

            self.con.commit()
            #We do not do any comprobation and return the username
	    if cur.rowcount < 1:
		return None
            return _username
        else:
            return None

    def modify_restaurant(self,restaurantName, restaurant):
        '''
        Extracts all the information of a restaurant.

        :param str restaurantName: The name of the restaurant to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_restaurant_object`

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the restuartantName as given restaurntname
	query1 = 'SELECT restaurantName FROM restaurant WHERE restaurantName = ?'
          #SQL Statement for updating the restuarant information
        query2 = 'UPDATE restaurant SET restaurantName = ?, address = ?, phone = ? \
		 WHERE restaurantName = ?'
          #SQL Statement for retrieving the user information
             
	_restaurantName = restaurant['restaurantName']
	_address = restaurant['address']
	_phone = restaurant['phone']

        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute SQL Statement to retrieve the id given a username
        pvalue = (restaurantName,)
        cur.execute(query1, pvalue)
       
        row = cur.fetchone()
        if row is None:
            return None
	else:
	    #Execute the update sql statement to update the restaurant
	    pvalue = (_restaurantName, _address, _phone, restaurantName )
	    cur.execute(query2, pvalue)
	    #Check if the restuarant information have been updated
	    #commet the transaction 
	    self.con.commit()
	    if cur.rowcount < 1:
		return None
	    return True
 
    def delete_user(self, username):
    	'''
    	Delete all the information of a given user
    	:param str username: the username of given user to be deleted
    	:return: return True if the user has been deleted or false 
    	if the user has not been deleted.
    	:raise valueError: if the aregument is not well supplyed. 
    	'''
    	
    	#SQL Statement for deleting user from database
    	query = 'DELETE FROM user WHERE username = ?'
    	
    	#Active foreign key support
    	self.set_foreign_keys_support()
    	
    	#Cursor and row initialization
    	self.con.row_factory = sqlite3.Row
    	cur = self.con.cursor()
    	
    	#Supply value for the sql statement and execute sql statement 
    	pvalue = (username, )
    	cur.execute(query, pvalue)
    	self.con.commit()
    	if cur.rowcount < 1:
    	    return False
    	return True












