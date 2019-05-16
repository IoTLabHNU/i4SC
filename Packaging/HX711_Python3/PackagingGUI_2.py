import RPi.GPIO as GPIO ;
import mysql.connector;
import time, datetime
import uuid, os, sys

from tkinter import *;
from tkinter import scrolledtext;
from tkinter import messagebox;
from hx711 import HX711  # import the class HX711
from mfrc522 import SimpleMFRC522

class Packaging():
    """
    This class write the order number to the RFID tag and update the database information about the order.

    Attribute
        @packageWeight
        @CALIBRATION (Tkinter Window): For calibrating the weight scale.
        @THRESHOLD (Tkinter Window): For entering the desired thresholds.
        @ROOT (Tkinter Window): The main window to check if the order exist.
        @cnx (MySQL Connection): Connection to MySQL database on the server.
    """
    packageWeight = -1;

    #WINDOWS
    CALIBRATION = None;
    THRESHOLD = None;
    ROOT = None;

    #MySQL
    cnx = None;

    #WIDGETS
    txtEnterOrderNumber = None;
    txtOrderResults = None;
    txtEnterHumidity = None;
    txtEnterTemperature = None;


    #RFID
    reader = None;

    def Threshold(self):
        """
        This function display the "THRESHOLD" window for an user to enter the desired temperature.

        @txtEnterTemperature (entry): The threshold temperature entry field.
        @txtEnterHumidity (entry): The threshold humidity entry field.
        """
        self.THRESHOLD = Tk()
        self.THRESHOLD.title('Threshold')
        self.THRESHOLD.geometry('400x200')

        lblTemperature = Label(self.THRESHOLD, text="Enter Temperature")
        lblTemperature.grid(column = 0, row = 0)

        self.txtEnterTemperature = Entry(self.THRESHOLD, bd = 2)
        self.txtEnterTemperature.grid(column = 1, row = 0)

        lblHumidity = Label(self.THRESHOLD, text="Enter Humidity")
        lblHumidity.grid(column = 0, row = 1)

        self.txtEnterHumidity = Entry(self.THRESHOLD, bd = 2)
        self.txtEnterHumidity.grid(column = 1, row = 1)

        btnSave = Button(self.THRESHOLD, text="Save", command = self.destroy)
        btnSave.grid(column = 1, row = 2)

        self.THRESHOLD.mainloop()

    def destroy(self):
        """
        This function start by writing the order number to the tag, then save the inserted threshold values to the database.

        @reader (SimpleMFRC522): RFID tag reader and writer.
        """
        try:
            self.reader.write(self.txtEnterOrderNumber.get())
        except:
            messagebox.showerror("Threshold","Error: {0}\n\t\t{1}\n\t\t{2}".format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
        finally:
            try:
                cursor = self.cnx.cursor();
                query = "INSERT INTO `packaging` (`customerorder`, `maximumThresholdTemperature`, `maximumThresholdHumidity`, `weight`) VALUES(%s, %s, %s, %s);";
                result = cursor.execute(query, (self.txtEnterOrderNumber.get(), self.txtEnterTemperature.get(), self.txtEnterHumidity.get(), self.packageWeight,))
                self.cnx.commit()
            finally:
                messagebox.showinfo("Done", "The package is ready for delivery")

                if(self.cnx.is_connected()):
                    cursor.close()

        self.THRESHOLD.destroy()

    def Calibration(self):
        """
        This function reading in the package weight and write the order number to RFID tag.
        Finally, it will envoke "Threshold" function

        @hx (HX711): the weight scale;
        @reader (SimpleMFRC522): RFID tag reader and writer.
        """
        try:
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
                ratio = 431.7388535031847
                hx.set_scale_ratio(ratio)  # set ratio for current channel
            else:
                print('invalid data', reading)

            time.sleep(3)
            if messagebox.askyesno("Question","Is the Package on the Scale?") == True:
                self.packageWeight = "{0:.2f} Grams".format(hx.get_weight_mean())
            else:
                pass
        except:
            messagebox.showerror("{0}".format(sys.exc_info()[0]), "- {0}\n- {1}".format(sys.exc_info()[1], sys.exc_info()[2]));
        finally:
            GPIO.cleanup()
            try:
                self.reader = SimpleMFRC522()
                id, rfidtext = self.reader.read()

                cursor = self.cnx.cursor();
                query = "INSERT INTO `rfid` (`uid`) VALUES(%s);";
                result = cursor.execute(query, (id,))
                self.cnx.commit()
            finally:
                GPIO.cleanup()
                try:
                    self.reader = SimpleMFRC522()
                    id, rfidtext = self.reader.read()
                    try:
                        cursor = self.cnx.cursor();
                        query = "INSERT INTO `rfid` (`uid`) VALUES(%s);";
                        result = cursor.execute(query, (id,))
                        self.cnx.commit()
                    except:
                        pass
                finally:
                    self.Threshold()

    def CheckOrderOnDatabase(self):
        """
        This function retrieve the entered order number from a textfield, then check if it exist on the database.
        It will show an error messagebox if the order number does not exist. Contrarily, it will display the contents on a textfield.
        Finally, it will invoke the "Calibration" function.
        """
        try:
            #Connection to MySQL
            self.cnx = mysql.connector.connect(user='pi2', password='password',
                                          host='10.49.63.147',
                                          port='3306',
                                          database='box')
            cursor = self.cnx.cursor(dictionary=True);
            query = "SELECT * FROM `customerorder` WHERE ordernumber=%s;";
            cursor.execute(query, (self.txtEnterOrderNumber.get(),))
            results = cursor.fetchall()

            if len(results) > 0:
                query = "SELECT `name` FROM `customer` WHERE idcustomer=%s;";
                cursor.execute(query, (results[0]['customer'],))
                customer = cursor.fetchone()
                self.txtOrderResults.insert(INSERT, "The Order: {0}, made by Customer: {1}, is found with the following product/s\n".format(self.txtEnterOrderNumber.get(), customer['name']))

                count = 1; total = 0;
                self.txtOrderResults.insert(INSERT,"NAME\t\t\tPRICE\n")
                for row in results:
                    query = "SELECT * FROM `productitems` WHERE idproductitems=%s;";
                    cursor.execute(query, (row['productitems'],))
                    product = cursor.fetchone()
                    total += product['price']
                    self.txtOrderResults.insert(INSERT, "{0} {1},\t{2}\n".format(count, product['name'], product['price']))
                    count = +1
                self.txtOrderResults.insert(INSERT, "\n\nTOTAL: {0}".format(total))
            else:
                messagebox.showerror("Check Database", "Order: {0}, was not found!".format(self.txtEnterOrderNumber.get()))
        except:
            self.cnx.rollback()
            messagebox.showerror("Check Database","Error: {0}\n\t\t{1}\n\t\t{2}".format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
        finally:
                self.Calibration();

    def Main(self):
        """
        This function initialise the main window with labels, button, and entry field.

        @ROOT (window): TKinter window with '400x200' scale.
        @btnCheckOrder (entry): The button to invoke "CheckOrderOnDatabase" function
        @txtOrderResults (entry): A text field to display the content of the order
        """
        self.ROOT = Tk()
        self.ROOT.geometry('400x200')
        self.ROOT.title('Packaging')

        lblOrderNumber = Label(self.ROOT, text="Order Number")
        lblOrderNumber.grid(column = 0, row = 0)

        self.txtEnterOrderNumber = Entry(self.ROOT, bd = 2)
        self.txtEnterOrderNumber.grid(column = 1, row = 0)

        btnCheckOrder = Button(self.ROOT,text='Check Order', command = self.CheckOrderOnDatabase)
        btnCheckOrder.grid(column = 2, row = 0)

        self.txtOrderResults = scrolledtext.ScrolledText(self.ROOT, width = 45, height = 10)
        self.txtOrderResults.grid(column = 0, row = 2, rowspan = 3, columnspan = 3)

        self.ROOT.mainloop()

if  __name__ == '__main__':
    try:
        P = Packaging();
        P.Main()
    except (KeyboardInterrupt, SystemExit):
        messagebox.showinfo('End','Bye')
