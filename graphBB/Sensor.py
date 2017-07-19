try:
    #8 kanaal ADC
    from Drivers.ABEL.ABE_ADCPi import ADCPi
    from Drivers.ABEL.ABE_helpers import ABEHelpers
    #Licht en temperatuur - ADAFRUIT = OUD, ADS = Nieuw
    # from Drivers.ADA.Adafruit_ADS1x15 import ADS1x15,Adafruit_I2C
    from Drivers.ADA.Adafruit_ADS1x15.ADS1x15 import ADS1115

    #Load cell ADC
    from Drivers.HX711 import hx711
    import RPi.GPIO as GPIO
    import math
except ImportError as e:
    print e

import logging
logger = logging.getLogger('sensor.instance.log')


class Sensor(object):
    def __init__(self,name,vallist = None):
        # print "BASE SENSOR CLASS CALLED"
        # print name
        if vallist and isinstance(vallist,list):
            self.values = vallist
        else:
            self.values = []
        self.name = name

        self.dict = dict(values= self.values, name = self.name)
        # print self.dict

    def conv(self,val):
        return val

    def read(self):
        pass

    def getvalues(self):
        self.read()
        for index, item in enumerate(self.values):
            self.values[index] = self.conv(item)
        # print "Values:" + str(self.values)
        self.dict["values"] = self.values
        #print self.dict
        return self.values

    def setname(self):
        self.dict["name"] = self.name
        return self.dict

    def __str__(self):
        return self.dict

class I2CSensor(Sensor):
    def __init__(self,name, vallist = None, adds = None):
        super(I2CSensor, self).__init__(name,vallist,)
        self.channels = []
        if vallist:
            self.adds = adds
        else:
            self.adds = []

        self.dict.update(dict(addresses=self.adds))
        try:
            self.helper = ABEHelpers()
            self.bus = self.helper.get_smbus()


        except Exception as e:
            logger.critical('I2C sensor not properly instantiated: ' + str(e))
            print e


    def setaddress(self,adds):
        self.adds = adds
        self.dict["addresses"] = self.adds

    def getaddress(self):
        return self.adds

    def addaddress(self,add):
        self.adds.append(add)

    def extaddress(self,adds):
        self.adds.extend(adds)


class GPIOSensor(Sensor):
    def __init__(self,name,vallist = None, pins = None):
        super(GPIOSensor, self).__init__(name,vallist)
        self.pins = pins
        self.dict.update(dict(pins=self.pins, driver="RPi"))
        #print "DEBUG: dict gpio init " + str(self.dict)

    def setpin(self,*args):
        self.pins = args
        print "pins: " + str(self.pins)
        self.dict["pins"] = self.pins
        #print "DEBUG :(pins()) " + str(self.dict)

class Humidity(I2CSensor):
    def __init__(self, name, vallist = None, adds = None,max = 5):
        super(Humidity, self).__init__(name,vallist,adds)

        self.max_volt = max
        self.setaddress([0x68,0x69,0x6C,0x6D])
        self.adc1 = ADCPi(self.bus, self.adds[0], self.adds[1], 12)
        self.adc2 = ADCPi(self.bus, self.adds[2], self.adds[2], 12)
        self.dict.update(dict(driver="ABEL"))


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
        # print tval
        return tval


class Light(I2CSensor):
    def __init__(self, name, vallist = None, adds = None):
        super(Light, self).__init__(name,vallist,adds)

        self.driver = ADS1115()
        self.setaddress([0x48])

        self.dict.update(dict(driver="ADS1x15"))



    # def conv(self, mvolt):
    #     # This conversion is not accurate!!
    #
    #     try:
    #         # volt = millivolt / 1000
    #
    #         # formula found on http://emant.com/316002.page
    #         # this formula is not accurate!!
    #         # lux = -(((2500 / volt) - 500) / 3.3) + 40000
    #
    #         lux = (mvolt / 50) * 10000
    #         return abs(lux)
    #     except Exception as e:
    #         print "Light conversion error; " + str(e)

    def read(self):
        tval = []
        front, back = self.driver.read_adc(3),self.driver.read_adc(1)
        tval.append(front)
        tval.append(back)
        self.values = tval
        return tval

class Temperature(I2CSensor):
    def __init__(self, name, vallist = None, adds = None):
        super(Temperature, self).__init__(name, vallist, adds)
        self.driver = ADS1115()
        self.setaddress([0x48])
        self.dict.update(driver="ADS1x15")


    def read(self):
        tval = []
        temp = self.driver.read_adc(0)
        tval.append(temp)
        self.values = tval
        return tval

    def conv(self,mvolt):
        # This conversion is not accurate!!
            try:
                volt = mvolt / 1000
                resistance = volt / (3.3 - volt)  # hier nog opvangen wanneer spanning exact 3.3V is
                temperature = abs(resistance)  # mag niet negatief zijn anders valueerrror
                temperature = math.log(temperature)
                temperature /= 3570  # aangepast voor laatste versie smd ntc
                temperature += 1 / (25 + 273.15)
                temperature = 1 / temperature
                temperature -= 273.15
                # print "temperatuur", math.ceil(temperature * 100) / 100
                temperature = math.ceil(temperature * 10) / 10
                temperature -= 2

                return temperature
            except ZeroDivisionError:
                return -1
            except Exception as exc:
                print "Temperature conversion error; " + str(exc)



class Weight(GPIOSensor):
    def __init__(self,name,vallist = None, pins = None):
        super(Weight, self).__init__(name,vallist,pins)

        self.setpin(22,27)
        # pinnen staan naast elkaar , naast ground
        self.amp = hx711.HX711(self.pins[0],self.pins[1])
        self.amp.set_reading_format("LSB", "MSB")
        self.amp.set_reference_unit(183.33)
        self.amp.reset()
        self.amp.tare()
        # referentie is nog niet geweten
        self.dict.update(driver = "HX711")
        #print "DEBUG: init weight DICT " + str(self.dict)


    def getweight(self):
        if len(self.values)>1:
            raise Exception("Only one weight value expected")
        return self.getvalues()[0]

    def read(self,times = 3):
        tval  = []
        tval.append(self.amp.get_weight(times))
        self.values = tval
        # print "READ method weight sensor : " + str(self.values)
        # print "DEBUG: dict (read())" + str(self.dict)
        return tval

    def calibrate(self):
        pass
