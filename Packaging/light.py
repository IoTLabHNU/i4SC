import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN)	#Digital
GPIO.setup(3, GPIO.IN)	#Analog

while True:
    if GPIO.input(2) == 1:
        print ("LIGHT 1")
        time.sleep(1)
    elif GPIO.input(2) == 0:
        print ("LIGHT 0")
        time.sleep(1)
    
    print("Analogo: {0}".format(GPIO.input(3)))

