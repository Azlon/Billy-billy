
#8 kanaal ADC
from Drivers.ABEL.ABE_ADCPi import ADCPi
from Drivers.ABEL.ABE_helpers import ABEHelpers

#Licht en temperatuur - ADAFRUIT = OUD, ADS = Nieuw
from Drivers.ADA.Adafruit_ADS1x15.ADS1x15 import ADS1115

#Load cell ADC
from Drivers.HX711 import hx711

import math
import logging
logger = logging.getLogger('sensor.instance.log')

# Temperatuur compensatie
from graphBB.Compensatie.condcompensate import Compensation

class Sensor(object):
    '''
    Basis sensor object
    '''
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
        '''
        verwerkingsfunctie voor de actuele sensorwaarden
        :param val:
        :return:
        '''
        return val

    def read(self):
        '''
        Methode om voor elke type sensor waarden uit te lezen
        :return:
        '''
        pass

    def getvalues(self):
        '''
        Methode om de sensorwaarden verder te verwerken : toepassen van conv()
        :return:
        '''
        self.read()
        for index, item in enumerate(self.values):
            self.values[index] = self.conv(item)
        # print "Values:" + str(self.values)
        self.dict["values"] = self.values

        #print self.dict
        return self.values

    def setname(self):
        '''
        Naam die afgebeeld wordt in JSON string aanpassen
        :return:
        '''
        self.dict["name"] = self.name
        return self.dict

    def __str__(self):
        '''
        Aanroepen van klasse als string geeft alle volledig woordenboek terug.
        :return:
        '''
        return self.dict

class I2CSensor(Sensor):
    '''
    Sensor die gebruikt maakt van I2C om gegevens te verzenden
    '''
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
        '''
        Zet de adressen waarop de bus moet luisteren. Zet de woordenboek entry
        :param adds: lijst met alle hexadecimale adressen
        :return:
        '''
        self.adds = adds
        self.dict["addresses"] = self.adds

    def getaddress(self):
        '''
        Geeft alle huidige adressen terug
        :return:
        '''
        return self.adds

    def addaddress(self,add):
        '''
        Voegt een bijkomstig adres toe
        :param add: 1 hexadecimaal adres
        :return:
        '''
        self.adds.append(add)

    def extaddress(self,adds):
        '''
        Voegt meerdere adressen toe
        :param adds: lijst met adressen
        :return:
        '''
        self.adds.extend(adds)


class GPIOSensor(Sensor):
    '''
    Sensor die gebruikt maakt van de GPIO pinnen om gegevens te verzenden.
    '''
    def __init__(self,name,vallist = None, pins = None):
        super(GPIOSensor, self).__init__(name,vallist)
        self.pins = pins
        self.dict.update(dict(pins=self.pins, driver="RPi"))
        #print "DEBUG: dict gpio init " + str(self.dict)

    def setpin(self,**kwargs):
        '''
        Geeft aan welke pinnen er gebruikt worden voor gegevens overdracht
        :param args: keywoord "pins" met lijst van pinnen
        :return:
        '''
        self.pins = kwargs.get("pins")
        print "pins: " + str(self.pins)
        self.dict["pins"] = self.pins
        #print "DEBUG :(pins()) " + str(self.dict)

class Humidity(I2CSensor):
    """
    Uitbreiden van sensoren met Humidity sensors die in dit geval gebruik maakt van
    I2C, met ABEL als driver
    """
    def __init__(self, name, vallist = None, adds = None,max = 5):
        super(Humidity, self).__init__(name,vallist,adds)

        # self.max_volt = max
        self.setaddress([0x68,0x69,0x6C,0x6D])
        self.adc1 = ADCPi(self.bus, self.adds[0], self.adds[1], 12)
        self.adc2 = ADCPi(self.bus, self.adds[2], self.adds[2], 12)
        self.dict.update(dict(driver="ABEL"))
        self._depsens = None

    def read(self):
        tval = []
        #als nummering sensoren niet klopt volgens ordening lijst : Sensoren niet sequentieel op kanalen aangesloten
        for i in range(0, 8):
            tval.append(self.adc1.read_voltage(i + 1))
        for i in range(0, 4):
            tval.append(self.adc2.read_voltage(i + 1))
        self.values = tval
        self.standarize()
        # print tval
        return tval

    def standarize(self):
        #Standariseert de vochtigheidswaarden.
        if  isinstance(self._depsens,Temperature):
            c = Compensation()
            map(c.compensate,self.values)

    def adddepsens(self,sobj):
        self._depsens = sobj
