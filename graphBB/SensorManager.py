from Sensor import Humidity,Light,Temperature,Weight
import time,json
import logging
logger = logging.getLogger('Sensor.manager')

#todo : Toevoegen en verwijderen van de sensoren (vb vochtigheid) throws errors : programma naar de zak

class SensorManager():
    def __init__(self):
        self.dict = {}
        self.values = []

        # self.h = (Humidity("0-12 Humidity Sensors"),'Humidity')
        # self.l =  (Light("Front and Back light sensors"),'Light')
        # self.t = (Temperature("Temperature sensor"),'Temperature')
        self.w = (Weight("Weight load cell"),'Weight')

        self.senslist = [self.w]
        self.sensors, self.types = zip(*self.senslist)
        self.monitor = Monitor(self.senslist)

        names = [s.name for s in self.sensors]
        logger.info("Found " + str(len(self.sensors)) + " sensors: " + str(names))

    def addsensor(self,*args):
        self.senslist.extend(*args)
        ts, tt = zip(*self.senslist)
        self.sensors = ts
        self.types = tt

    def getAllVal(self):
        for i in self.sensors:
            self.values.append(i.getvalues())
        return self.values

    def getValByID(self,id):
        return self.sensors[id].getvalues()

    def mkjson(self):
        self.monitor.notify()
        self.getAllVal()
        tl = []
        [tl.append(i.dict) for i in self.sensors]
        self.dict["Sensors"] = tl
        self.dict["Time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        return json.dumps(self.dict)

class Monitor:
    def __init__(self,sensors):
        self.sensors = sensors
        # print 'Init in monitor : ' + str(self.sensors)
        self.thresh = dict(Light = 1000,Weight = 10, Humidity = 5, Temperature = 10)

    def addsens(self,sens,type):
        self.sensors.append((sens,type))

    def notify(self):
        for sens,type in self.sensors:
            print "Sensor : " + type
            for val in sens.getvalues():
                if not self.thresh.get(type):
                    logger.info("Threshold not available for: " + type)
                elif val > self.thresh[type]:
                    print type + ' sensor is exceeding threshold ' + str(self.thresh[type]) + ' with ' + str(val)
                    logger.warning(type + ' sensor is exceeding threshold ' + str(self.thresh[type]) + ' with ' + str(val))

    def addthreshold(self,type,val):
        if not self.thresh.get(type):
            self.thresh[type] = val
        else:
            self.thresh.update([(type,val)])

if __name__ == "__main__":
    manager = SensorManager()
    while 1:
        print manager.mkjson()
        time.sleep(1)

