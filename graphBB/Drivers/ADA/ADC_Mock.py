import random

class ADC_Mock:
    def getSensorValuesRandom(self, potID):
        temp = random.gauss(20.0, 5.0)
        hum  = random.gauss(50.0, 20.0)
        light = random.gauss(100000.0, 7000.0)

        sensorDict = {
            "pot": potID,
            "temperature": temp,
            "humidity": hum,
            "light": light
        }

        return sensorDict

    def getSensorValuesLow(self, potID):
        sensorList = []

        sensorList.append(-5)
        sensorList.append(3)
        sensorList.append(800)

        sensorDict = {
            "pot": potID,
            "temperature": -5,
            "humidity": 3,
            "light": 800
        }

        return sensorDict