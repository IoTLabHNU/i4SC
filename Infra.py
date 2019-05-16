from __future__ import print_function
from __future__ import division
import RPi.GPIO as GPIO
import time
from BrickPi import *
from builtins import input

class Infra:
    '''
    This class contains the methods used to keep track of the sorting arm.
    The idea is that the sorting arm needs to always finish in the same place that it started off at.
    For this we are currently using a infra red sensorand one motor.
    
    Attributes
    ----------
    
    BrickPi.MotorEnable[PORT_A] : method of object BrickPi
            When this value is set to 1 it enabels motor A to be used in the script
    
    Methods
    -------
    setup()
        This method is called to set up the Infra red sensor for use.
    
    infSen()
        This function is used to sense where the blade is and will stop giving power to the motor once it senses that the blade whent past it. This helps
        to always keep track of the blade after it moved a package onto the sorting platform.
        
    '''
    BrickPiSetup()  
    BrickPi.MotorEnable[PORT_A] = 1
    BrickPi.MotorEnable[PORT_C] = 0 #Enable the Motor C --> Wheels

    
    def setup(self):
        '''This method is called to set up the Infra red sensor for use.
            
        '''
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(3,GPIO.IN)
        
    def infSen(self):
        '''This function is used to sense where the blade is and will stop giving power to the motor once it senses that the blade whent past it. This helps
        to always keep track of the blade after it moved a package onto the sorting platform.


        '''
        while True:
            power = 210
            sens = GPIO.input(3)
            BrickPi.MotorSpeed[PORT_C] = 0
            BrickPi.MotorSpeed[PORT_A] = power  #Set the speed of MotorC (-255 to 255)
            BrickPiUpdateValues()
            if (sens == 0 ):
                break