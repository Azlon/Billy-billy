import copy
import traceback

class SensorDict_wrapper:
    def __init__(self, size):
        self.sensordict = {"temperature": [], "humidity": [], "light_front": [], "light_back": [], "light": [], }
        self.size = size
        self.sensordictfilled = False

    def addSensorData(self, sensordata):
        try:
            self.sensordict['temperature'].append(sensordata[0])
            self.sensordict['humidity'].append(sensordata[1])
            self.sensordict['light_front'].append(sensordata[2])
            self.sensordict['light_back'].append(sensordata[3])
            
            brightestLightValue = self.takeBrightestLightValue(sensordata[2], sensordata[3])
            print "Brightest light: " + str(brightestLightValue)
            self.sensordict['light'].append(brightestLightValue)

            print "buffer size: " + str(len(self.sensordict["temperature"]))

        except IndexError:
            print("The sensordata passed to the addSensorData function is possibly empty. ")
            traceback.print_exc()

    def shrinkSensorDataToLastMeasured(self):
        lastMeasuredTemperature = self.sensordict['temperature'][-1]
        self.sensordict['temperature'] = [lastMeasuredTemperature]

        lastMeasuredHumidity = self.sensordict['humidity'][-1]
        self.sensordict['humidity'] = [lastMeasuredHumidity]

        lastMeasuredFrontLight = self.sensordict["light_front"][-1]
        self.sensordict['light_front'] = [lastMeasuredFrontLight]

        lastMeasuredBackLight = self.sensordict["light_back"][-1]
        self.sensordict['light_back'] = [lastMeasuredBackLight]

        lastMeasuredLight = self.sensordict['light'][-1]
        self.sensordict['light'] = [lastMeasuredLight]

    def takeBrightestLightValue(self, frontLightLux, backLightLux):
        if frontLightLux >= backLightLux:
            return frontLightLux
        else:
            return backLightLux

    def getDeepCopy(self):
        return copy.deepcopy(self.sensordict)