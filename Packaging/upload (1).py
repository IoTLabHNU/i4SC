"""
    This Python Script uses Adafruit Python DHT Sensor Library to read the DHT 
    series of humidity and temperature sensors on a Raspberry Pi 3 (Model  B+). The sensor 
    used is the DHT22 temperature-humidity sensor. --> https://www.adafruit.com/products/385
"""
import pyrebase                                     #Python wrapper for the Firebase API
import uuid, os, sys, time, datetime, socket;
import mysql.connector;                             #MySQL connector Python connector
import Adafruit_DHT                                 #for reading the humidity and temaparature
import RPi.GPIO as GPIO  

LightSensorDigital = 2                              #GPIO output pin for light sensor (digital output)
LightSensorAnalog = 3                               #GPIO output pin for light sensor (analog output)
RedLight = 19
sensor = Adafruit_DHT.DHT11                         # Sensor should be set to Adafruit_DHT.DHT11


#Connection to MySQL Database Server
cnx = mysql.connector.connect(user='pi2', password='password',host='10.49.63.147',port='3306',database='box')
#Credentials to connect to the the Firebase database
Config = {
                "apiKey": "AIzaSyANky8tRqM9OB-DE7GhGCbsXNrc1miPbi4",
                "authDomain": "database2-3608a.firebaseapp.com",
                "databaseURL": "https://database2-3608a.firebaseio.com",
                "projectId": "database2-3608a",
                "storageBucket": "database2-3608a.appspot.com",
                "messagingSenderId": "767798854296",
                "appId": "1:767798854296:web:daf29694c4517a34"
            }

def destroy():
    """
        Function to to clean up all the GPIO ports used in this script.
        It resets ports used in this program back to input mode.
        :return: nothing
    """
    GPIO.output(RedLight, GPIO.LOW) 
    GPIO.cleanup()  

def get_mac():
    """
        Function to get the MAC address of the Raspberry Pi.
        :return: returns the MAC address
    """
    mac_num = hex(uuid.getnode()).replace('0x', '').upper()
    mac = '-'.join(mac_num[i: i + 2] for i in range(0, 11, 2))
    return mac


def get_ip():
    """
        Function to get the IP address of the Raspberry Pi.
        :return: returns the IP address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def uploadDeviceInformation():
    """
        Function to upload or insert the Raspberry Pi information into the database (device table)
        :return: nothing
    """
    print("Inserting Device information")
    try:
        MacAddress = get_mac();
        IpAddress =  get_ip();

        cursor = cnx.cursor();  
        query = "INSERT INTO `device` (`name`, `macAddress`, `IPAddress`, `OS`, `manufacturer`, `model`) VALUES(%s, %s, %s, %s, %s, %s);";
        values = ('Smart Box', MacAddress, IpAddress, 'Raspberian','Raspberry Pi', 'Model B+');
        result = cursor.execute(query, values)
        cnx.commit()
    except:
        cnx.rollback()
        print('!Could not insert a new record  to MySql\n\tError: {0}\n\t\t{1}\n\t\t{2}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]));
    finally:
        if(cnx.is_connected()):
            cursor.close()

def uploadSensorReadings():
    """
        Function to upload or insert real-time sensor readings of temperature, light intensity and
        humidity into MySQL database.
        :return: nothing
    """
    MacAddress = get_mac();                             # retrieving the MAC address
    pin = 4                                             # connected to GPI04.

    try:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LightSensorDigital, GPIO.IN) #Digital
        GPIO.setup(LightSensorAnalog, GPIO.IN)  #Analog

        GPIO.setup(RedLight, GPIO.OUT)   
        GPIO.output(RedLight, GPIO.LOW) 
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
            

    while(True):

        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)    
        # Note that sometimes you won't get a reading and
        # the results will be null (because Linux can't
        # guarantee the timing of calls to read the sensor).
        # If this happens try again!
        if humidity is not None and temperature is not None:
            try:
                cursor = cnx.cursor();
                query = "INSERT INTO `environmentsensor` (`temperature`,`humidity`) VALUES(%s, %s);";
                values = (temperature, humidity);
                result = cursor.execute(query, values)                  
                cnx.commit()
                result = cursor.execute("SELECT LAST_INSERT_ID();")
                Environment_ID = cursor.fetchone()[0]
            except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
                destroy()
            except:
                cnx.rollback()
                print('!Could not insert a new record of ENVIRONMENT SENSOR to MySql\n\tError: {0}\n\t\t{1}\n\t\t{2}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]));
            finally:
                if(cnx.is_connected()):
                    cursor.close()
            print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))          
        else:
            print('Failed to get reading. Try again!')
        
        #Inserting light sensor data
        try: 
            cursor = cnx.cursor();
            query =   "INSERT INTO `lightsensor` (`digital`, `analog`) VALUES (%s, %s);";
            values = (GPIO.input(LightSensorDigital), GPIO.input(LightSensorAnalog));
            if GPIO.input(LightSensorAnalog) == 1:
                GPIO.output(RedLight, GPIO.HIGH)

            result = cursor.execute(query, values)
            cnx.commit()
            result = cursor.execute("SELECT LAST_INSERT_ID();")
            Light_ID = cursor.fetchone()[0]
        except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
            destroy()
        except:
            cnx.rollback()
            print('!Could not insert a new record of LIGHT SENSOR to MySql\n\tError: {0}\n\t\t{1}\n\t\t{2}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]));
        finally:
            if(cnx.is_connected()):
                cursor.close()
        print('Digital={0}  Analog={1}\n'.format(GPIO.input(LightSensorDigital), GPIO.input(LightSensorAnalog))) 

        #Inserting a Record
        try: 
            time_sense = time.strftime('%H:%M:%S')
            date_sense = time.strftime('%d/%m/%Y')
            cursor = cnx.cursor();
            query =   "INSERT INTO `sensorrecord` (`light`,`environment`, `device`, `datevalue`, `timevalue`) VALUES (%s, %s, %s, %s, %s);";
            values = (Light_ID, Environment_ID, MacAddress, date_sense,time_sense);
            result = cursor.execute(query, values)
            cnx.commit()
        except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
            destroy()
        except:
            cnx.rollback()
            print('!Could not insert a new record of RECORDS to MySql\n\tError: {0}\n\t\t{1}\n\t\t{2}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]));
        finally:
            if(cnx.is_connected()):
                cursor.close()

        time.sleep(1);

def uploadToFirebase():
    """
        Function to upload or insert real-time sensor readings of temperature and
        humidity into the Firebase database. It also alerts the user if temperature > 25 degrees celcius
        or humidity >50% (too humid or warm for the cakes) by turning a red LED on.
        :return: nothing
    """

    GPIO.setmode(GPIO.BCM)
    Firebase = pyrebase.initialize_app(Config)          #       
    db = Firebase.database()                            #
    while(True):
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        data = {'Temperature':temperature,'Humidity':humidity}

        db.child('/data').push(data)

        if (humidity > 50) or (temperature > 25) :
            GPIO.setup(18,GPIO.OUT)
            GPIO.output(18,GPIO.HIGH)
            print ('Warning : Alert light on!!. Box too humid or temperature too high')
        else:
            GPIO.setup(18,GPIO.OUT)
            GPIO.output(18,GPIO.LOW)
            print ('Temperature is still okay ')
    GPIO.cleanup()

print("i4SC\n")
uploadDeviceInformation()
uploadSensorReadings()
uploadToFirebase()

