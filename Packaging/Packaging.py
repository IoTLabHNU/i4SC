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
		
			print("\nThe Order: {0}, made by Customer: {1}, is found with the following product/s".format(inputOrderNumber, customer['name']))
			
			count = 1; total = 0;
			print("NAME\t\t\tPRICE")
			for row in results:
				query = "SELECT * FROM `productitems` WHERE idproductitems=%s;";
				cursor.execute(query, (row['productitems'],))
				product = cursor.fetchone()
				total += product['price']
				print("{0} {1},\t{2}".format(count, product['name'], product['price']))
				count = +1
			print("TOTAL: {0}".format(total))

			if input("\nPlease enter Y if the package is ready:\t").lower() == "y":
				try:
					id, rfidtext = reader.read()
					try:
						cursor = cnx.cursor();	
						query = "INSERT INTO `rfid` (`uid`) VALUES(%s);";
						result = cursor.execute(query, (id,))
						cnx.commit()
					except:
						pass
				finally:
					try:
						reader.write(inputOrderNumber)						
					finally:
						thresholdTemperature = input("Enter the Maximum Threshold Temperature:\t")
						thresholdHumidity =   input("Enter the Maximum Threshold Humidity:\t")
						try:
							cursor = cnx.cursor();	
							query = "INSERT INTO `packaging` (`customerorder`, `maximumThresholdTemperature`, `maximumThresholdHumidity`) VALUES(%s, %s, %s);";
							result = cursor.execute(query, (inputOrderNumber, thresholdTemperature, thresholdHumidity,))
							cnx.commit()
						finally:
							print("\nThe package is ready for delivery\n")
	except:
		cnx.rollback()
		print('!Could not insert a new record  to MySql\n\tError: {0}\n\t\t{1}\n\t\t{2}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]));
		print("The record was not found!");
	finally:
		if(cnx.is_connected()):
			cursor.close()
except KeyboardInterrupt:
	GPIO.cleanup()
finally:
        GPIO.cleanup()
