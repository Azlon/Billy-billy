try:

    from ABE_helpers import ABEHelpers
    from ABE_ADCPi import ADCPi
except ImportError as e:
    print e
import threading



class sensthread(threading.Thread):
    """
    Thread vangt alle waarden op en plaatst ze in een list (1 - 12 sensoren)
    """
    def __init__(self,list,adc1, adc2):

        super(sensthread, self).__init__()
        self.values = list
        self.adc1 = adc1
        self.adc2 = adc2

    def run(self):
        """
        Runnen van de thread : sequentieel spanning opmeten van kanalen
        :return:
        """
        intval =
        #Per intverval of continu?
        try:
            for i in range(1,9):
                self.values[i] = self.adc1.read_voltage[i]
            for i in range(9,13):
                self.values[i] = self.adc2.read_voltage[i]

        except Exception as e:
            print e

class Boards:
    """
    initialiseren van het bord met de bijhorende ADC driver
    :param list: lijst waarin de vochtigheidswaarden in geplaatst worden
    :param adc1: Eerste bord met 8 kanalen (2 i2C addressen)
    :param adc2: Tweede bord met 8 kanelen, waar maar 4 van nodig zijn (8 + 4 = 12)
    """
    def __init__(self):
        i2c_helper = ABEHelpers()
        bus = i2c_helper.get_smbus()

        # Board 1
        self.addr1 = 0x68
        self.addr2 = 0x69
        self.b1 = ADCPi(bus, self.addr1, self.addr2, 12)
        # Board 2
        self.addr3 = 0x6A
        self.addr4 = 0x6B
        self.b2 = ADCPi(bus, self.addr3, self.addr4, 12)

        self.values = [0 for i in range(1,13)]
        self.startthread()

    def setAddresstuple(self,adr1, adr2,id):
        """
        De i2c addressen van de twee borden aanpassen (ook jumpers moeten veranderd worden)
        :param adr1: adress voor eerste ic (MCP3424)
        :param adr2:adress voor tweede ic (MCP3424)
        :param id: bord identificatie
        :return:
        """
        if id == 1:
            self.b1.__address = adr1
            self.b1.__address = adr2
        elif id == 2:
            self.b2.__address = adr1
            self.b2.__address = adr2
        else:
            print "Maar twee borden beschikbaar (verander ID)"

    def getvalues(self):
        """
        Lijst, die continue aangepast wordt door de thread terugeven
        :return: Sensor metingen
        """
        return self.values

    def startthread(self):
        """
        Starten van de thread
        :return:
        """
        sensthread.start()
