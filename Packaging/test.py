import RPi.GPIO as GPIO
import time

LightSensorDigital = 2
LightSensorAnalog = 3
GreenLight = 1
RedLight = 17



def destroy():
	GPIO.output(RedLight, GPIO.LOW) 
	GPIO.cleanup()                     # Release resource

if __name__ == '__main__':     # Program start from here

	try:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(LightSensorDigital, GPIO.IN)	#Digital
		GPIO.setup(LightSensorAnalog, GPIO.IN)	#Analog

		GPIO.setup(GreenLight, GPIO.OUT)
		GPIO.output(GreenLight, GPIO.HIGH) 


		GPIO.setup(RedLight, GPIO.OUT)   
		GPIO.output(RedLight, GPIO.HIGH) 

		GPIO.output(GreenLight, GPIO.HIGH) 
		GPIO.output(RedLight, GPIO.HIGH) 
	

		while True:
			if GPIO.input(2) == 1:
				print ("LIGHT 1")
				time.sleep(1)
			elif GPIO.input(2) == 0:
				print ("LIGHT 0")
				time.sleep(1)

			print("Analog: {0f}".format(GPIO.input(3)))
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()