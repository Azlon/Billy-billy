class HumiditySensor:
    # This conversion is not accurate!!
    def convertToPercentage(self, millivolt):
        try:
            ratio = millivolt/3300
            return abs((ratio*140))
        except Exception as exc:
            print "Humity conversion error; " + str(exc)
            raise