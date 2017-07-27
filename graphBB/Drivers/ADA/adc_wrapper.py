import time

from Drivers.ADA.sensor_adafruit.Adafruit_ADS1x15.Adafruit_ADS1x15 import ADS1x15

from humiditysensor import HumiditySensor
from lightsensor import LightSensor
from thermalsensor import ThermalSensor


class ADC_Wrapper:
    def __init__(self):
        self.pga = 6144
        self.sps = 1  # met Pi 2 was dit 8 met pi 3 is conversie nog niet gedaan en krijgen we vorige waarde
        self.adc = ADS1x15(ic=0x01)

        self.thermalsensor = ThermalSensor()
        self.humiditysensor = HumiditySensor()
        self.lightsensor = LightSensor()


    def readAllSensors(self):
        temp = self.adc.readADCSingleEnded(0, self.pga, self.sps)
        tempDegrees = self.thermalsensor.convertToDegrees(temp)

        #time.sleep(0.2)

        backLight = self.adc.readADCSingleEnded(1, self.pga, self.sps)
        backLightLux = self.lightsensor.convertToLux(backLight)

        #time.sleep(0.2)

        hum = self.adc.readADCSingleEnded(2, self.pga, self.sps)
        humPercentage = self.humiditysensor.convertToPercentage(hum)

        #time.sleep(0.2)

        frontLight = self.adc.readADCSingleEnded(3, self.pga, self.sps)
        frontLightLux = self.lightsensor.convertToLux(frontLight)

        #time.sleep(0.2)

        print "Read temperature: " + str(tempDegrees) + " degrees Celsius"
        print "Read humidity percentage: " + str(humPercentage)
        print "Read front light ADC value: " + str(frontLight)
        print "Read back light ADC value " + str(backLight)
        print "Read front light: " + str(frontLightLux) + " lux"
        print "Read back light: " + str(backLightLux) + " lux"

        sensorValues = [tempDegrees, humPercentage, frontLightLux, backLightLux]

        return sensorValues

if __name__ == "__main__":
    wrap = ADC_Wrapper()
    while 1:
        wrap.readAllSensors()
        time.sleep(1)




