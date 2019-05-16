from tkinter import *;
from tkinter import scrolledtext;

def Threshold():
	THRESHOLD = Tk()
	THRESHOLD.title('Threshold')
	THRESHOLD.geometry('400x200')

	lblTemperature = Label(THRESHOLD, text="Enter Temperature")
	lblTemperature.grid(column = 0, row = 0)

	txtEnterTemperature = Entry(THRESHOLD, bd = 2)
	txtEnterTemperature.grid(column = 1, row = 0)

	lblHumidity = Label(THRESHOLD, text="Enter Humidity")
	lblHumidity.grid(column = 0, row = 1)

	txtEnterHumidityr = Entry(THRESHOLD, bd = 2)
	txtEnterHumidityr.grid(column = 1, row = 1)

	btnCheckOrder = Button(THRESHOLD,text='Save', command = Calibration)
	btnCheckOrder.grid(column = 2, row = 2)

	THRESHOLD.mainloop()

def Calibration():
	CALIBRATION = Tk()
	CALIBRATION.title('Weight Calibration')
	CALIBRATION.geometry('400x200')

	lblOrderNumber = Label(CALIBRATION, text="Enter Weight")
	lblOrderNumber.grid(column = 0, row = 0)

	txtEnterOrderNumber = Entry(CALIBRATION, bd = 2)
	txtEnterOrderNumber.grid(column = 1, row = 0)

	btnCheckOrder = Button(CALIBRATION,text='Calibrate', command = Threshold)
	btnCheckOrder.grid(column = 2, row = 0)

	CALIBRATION.mainloop()

ROOT = Tk()
ROOT.geometry('400x200')
ROOT.title ('Packaging')

lblOrderNumber = Label(ROOT, text="Order Number")
lblOrderNumber.grid(column = 0, row = 0)

txtEnterOrderNumber = Entry(ROOT, bd = 2)
txtEnterOrderNumber.grid(column = 1, row = 0)

btnCheckOrder = Button(ROOT,text='Check Order', command = Calibration)
btnCheckOrder.grid(column = 2, row = 0)

txtOrderResults = scrolledtext.ScrolledText(ROOT, width = 45, height = 10)
txtOrderResults.grid(column = 0, row = 2, rowspan = 3, columnspan = 3)


ROOT.mainloop()
																		 