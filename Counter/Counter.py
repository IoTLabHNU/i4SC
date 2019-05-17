"""
This Python Script uses a light emmitter (laser) and a light detector sensor [Dual Comperator and laser emmitter modules HW-483]
"""
import RPi.GPIO as GPIO
import time
from sense_hat import SenseHat

alert_led = 18
light_sensor = 4
counter=0
sense = SenseHat()

def setup():
        """
        This function sets up the GPIO pins to BCM mode and sets GPIO pin 4 for input GPIO pin 18.
        :return: nothing
        """
        GPIO.setmode(GPIO.BCM)                  # Numbers GPIOs by BCM pinout
        GPIO.setup(light_sensor,GPIO.IN)        # Set light_sensor pin mode as input
        GPIO.setup(alert_led,GPIO.OUT)

def loop():
        """
        This function counts the number of items/objects that pass past the laser light.
        :return: number of items that passed past the laser
        """ 
        prev = False
        current = False
        global counter
        print ('Counter Program now running')
        while True:
                prev = current
                output = bool(GPIO.input(light_sensor))
                
                current = output

                if ((current==True) and (prev ==False)):        #if values switch between True and a False, one object has passed
                        counter=counter+1
                        print ('Counting in Progress '+ str(counter))
                        sense.show_message(str(counter),scroll_speed=0.02)
                
                if output:
                        GPIO.output(alert_led,GPIO.HIGH)       #switch alert led ON      
                else:
                        GPIO.output(alert_led,GPIO.LOW)

        return (counter)

def resetCounter():
        """
        This function resets the counter to zero.
        :return: nothing
        """ 
        counter = 0
        
def destroy():
         """
        This function clears up the GPIO pins
        :return: nothing
        """
         GPIO.cleanup()                     # Release resources

if __name__ == '__main__':     # Program start from here
        setup()
        try:
                loop()
        except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
                destroy()
                print('Total is :'+ str(counter))
