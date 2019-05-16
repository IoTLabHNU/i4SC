import RPi.GPIO as GPIO	;
import mysql.connector;
import os, sys;

from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

print("PACKAGING SYSTEM")
try:
	#Connection to MySQL
	cnx = mysql.connector.connect(user='pi2', password='password',
								  host='10.49.63.147',
								  port='3306',
								  database='box')

	results = "";
	inputOrderNumber = input('\n\nEnter Order Number:\t')
	#inputOrderNumber = "FXID001"
	try:
		cursor = cnx.cursor(dictionary=True);	
		query = "SELECT * FROM `customerorder` WHERE ordernumber=%s;";
		cursor.execute(query, (inputOrderNumber,))
		results = cursor.fetchall()

		if len(results) > 0:
			query = "SELECT `name` FROM `customer` WHERE idcustomer=%s;";
			cursor.execute(query, (results[0]['customer'],))
			customer = cursor.fetchone()
		
			print("\nThe Order: {0}, made by Customer: {1}, is found with the following product/s.".format(inputOrderNumber, customer['name']))
			
			count = 1; total = 0;
			print("STAGES")
			query = "SELECT * FROM `packaging` WHERE customerorder=%s;";
			cursor.execute(query, (inputOrderNumber,))
			packaging = cursor.fetchone()
			if len(packaging) > 0:
				print("1 - SUCCESSFUL, the order was packaged.")

				query = "SELECT * FROM `dropzone` WHERE customerorder=%s;";
				cursor.execute(query, (inputOrderNumber,))
				zone = cursor.fetchone()
				if len(zone) > 0:
					print("2 - SUCCESSFUL, the order was droped.")
				else:
					print("The order is still waiting to be dropped on the zone.")
			else:
				print("The order has not been packaged yet.")
	except:
		print("The order was not found!");
	finally:
		if(cnx.is_connected()):
			cursor.close()
except:
	cnx.rollback()
	print('!Could not connect to MySql\n\tError: {0}\n\t\t{1}\n\t\t{2}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]));
finally:
        print("DONE!");

