try:
    from ABE_ADCPi import ADCPi
    from ABE_helpers import ABEHelpers
except ImportError as e:
    print e
import time
import datetime
from time import gmtime,strftime
import os
import csv
import json
import TAL220



class SensorManager:
    def __init__(self, list = None,sensors = 12):
        self.max_volt = 5
        self.readings = list
        if not self.readings:
            self.readings = [None for i in range(0, sensors)]


        self.num_sensors = sensors

        self.addr1_board1 = 0x68
        self.addr2_board1 = 0x69

        self.addr1_board2 = 0x6C
        self.addr2_board2 = 0x6D

        self.w_readings = [0] * 2
        self.loadcell = TAL220.TAL220(self.max_volt)
        self.loadcell.setcalibration(0.5)


        try:
            i2c_helper = ABEHelpers()
            bus = i2c_helper.get_smbus()
            self.adc1 = ADCPi(bus, self.addr1_board1, self.addr2_board1, 12)
            self.adc2 = ADCPi(bus, self.addr1_board2, self.addr2_board2, 12)
        except Exception as e:
            print e

    def getvalues(self):
        self.__get_readings()
        return self.readings

    def getwvalues(self):
        self.__getwreadings()
        return self.w_readings

    def getsizesensorlist(self):
        return self.num_sensors

    def capture(self,filename =' humidity_sensor.txt',int_val=0.5):
        history = []
        row = {}
        try:
            while 1:
                intval = int_val
                row['value'] = self.getvalues()
                # convert to json
                row['time'] = time.strftime("%d-%m-%y  %H:%M:%S")
                history.append(json.dumps(row) + "\n")
                print row
                time.sleep(intval)

        except KeyboardInterrupt as e:
            with open(filename, 'w') as file:
                    file.writelines(history)
            print "Data saved"

    def playback(self,filename,intval = 1):
        total = []
        try:
            with open(filename, 'r') as file:
                for line in file:
                    # print line
                    total.append(line)
                    # time.sleep(intval)
            return total
        except Exception as e:
            print e

    def __get_readings(self):
        for i in range(0,8):
            self.readings[i] = self.adc1.read_voltage(i+1)
        for i in range(0, 4):
            self.readings[8+i] = self.adc2.read_voltage(i+1)

    def __getwreadings(self):
        for i in range(0, 2):
            self.w_readings[i] = self.adc2.read_voltage(5 + i)

    def getweight(self):
        wvals = self.getwvalues()
        kg = self.loadcell.voltage_to_weight(abs(wvals[0] - wvals[1]))
        print "Weight in kg: " + str(kg)
        return kg

    def changeaddress(self,ad1,ad2,ad3,ad4):
        self.addr1_board1 = ad1
        self.addr2_board1 = ad2

        self.addr1_board2 = ad3
        self.addr2_board2 = ad4

if __name__ == "__main__":
    manager = SensorManager()
    manager.capture()

    #write to file