class Light(I2CSensor):
    '''
    Uitbreiding met licht sensoren met I2C als protocol. De sensoren communiceren met de ADS1x1 driver.
    '''

    def __init__(self, name, vallist = None, adds = None):
        super(Light, self).__init__(name,vallist,adds)
        self.driver = ADS1115()
        self.setaddress([0x48])
        self.dict.update(dict(driver="ADS1x15"))
    def __conv(self,mvolt):
        '''
        Voorgaande conversie functie om waarden vanuit de sensor te converteren naar lux.
        Uit voorgaande testen kan intuitief afgeleid worden dat de waarden de actuele lichtintensiteit benaderen
        en er geen additionele conversie moet toegepast worden. Vervang __lux() door lux() als er toch nog een conversie moet
        plaatsvinden.
        :return:
        '''

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

    def read(self):
        tval = []
        front, back = self.driver.read_adc(3),self.driver.read_adc(1)
        tval.append(front)
        tval.append(back)
        self.values = tval
        return tval

class Temperature(I2CSensor):
    '''
    Klasse om temperatuur uit te lezen via I2C protocol
    '''
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
        """
        Conversie functie zoals beschreven in
        :param mvolt:
        :return:
        """
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
    """
    Klasse om de gewichtsensor te initialiseren. De HX711 driver communiceert met  GPIO volgens het tijdschema die in de datasheet beschreven staat.
    (https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf)
    Om reele massa's te bepalen, moet de gewichtsensor eerst gekalibreerd worden.

    """
    def __init__(self,name,vallist = None, pins = None):
        super(Weight, self).__init__(name,vallist,pins)
        self.setpin(22,27)
        # pinnen staan naast elkaar
        self.amp = hx711.HX711(self.pins[0],self.pins[1])
        self.amp.set_reading_format("LSB", "MSB")

        #kalibratie is onbruikbaar bij andere gain instellingen (128 : 225,239, 64: ? , 32: ?)
        #linaire verhouding tussen gain/ referenties?
        self.amp.set_reference_unit(225.239)
        self.amp.set_offset(50)
        self.amp.reset()
        self.amp.tare()
        # referentie is nog niet geweten
        self.dict.update(driver = "HX711")
        #print "DEBUG: init weight DICT " + str(self.dict)
    def calibrate(self,offset, ref= 225.239,):
        '''
        Kalibreer process : reference unit op 1 instellen, bepalen of de sensor zonder gewicht een nulmeting teruggeeft.
        Zoniet stel de offset op de afwijkende waarde in. Een gekend gewicht wordt aan de sensor gehangen en de opeenvolgende conversies
        noteren. (vb m = gewicht in gram, v = output hx711.
            massa in gram ref = v/m, in kilogram ref = v*1000/m enz.

        :param ref: referentie per gewichteenheid
        :param offset: offset bij gewichtloze meting
        :return:
        '''
        self.amp.set_reference_unit(ref)
        self.amp.set_offset(offset)
        self.amp.reset()
        self.amp.tare()

    def reset(self):
        '''
        Aan en uitschakelen van de HX711
        :return:
        '''
        self.amp.reset()
        self.amp.tare()

    def getweight(self):
        '''
        Methode geeft directe gewicht respresentatie terug
        :return: gewicht volgens kalibratie
        '''
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

