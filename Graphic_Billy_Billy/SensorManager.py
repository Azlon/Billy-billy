from Sensor import Humidity,Light,Temperature,Weight
import time,json

class SensorManager():
    def __init__(self):
        self.dict = {}
        self.values = []
        self.h = Humidity("0-12 Humidity Sensors")
        self.l =  Light("Front and Back light sensors")
        self.t = Temperature("Temperature sensor")
        self.w = Weight("Weight load cell")

        self.sensors = [self.h, self.l,self.t,self.w]

    def getAllVal(self):
        for i in self.sensors:
            self.values.append(i.getvalues())
        return self.values

    def getValByID(self,id):
        return self.sensors[id].getvalues()

    def mkjson(self):
        self.getAllVal()
        tl = []
        [tl.append(i.dict) for i in self.sensors]
        self.dict["Sensors"] = tl
        self.dict["Time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        return json.dumps(self.dict)

if __name__ == "__main__":
    manager = SensorManager()
    while 1:
        print manager.mkjson()
        time.sleep(1)

