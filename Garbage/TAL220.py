class TAL220:
    def __init__(self,vcc):
        self.vcc = vcc
        self.calibrated = False
        self.VTWratio = None

    def calibrate(self,weight,voltage):
        self.VTWratio = voltage / weight
        self.calibrate = True


    def voltage_to_weight(self,voltage):
        try:
            if self.calibrate:
                return(self.__convert(voltage))
            else:
                raise Exception("Load cell not calibrated")
        except Exception as e:
            print e

    def __convert(self,volt):
        if self.VTWratio is None:
            raise Exception("Load cell not calibrated")
        else:
            return volt/self.VTWratio

    def setcalibration(self,ratio):
        self.VTWratio = ratio
        self.calibrated = True