try:
    #8 kanaal ADC
    from Drivers.ABEL import ADCPi
    from Drivers.ABEL import ABEHelpers
    #Licht en temperatuur
    from Drivers.ADA.Adafruit_ADS1x15 import ADS1x15,Adafruit_I2C
    #Load cell ADC
    from Drivers.HX711 import hx711
except ImportError as e:
    print e

import json
import time

class SensorManager:
    """
    Klasse die de verbinding tussen de sensoren maakt.

    """
    #todo: Klasse refactoren zodat sensoren beter toegevoegd kunnen worden

    def __init__(self, list = None,sensors = 12):
        """
        zet de adressen van I2C, inititaliseert driver van TAL220
        :param list: lijst met sensoren
        :param sensors: aantal humidity sensoren
        """
        self.max_volt = 5
        self.readings = list
        if not self.readings:
            self.readings = [None for i in range(0, sensors)]

        self.num_sensors = sensors
        self.addr1_board1 = 0x68
        self.addr2_board1 = 0x69

        self.addr1_board2 = 0x6C
        self.addr2_board2 = 0x6D

        #pinnen staatn naast elkaar , naast ground
        self.amp = hx711.HX711(19,26)
        #referentie is nog niet geweten
        self.amp.set_reference_unit(1)

        try:
            i2c_helper = ABEHelpers()
            bus = i2c_helper.get_smbus()
            self.adc1 = ADCPi(bus, self.addr1_board1, self.addr2_board1, 12)
            self.adc2 = ADCPi(bus, self.addr1_board2, self.addr2_board2, 12)
        except Exception as e:
            print e

    def getvalues(self):
        """
        Haalt up-to-date values op
        :return:
        """
        self.__get_readings()
        return self.readings


    def getsizesensorlist(self):
        '''
        Lijst met alle sensoren
        :return:
        '''
        return self.num_sensors

    def capture(self,filename =' humidity_sensor.txt',int_val=0.5):
        '''
        schrijft file weg met vochtigheidswaarden, timestamp en gewicht
        :param filename: bestandsnaam
        :param int_val: sample tijd
        :return:
        '''
        history = []
        row = {}
        try:
            while 1:
                intval = int_val
                row['value'] = self.getvalues()
                # convert to json
                row['time'] = time.strftime("%d-%m-%y  %H:%M:%S")

                #todo : commentaar weglaten als gewicht in orde is
                #row['gewicht'] = self.getweight()
                history.append(json.dumps(row) + "\n")
                print row
                time.sleep(intval)

        except KeyboardInterrupt as e:
            with open(filename, 'w') as file:
                    file.writelines(history)
            print "Data saved"

    def playback(self,filename,intval = 1):
        '''
        Haalt JSON waarden uit een bestand en geeft dictionnary terug.
        :param filename:
        :param intval:
        :return:
        '''
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
        '''
        leest spanning van ABEL adc en schrijft in list
        :return:
        '''
        for i in range(0,8):
            self.readings[i] = self.adc1.read_voltage(i+1)
        for i in range(0, 4):
            self.readings[8+i] = self.adc2.read_voltage(i+1)

    def getweight(self):
        '''
        Haalt gewicht van load cell op
        :return:
        '''
        pass
        # self.amp.get_weight(2)

    def changeaddress(self,ad1,ad2,ad3,ad4):
        '''
        Verandert de I2C adressen waarop de ABEL ADC naartoe schrijft
        :param ad1:
        :param ad2:
        :param ad3:
        :param ad4:
        :return:
        '''
        self.addr1_board1 = ad1
        self.addr2_board1 = ad2

        self.addr1_board2 = ad3
        self.addr2_board2 = ad4

if __name__ == "__main__":
    manager = SensorManager()
    manager.capture()

    #write to file

