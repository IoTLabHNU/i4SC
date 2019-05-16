
import RPi.GPIO as GPIO ;
import mysql.connector;
from hx711 import HX711  # import the class HX711
import time, datetime
import uuid, os, sys

from mfrc522 import SimpleMFRC522

packageWeight = -1;

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

            GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
            # Create an object hx which represents your real hx711 chip
            # Required input parameters are only 'dout_pin' and 'pd_sck_pin'
            hx = HX711(dout_pin=21, pd_sck_pin=20)
            # measure tare and save the value as offset for current channel
            # and gain selected. That means channel A and gain 128
            err = hx.zero()
            # check if successful
            if err:
                raise ValueError('Tare is unsuccessful.')

            reading = hx.get_raw_data_mean()
            if reading:  # always check if you get correct value or only False
                # now the value is close to 0
                #print('Data subtracted by offset but still not converted to units:',
                #      reading)
                pass
            else:
                print('invalid data', reading)

            # In order to calculate the conversion ratio to some units, in my case I want grams,
            # you must have known weight.
            #input('Put known weight on the scale and then press Enter')
            reading = hx.get_data_mean()
            if reading:
                #print('Mean value from HX711 subtracted by offset:', reading)
                #known_weight_grams = input(
                #    'Write how many grams it was and press Enter: ')
                known_weight_grams = 1
                try:
                    value = float(known_weight_grams)
                    #print(value, 'grams')
                except ValueError:
                    print('Expected integer or float and I have got:',
                          known_weight_grams)

                # set scale ratio for particular channel and gain which is
                # used to calculate the conversion to units. Required argument is only
                # scale ratio. Without arguments 'channel' and 'gain_A' it sets
                # the ratio for current channel and gain.
                ratio = reading / value  # calculate the ratio for channel A and gain 128
                hx.set_scale_ratio(ratio)  # set ratio for current channel
                #print('Ratio is set.')
            else:
                raise ValueError('Cannot calculate mean value. Try debug mode. Variable reading:', reading)

            # Read data several times and return mean value
            # subtracted by offset and converted by scale ratio to
            # desired units. In my case in grams.
            #print("Now, I will read data in infinite loop. To exit press 'CTRL + C'")
            input('Press Enter to begin reading')
            
            #print(hx.get_weight_mean(20), 'g')
            packageWeight = "{0:.2f} Grams".format(hx.get_weight_mean())
            #time.sleep(2)
            #print("Current weight on the scale in grams is: ".format(packageWeight))
    except:
        cnx.rollback()
        print('Error: {0}\n\t\t{1}\n\t\t{2}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]));
        print("The record was not found!");
        GPIO.cleanup()
    finally:
        GPIO.cleanup()
        try:
            reader = SimpleMFRC522()
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
                    query = "INSERT INTO `packaging` (`customerorder`, `maximumThresholdTemperature`, `maximumThresholdHumidity`, `weight`) VALUES(%s, %s, %s, %s);";
                    result = cursor.execute(query, (inputOrderNumber, thresholdTemperature, thresholdHumidity, packageWeight,))
                    cnx.commit()
                finally:
                    print("\nThe package is ready for delivery\n")
            if(cnx.is_connected()):
                cursor.close()
except (KeyboardInterrupt, SystemExit):
    GPIO.cleanup()
    print("Bye")
finally:
        GPIO.cleanup()

