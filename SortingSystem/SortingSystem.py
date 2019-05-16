#This is the import block ===================
from __future__ import print_function
from __future__ import division
from builtins import input
from BrickPi import *   
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import mysql.connector
from Cake import Cake
import datetime
from firebase import firebase
from Infra import Infra
#============================================
class sortingSys:
    '''
        __author_ = Marcell Oosthuizen
        __credits_ = Daniel ,
        This class contains all the functions/methods used to control the sorting station.
        This includes 3 motors , 1 RFDI scanner and 1, infra red sensor.
        
        
        Attributes
        ----------
        
        reader: SimpleMFRC522()
            reader is set to the object that is used for the RFID scanner
            
        BrickPi.MotorEnable[PORT_A] : method of object BrickPi
            When this value is set to 1 it enabels motor A to be used in the script
        
        BrickPi.MotorEnable[PORT_B] : method of object BrickPi
            When this value is set to 1 it enabels motor B to be used in the script
            
        BrickPi.MotorEnable[PORT_C] : method of object BrickPi
            When this value is set to 1 it enabels motor C to be used in the script

        BrickPi.MotorEnable[PORT_D] : method of object BrickPi
            When this value is set to 1 it enabels motor D to be used in the script
            
        Infra: obj
            This is a object of the class Infra which handels the positioning of the sorting arm.
        
        cake : obj
            This is a object of the Cake class that is used to store variables of an incomming parcel(cake)
        
        power : int
            This is the power setting that given x it will set the power snet to the motor to x (from -255 , 255)
        
        dropZones : arry
            This array features the distances in seconds that the platform needs to travel to reach zone A-C
                
        cnx: obj
            used to establish a connection to the given database and sending/retrieving data from it
        
        Methods
        --------
        
        toFireBase(pack)
            This method was used in the legacy system where it would take a input of pack and send the infromation of that
            object to a cloud based database called firebase.
        ReadRFID(self)
            This is used to retrieve information from the rfid tag (customer order number), which it will return as well as write to the cake object.
            
        sendDataCont()
            This function sends data to the Bakery's database (dropZone table)
        
        forwardRoad(Sec)
            This function is used to move the platform forward for a given amount of time in seconds.
        
        backwardRoad(Sec)
            This function is used to move the platform backwards for a givena amount of time in seconds.
            
        forwardBelt(Sec)
            This fuction is used to move the convayer belt's motor forward (note due to the transmission designed this function moves the belt backwards)
            
        backwardBelt(Sec)
            This fuction is used to move the convayer belt's motor backward (note due to the transmission designed this function moves the belt frowards)
            
        getDestNew(oN)
            This function gets the destination of the product by quering it from the database and deciding by postal code in a if statement. This function returns ther destination
            as a string.
        
        rotor(Sec)
            This function handels the loading of the product onto the platform from the rfid read station(moves rotator arm and the belt)
        
        rotor2(Sec)
            This function is invoked when ever a bad package is found and will move the arm backwards to a designated zone.
            
        getTemp(oN)
            This fucntion queries the database to find if the product has at some point exceeded its temprature and humidity limit and will deside to sort the product or move it
            off the production line.
        
        zoneA()
            This function will move the sorting platform to desicnated zone A and then back to base.
        
        zoneB()
            This function will move the sorting platform to desicnated zone B and then back to base.
        
        zoneC()
            This function will move the sorting platform to desicnated zone C and then back to base.
        
        runFunc()
            This function binds all the functions in this file script together to form the over all sorting managment system.
    '''

    global  reader
    reader = SimpleMFRC522()
    BrickPiSetup()  

    BrickPi.MotorEnable[PORT_A] = 1 #Enable motor A --> rotor
    BrickPi.MotorEnable[PORT_C] = 1 #Enable the Motor C --> Wheels
    BrickPi.MotorEnable[PORT_D] = 1 #Enable the Motor D --> conv
    BrickPi.MotorEnable[PORT_B] = 1 #Enable motor B --> Belt 
    BrickPiSetupSensors()
    
        
        
    global Infra
    Infra = Infra()
    #=============================================================
    # Data to use
    #=============================================================
    global cake,power,dropZones
    cake = Cake("","","")
    power = 0
    
    dropZones = [0,2,4] #Loaction of the dropzones from a - c#
    #=============================================================
    # Connect to the database
    #=============================================================
    global cnx
    cnx = mysql.connector.connect(user ='pi2',password='password',host='10.49.63.147',port='3306',database='box')
    rfidTag = ""

    #=============================================================
    #sending data to the db package
    #=============================================================

    #def setup():
      #  GPIO.setmode(GPIO.BCM)
       # GPIO.setup(3,GPIO.IN)
        
    def toFireBase(self,pack):
        '''This method was used in the legacy system where it would take a input of pack and send the infromation of that
        object to a cloud based database called firebase.
        
        Parameters
        ----------
            pack: obj
                This function takes a input of the object pack.
        
        '''
        try:
            firebaser = firebase.FirebaseApplication('https://aiportcon.firebaseio.com/')
            res = firebaser.post('AirportCon',{'ID':pack.ID ,'Dest_ICAO': pack.Dest, 'DropZ': pack.DropZ , 'Origin' : pack.From , 'Time': pack.time , 'FlightNo' : pack.flightNo ,'TypeC' : pack.typeC})
            print (res)
        finally:
            print("done")
            
    #=============================================================

    #=============================================================
    #sending data to the db package
    #=============================================================

    def ReadRFID(self):
        '''This is used to retrieve information from the rfid tag (customer order number), which it will return as well as write to the cake object.
            
            Return
            ------
            newT : str
                returns the order number as a string. 
        
        '''
        global reader
        
        newT =""
        try:
            print("Waiting for package information ....")
            id, text = reader.read()
            newT = text.strip();
        finally:
            GPIO.cleanup()
            cake.setCustOr(newT)
        return str(newT) 
        
        
    #=============================================================
    #sending data to the db package
    #=============================================================
    def sendDataCont(self):
        '''This function sends data to the Bakery's database (dropZone table)
            
        Inputs
        ------
        cake : obj
            Object cake's data will be send to the database (ordernumber and dropzone).
        '''
        try:
            if(cnx.is_connected()):
                print("connected")
            cursor = cnx.cursor()
            query ="INSERT INTO box.dropzone (customerorder,Zone) VALUES (%s,%s)" 
            result = cursor.execute(query,[cake.custOr,cake.zone])
            cnx.commit()
        except Exception as l:
            print(l)
            print("could not insert!")
        cursor.close()

    #=============================================================
    #Run car forward 
    #=============================================================

    def forwardRoad(self,Sec):
        '''This function is used to move the platform forward for a given amount of time in seconds.
            
            Parameter
            ----------
            Sec : float
                The amount of time power will be provided to the motor.
            
        '''
        print ("Running Forward")
        power = 255
        BrickPi.MotorSpeed[PORT_A] = 0
        BrickPi.MotorSpeed[PORT_B] = 0
        BrickPi.MotorSpeed[PORT_D] = 0
        BrickPi.MotorSpeed[PORT_C] = power  #Set the speed of MotorC (-255 to 255)
       
        ot = time.time()
        while(time.time() - ot < Sec):    #running while loop for 3 seconds
            BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors
        time.sleep(.1)

    #=============================================================
    #Run car backwards
    #=============================================================
    def backwardRoad(self,Sec):
        '''This function is used to move the platform backwards for a givena amount of time in seconds.
        
            Parameter
            ----------
            Sec : float
                The amount of time power will be provided to the motor.
        
        '''
        print ("Running Backward")
        power = -255
        BrickPi.MotorSpeed[PORT_A] = 0
        BrickPi.MotorSpeed[PORT_B] = 0
        BrickPi.MotorSpeed[PORT_D] = 0
        BrickPi.MotorSpeed[PORT_C] = power  #Set the speed of MotorC (-255 to 255)
        distance = 0
        ot = time.time()
        while(time.time() - ot < Sec):    #running while loop for 3 seconds
            BrickPiUpdateValues()
        time.sleep(.1)
        
    #=============================================================
    #Run belt forwards
    #=============================================================    
    def forwardBelt(self,Sec):
        '''This fuction is used to move the convayer belt's motor forward (note due to the transmission designed this function moves the belt backwards)
            
            Parameter
            ----------
            sec : float
                The amount of time power will be provided to the motor.
       
        '''
        print ("Running Forward")
        power = 255
        BrickPi.MotorSpeed[PORT_B] = 0
        BrickPi.MotorSpeed[PORT_A] = 0
        BrickPi.MotorSpeed[PORT_D] = power  #Set the speed of MotorD (-255 to 255)
        BrickPi.MotorSpeed[PORT_C] = 0
        ot = time.time()
        while(time.time() - ot < Sec):    #running while loop for 3 seconds
            BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors
        time.sleep(.1)

    #=============================================================
    #Run belt backwards
    #=============================================================
    def backwardBelt(self,Sec):
        '''This fuction is used to move the convayer belt's motor backward (note due to the transmission designed this function moves the belt frowards)
           
            Parameter
            ----------
            sec : float
                The amount of time power will be provided to the motor.
           
        '''
        print ("Running belt Backward")
        power = -255
        BrickPi.MotorSpeed[PORT_A] = 0
        BrickPi.MotorSpeed[PORT_C] = 0
        BrickPi.MotorSpeed[PORT_D] = 0#Set the speed of MotorD (-255 to 255)
        BrickPi.MotorSpeed[PORT_B] = power
        ot = time.time()
        while(time.time() - ot < Sec):    #running while loop for 3 seconds
            BrickPiUpdateValues()
        time.sleep(.1)


    #=============================================================
    def getDestNew(self,oN):
        '''This function gets the destination of the product by quering it from the database and deciding by postal code in a if statement. This function returns ther destination
        as a string.
        
            Parameter
            ----------
            oN : str
                order number of the product
            
            Returns
            -------
            dest : str
                The destiantion/zone of the product
        
        '''
        dest = ""
        try:
            if(cnx.is_connected()):
                print("connected")
            cursor = cnx.cursor()
            query = ( "SELECT * FROM box.customerorder WHERE ordernumber = %s ") 
            result = cursor.execute(query,(oN,))
            records = cursor.fetchall()
            cust = records[0]
            cust = cust[1]
            print(type(cust))
            print(cust)
            
            #gets adress
            result = cursor.execute("SELECT * FROM box.customer WHERE idcustomer = %d " %int(cust))
            records = cursor.fetchall()
            add = records[0]
            add = add[2]
            #print("here" + str(add))
            #get zone
            result = cursor.execute("SELECT * FROM box.address WHERE idaddress = %d " %int(add))
            records = cursor.fetchall()
            yone = records[0]
            yone = yone[3]
            yone = str(yone)
            yone = yone[0]
            yone = int(yone)
            #print("there")
            
            if(yone >= 1 and yone <= 3):
                dest = "A"
            if(yone >= 4 and yone <= 6):
                dest = "B"
            if(yone >= 7 and yone <= 9):
                dest = "C"
            
            #print("this is the : " + dest)
        except Exception as l:
            print(l)
            
            #print("could not read")
        cursor.close()
        cake.setZone(dest)
        return dest
    #Run program 1
    #=============================================================

    def rotor(self,Sec):
        '''This function handels the loading of the product onto the platform from the rfid read station(moves rotator arm and the belt)
        
            Parameters
            -----------
            Sec : float
                The amount of seconds the power will be supplied to the sorting blade and convayer belt.

        
        '''
        print ("Running rotor")
        power = -255
        BrickPi.MotorSpeed[PORT_D] = 0
        BrickPi.MotorSpeed[PORT_A] = power
        BrickPi.MotorSpeed[PORT_B] = -190
        
        BrickPi.MotorSpeed[PORT_C] = 0  #Set the speed of MotorC (-255 to 255)
        distance = 0
        ot = time.time()
        while(time.time() - ot < Sec):    #running while loop for 3 seconds
            BrickPiUpdateValues()
        time.sleep(.1)
        
        
    def rotor2(self,Sec):
        '''This function is invoked when ever a bad package is found and will move the arm backwards to a designated zone.

        '''
        print ("Running rotor")
        power = 255
        BrickPi.MotorSpeed[PORT_D] = 0
        BrickPi.MotorSpeed[PORT_A] = power
        BrickPi.MotorSpeed[PORT_B] = 0 # belt
        BrickPi.MotorSpeed[PORT_C] = 0  #Set the speed of MotorC (-255 to 255) wheels
        distance = 0
        ot = time.time()
        while(time.time() - ot < Sec):    #running while loop for 3 seconds
            BrickPiUpdateValues()
        time.sleep(.1)
        
    #def getRotorPos():


    def getTemp(self,oN):
        '''This fucntion queries the database to find if the product has at some point exceeded its temprature and humidity limit and will deside to sort the product or move it
        off the production line.
    
            Parameters
            ----------
            oN : str
                This is the order number of the product arriving on then scanning platform.
            
            Return
            -------
            dest : str
                Returns the destination/zone the product must be sorted to.
            
            
        '''
        dest = "0"
        temp = 0
        maxTemp = 0
        hum = 0
        maxHum = 0
        try:
            if(cnx.is_connected()):
                print("connected")
            cursor = cnx.cursor()
            query = ( "SELECT * FROM box.packaging WHERE customerorder = %s ") 
            result = cursor.execute(query,(oN,))
            records = cursor.fetchall()
            temp = records[0]
            maxTemp = temp[5]
            print(maxTemp)
            
            cursor = cnx.cursor()
            query = ( "select *from box.environmentsensor ORDER BY idenvironmentSensor DESC LIMIT 1;") 
            result = cursor.execute(query)
            records = cursor.fetchall()
            temp = records[0]
            temp = temp[1]
            
            print(type(temp))
            print(temp)
            
            cursor = cnx.cursor()
            query = ( "SELECT * FROM box.packaging WHERE customerorder = %s ") 
            result = cursor.execute(query,(oN,))
            records = cursor.fetchall()
            hum = records[0]
            maxHum = hum[7]
            print("max hum =" +str(maxHum))
            
            cursor = cnx.cursor()
            query = ( "select *from box.environmentsensor ORDER BY idenvironmentSensor DESC LIMIT 1;") 
            result = cursor.execute(query)
            records = cursor.fetchall()
            hum = records[0]
            hum = hum[2]
            print ("current hum = " + str(hum))
            
        except Exception as l:
            print(l)
            
            print("could not read")
        cursor.close()
        if (temp <= maxTemp and hum <= maxHum):
            dest = "0"
        else:
            dest = "1"
        return dest
    
    
    def zoneA(self):
        '''This function will move the sorting platform to desicnated zone A and then back to base.
        
        '''
        self.rotor(0.8)
        print('this is zone one')
        self.forwardRoad(dropZones[0])
        time.sleep(1)
        self.backwardBelt(1)
        time.sleep(1)
        self.backwardRoad(dropZones[0])
        
    def zoneB(self):
        '''This function will move the sorting platform to desicnated zone B and then back to base.
        
        '''
        self.rotor(0.8)
        print('this is zone two')
        self.forwardRoad(dropZones[1])
        time.sleep(1)
        self.backwardBelt(1)
        time.sleep(1)
        self.backwardRoad(dropZones[1])
        
        
    def zoneC(self):
        '''This function will move the sorting platform to desicnated zone C and then back to base.
        
        '''
        
        self.rotor(0.8)
        print('this is zone three')
        self.forwardRoad(dropZones[2])
        time.sleep(1)
        self.backwardBelt(1)
        time.sleep(1)
        self.backwardRoad(dropZones[2])
    
    def runFunc(self):
        '''This function binds all the functions in this file script together to form the over all sorting managment system.

            More detail
            -----------
             -> Calls the ReadRFID function to get order number.
             -> Checks if the temprature was compremized.
             -> Calls getDestNew function to get the destination of the product.
             -> Uses If to deduce if the product must go on to sorting or be kicked off the production line.
             -> Uses another if statment block to send the platform where the product must be dropped off.
             -> will call apon the sendDataCont function to post the nessacary data to the database given the product hand off. 
            
        '''
        while True:
            try:
                
                orderNum = self.ReadRFID()
                Dest  = self.getDestNew(self.ReadRFID())
                
                if self.getTemp(cake.getCustOr()) == "0":
                    Dest = Dest
                else :
                    Dest = "Z"
                    cake.setZone(Dest)
                
                if (Dest == 'A'):
                    self.zoneA()
                    self.sendDataCont()
                    
                elif (Dest == 'B'):
                    self.zoneB()
                    self.sendDataCont()
                    
                elif Dest == 'C':
                    self.zoneC()
                    self.sendDataCont()
                    
                else:
                    print("not any of those")
                    self.rotor2(0.8)#Infra.infSen()
                    self.sendDataCont()
                    
                print("End of Try")
                Infra.setup()
                Infra.infSen()
            except Exception as exit:
                print("User pressed exit !!!")    
            finally:
                GPIO.cleanup()
  




