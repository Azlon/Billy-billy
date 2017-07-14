try:
    #8 kanaal ADC
    from Drivers.ABEL import ADCPi
    from Drivers.ABEL import ABEHelpers
    #Licht en temperatuur - ADAFRUIT = OUD, ADS = Nieuw
    # from Drivers.ADA.Adafruit_ADS1x15 import ADS1x15,Adafruit_I2C
    from Drivers.ADA.Adafruit_ADS1x15.ADS1x15 import ADS1115
    #Load cell ADC
    from Drivers.HX711 import hx711
    import RPi.GPIO as GPIO
except ImportError as e:
    print e

import json
import time

#todo: superklass mksjson klopt?

class Sensor(object):
    def __init__(self,name,vallist = None):
        if vallist and isinstance(list,vallist):
            self.values = vallist
        else:
            self.values = []
        self.name = name
        self.dict = dict(values= self.values, name = self.name)

    def conv(self,val):
        return val

    def read(self):
        pass

    def getvalues(self):
        self.read()
        for i in self.values:
            self.values[i] = self.conv(i)

    def mkjson(self):
        return json.dumps(self.dict)

    def __str__(self):
        return self.mkjson()

class I2CSensor(Sensor):
    def __init__(self,name, vallist = None, adds = None):
        super(I2CSensor, self).__init__(vallist,name,)
        self.channels = []
        if vallist and isinstance(list,adds):
            self.adds = adds
        else:
            self.adds = []

        try:
            self.helper = ABEHelpers()
            self.bus = self.helper.get_smbus()


        except Exception as e:
            print e



    def setaddress(self,adds):
        self.adds = adds
    def getaddress(self):
        return self.adds
    def addaddress(self,add):
        self.adds.append(add)
    def extaddress(self,adds):
        self.adds.extend(adds)

    def mkjson(self):
        self.dict = self.dict.update(dict(addresses =  self.adds))
        return self.mkjson()

class GPIOSensor(Sensor):
    def __init__(self,name,vallist = None, mode = None, pins = None):
        super(GPIOSensor, self).__init__(vallist,name)
        self.mode = mode
        self.pins = pins
        if self.mode:
            self.setmode("BCM")
        else:
            self.setmode("BOARD")
        if self.pins:
            self.pin = []

    def setmode(self,mode):
        if mode == "BCM":
            self.mode =  self.mode = GPIO.setmode(GPIO.BSM)
        elif  mode == "BOARD":
            self.mode = self.mode = GPIO.setmode(GPIO.BOARD)

    def setpin(self,*args):
        self.pins = args

    def mkjson(self):
        self.dict = self.dict.update(dict(pins = self.pins, mode= self.mode, driver = "RPi"))
        return self.mkjson()

class Humidity(I2CSensor):
    def __init__(self, name, vallist = None, adds = None,max = 5):
        super(Humidity, self).__init__(name,vallist,adds)
        self.max_volt = max
        adds = [0x68,0x69,0x6C,0x6D]
        self.setaddress(adds)

        self.adc1 = ADCPi(self.bus, self.adds[0], self.adds[1], 12)
        self.adc2 = ADCPi(self.bus, self.adds[2], self.adds[2], 12)

    def read(self):
        '''
        leest spanning van ABEL adc en schrijft in list
        :return:
        '''
        tval = []
        for i in range(0, 8):
            tval.append(self.adc1.read_voltage(i + 1))
        for i in range(0, 4):
            tval.append(self.adc2.read_voltage(i + 1))
        self.values = tval
        return tval

    def mkjson(self):
        self.dict = self.dict.update(dict(driver = "ABEL"))
        return self.mkjson()

class Light(I2CSensor):
    def __init__(self, name, vallist = None, adds = None):
        super(Light, self).__init__(name,vallist,adds)
        self.driver = ADS1115()
        self.adds = [0x48]



    def read(self):
        tval = []
        front, back = self.driver.read_adc(3),self.driver.read_adc(1)
        tval.append(front)
        tval.append(back)
        self.values = tval
        return tval

    def mkjson(self):
        self.dict = self.dict.update(dict(driver = "ADS1x15"))
        return self.mkjson()

class Temperature(I2CSensor):
    def __init__(self, name ,vallist = None, adds = None):
        super(Temperature, self).__init__(name, vallist, adds)
        self.driver = ADS1115()

    def read(self):
        tval = []
        temp = self.driver.read_adc(0)
        tval.append(temp)
        self.values = tval
        return tval

    def conv(self,mvolt):
        # This conversion is not accurate!!

        try:
            # volt = millivolt / 1000

            # formula found on http://emant.com/316002.page
            # this formula is not accurate!!
            # lux = -(((2500 / volt) - 500) / 3.3) + 40000

            lux = (mvolt / 50) * 10000
            return abs(lux)
        except Exception as e:
            print "Light conversion error; " + str(e)

    def mkjson(self):
        self.dict = self.dict.update(driver = "ADS1x15")

class Weight(GPIOSensor):
    def __init__(self,name,vallist = None, mode = None, pins = None):
        super(Weight, self).__init__(name,vallist,mode,pins)
        self.pins = [19,26]
        # pinnen staan naast elkaar , naast ground
        self.amp = hx711.HX711(self.pins[0],self.pins[1])

        # referentie is nog niet geweten
        self.amp.set_reference_unit(1)

    def getweight(self):
        if len(self.values)>1:
            raise Exception("Only one weight value expected")
        return self.getvalues()[0]

    def read(self,times = 3):
        tval = []
        self.values.append(self.amp.get_weight(times))

    def calibrate(self):
        pass


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

