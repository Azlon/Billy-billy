'''
nuttige links :
    http://forum.arduino.cc/index.php?topic=203198.0
    http://www.growcontrol.com/
    https://www.reagecon.com/pdf/technicalpapers/Effect_of_Temperature_TSP-07_Issue3.pdf

basis :
De conductiviteit van het water verandert bij temperatuurschommelingen
door de grotere / kleinere dissociatie van water en verder oplossing van mineralen
waardoor meer ionen vrijkomen.
De standaard oplossing om de temperatuurschommeling te compenseren is
door de conductiviteit bij een zekere temperatuur naar de conductiviteit van 25 C
terug te brengen.
Er zijn twee mogelijke manieren om te correleren: lineair of niet -lineair
. Bij een niet lineaire correlatie tussen conductiviteit en temperatuur wordt
er aangenomen dat voor elke incrementatie van temperatuur, de conductiviteit
in verhouding zal toenemen. Uit voorgaande emperische waarnemingen is gebleken dat voor
drinkwater dat de conductiviteit 2% verandert per graad C. (0.02 / C).


'''
import logging
import numpy
import time

from  graphBB.Sensor import Temperature,Humidity

tsensor = Temperature("Core temperature")
hsensor = Humidity("Humidity")

__LOGNAME__ = "Innerpotlog.log"
__LOGDIR__ = "/log/" + __LOGNAME__
__LOGMAXBYTES__ = 50000

class Compensation:
    def __init__(self):
        try:
            #initialiseren van de logger
            self.corelog = logging.getLogger("core.temphumlog")
            self.corelog.setLevel(logging.DEBUG)
            rfl = logging.handlers.RotatingFileHandler(__LOGDIR__, max)
            rfl.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.corelog.addHandler(rfl)
        except Exception as e:
            print "No logger available: " + str(e)
        self.tvc = 0.0185

    #todo: script schrijven om telkens humidity waarden terug te brengen naar die van 25 graden.
    def compensate(self,temp,hum):
        #basis formule om de temperatuur naar 25 C terug te brengen
        return hum / (1 + self.tvc * (temp-25))

    #opstellen van temperature/ conductiviteit coefficient
    def __calcTVCgraph(self,tflag = False,degree = 1):
        temp = []
        try:
            i = 0
            mes = "Monitoring temperature - humidity values, press ctrl+c to proceed to applying gradient to actual sensor"
            print mes
            self.corelog.info(mes)
            try:
                while 1:
                    i = i + 1
                    th = (tsensor.getvalues()[0],hsensor.getvalues()[0])
                    temp.append(th)
                    self.corelog.info("{i}:{tuple} at {time} ".format(i = i,tuple = str(th),time = time.strftime(time.time(),"%H:%M")))
                    time.sleep(0.5)
            except Exception as e:
                self.corelog.warning("Sensors are unavailable: " + str(e))
                print e
        except KeyboardInterrupt:
            x,y = zip(temp)
            x = numpy.asarray(x)
            y = numpy.asarray(y)
            z = numpy.polyfit(x,y,degree)
            return numpy.poly1d(z)

    def getgradient(self):
        #process starten om coefficient te bepalen
        z = self.__calcTVCgraph()[0]
        if len(z) == 2:
            print "Linear approximation"
            print "TVC : " + str(z[0])
            self.tvc = z
        return z

    def main(self):
        #toepassen van de coefficient op verdere metingen
        self.getgradient()
        while 1:
            x = tsensor.getvalues()
            y = hsensor.getvalues()
            newy = self.compensate(x,y)
            mes = "Compensated humidity (at {old} at {temp} degrees is {new}".format(old =y, temp = x, new = newy)
            self.corelog.info(mes)


if __name__ == "__main__":
    c = Compensation()
    c.main()




