class LightSensor:
    # This conversion is not accurate!!
    def convertToLux(self, millivolt):
        try:
            #volt = millivolt / 1000

            # formula found on http://emant.com/316002.page
            # this formula is not accurate!!
            #lux = -(((2500 / volt) - 500) / 3.3) + 40000
            lux = (millivolt/50)*10000
            return abs(lux)
        except Exception as exc:
            print "Light conversion error; " + str(exc)
            raise

