import math

class ThermalSensor:
    # This conversion is not accurate!!
    def convertToDegrees(self, millivolt):
        try:
            volt = millivolt / 1000
            resistance = volt / (3.3 - volt) # hier nog opvangen wanneer spanning exact 3.3V is
            temperature = abs(resistance)  # mag niet negatief zijn anders valueerrror
            temperature = math.log(temperature)
            temperature /= 3570 # aangepast voor laatste versie smd ntc
            temperature += 1 / (25 + 273.15)
            temperature = 1 / temperature
            temperature -= 273.15
            #print "temperatuur", math.ceil(temperature * 100) / 100
            temperature = math.ceil(temperature * 10) / 10
            temperature -= 2

            return temperature
        except ZeroDivisionError:
            return -666
        except Exception as exc:
            print "Temperature conversion error; " + str(exc)
            raise
