#temperature compensensatie via K25 = (Kt) / (1 + 0.019 (t - 25)

    #wat is de temperature compensation value voor de potgrond?
    #uitgaan van lineaire compensatie
    #conductiviteit van vochtigheidssensor nauwkeurig genoeg?
    #zelf een aantal metingen nemen en best fit afleiden?
    #= eigen TCV afleiden
    #= plotten van de vochtigheids waarden alsof aarde altijd bij 25 °C gedijd
    #conversie van conductiviteit naar siemens / cm heeft buffer vloeistof
    #nodig en daarna spanningen interpoleren naar corresponderende geleidingswaarden
#conversie van spanning naar siemens / cm
#calibratie van de humitity / temperature en light sensor
#

import logging,numpy,time
from  graphBB.Sensor import Temperature,Humidity
tsensor = Temperature("Core temperature")
hsensor = Humidity("Humidity")

__LOGNAME__ = "Innerpotlog.log"
__LOGDIR__ = "/log/" + __LOGNAME__
__LOGMAXBYTES__ = 50000

class Compensation:
    def __init__(self):
        try:
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
        return hum / (1 + self.tvc * (temp-25))

    #opstellen van temperature/ conductiviteit formule
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
        z = self.__calcTVCgraph()[0]
        if len(z) == 2:
            print "Linear approximation"
            print "TVC : " + str(z[0])
            self.tvc = z
        return z

    def main(self):
        self.getgradient()
        x = tsensor.getvalues()
        y = hsensor.getvalues()
        newy = self.compensate(x,y)
        mes = "Compensated humidity (at {old} at {temp} degrees is {new}".format(old =y, temp = x, new = newy)
        self.corelog.info(mes)
if __name__ == "__main__":
    c = Compensation()
    c.main()




