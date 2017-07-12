import Adafruit_ADS1x15.ADS1x15 as adc
import threading
import time
CH = 1
GAIN= 1
DR = 128
dt = 0.5
#
#meerdere adc = default adres aanpassen?

class genvaluesThread(threading.Thread):
    def __init__(self):
        super(genvaluesThread,self).__init__()
        self.active = False
        self.dt = 0.5

    def activate(self):
        self.active = True

    def interval(self,intval):
        self.dt = intval

    def run(self):
        print "started measuring"
        if self.active:
            gen = adc.ADS1115()
            gen.start_adc(channel=CH, gain=GAIN, data_rate=DR, )
            while self.active:
                for i in range(0,3):
                    gen.read_adc(i,GAIN)
                time.sleep(self.dt)
            gen.stop_adc()
