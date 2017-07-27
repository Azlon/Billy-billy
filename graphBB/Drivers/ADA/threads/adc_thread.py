import json
import threading
import time
import traceback

from modules.adc.adc_wrapper import ADC_Wrapper


class AdcThread (threading.Thread):
    def __init__(self, threadID, name, event, client, shared_plant, sensor_wrapper, **kwargs):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.client = client
        # self.led = led
        self.plant = shared_plant
        self.bufferedPotId = ""

        self.event = event
        self.adc_wrapper = ADC_Wrapper()
        self.sensor_wrapper = sensor_wrapper

        self.i = 0
        #TODO: use j to publish sensor values to web interface.
        self.j = 0

        self.tempAlertLevel = 0
        self.tempWarningLevel = 0

        self.humAlertLevel = 0
        self.humWarningLevel = 0

        self.lightAlertLevel = 0
        self.lightWarningLevel = 0


    def run(self):
        while self.event.is_set():
            try:
                self.bufferedPotID = self.plant.potID
                # print "mainThread running"
                # self.i = self.i + 1
                # print(plant.potID)

                # necessary logic for LEDS
                # if self.tempAlertLevel or self.humAlertLevel or self.lightAlertLevel:
                #     self.led.statusAlarm()
                # elif self.tempWarningLevel or self.humWarningLevel or self.lightWarningLevel:
                #     self.led.statusWarning()
                # else:
                #     self.led.statusGood()

                #read sensor data
                sensorArray = self.adc_wrapper.readAllSensors()
                self.sensor_wrapper.addSensorData(sensorArray)

                #check if there are warnings or alerts
                self.checkTempAlert()
                self.checkHumidityAlert()
                self.checkLightAlert()

                # print str(plant)
                # print(self.sensor_wrapper.sensordict)

                time.sleep(0.3)

                # if self.i == 30:
                    # jsonstring = util.createSensorJsonBySensorData(self.plant.potID, self.sensor_wrapper.sensordict)
                    # self.client.publish("vmnengine/event/sensor", jsonstring)
                    #if (self.i % 3) == 0:
                    #    self.client.publish("vmndb/push/sensor/volatile", jsonstring)
                    # self.i = 0
                    # print "Pushlished sensor values PERIODICALLY to topic vmnengine/event/sensor: " + jsonstring
                    # print str(self.plant)

            except Exception as e:
                print "Exception thrown in main sensor while loop; " + str(e)
                traceback.print_exc()


    def checkTempAlert(self):
        if self.bufferedPotID:
            self.tempAlertLevel = self.plant.temperatureParams.is_alert(self.sensor_wrapper.sensordict["temperature"][-1])
            self.tempWarningLevel = self.plant.temperatureParams.is_warning(
                self.sensor_wrapper.sensordict["temperature"][-1])

            if self.tempAlertLevel:
                alertDict = vmnengine.modules.adc.util.createStatusDict(self.bufferedPotID, "alert", self.tempAlertLevel, "temperature",
                                                                        self.sensor_wrapper.sensordict["temperature"][-1])
                alertString = json.dumps(alertDict)
                self.client.publish("vmnengine/event/notification/alert", alertString)
                print "Pushlished ALERT: " + alertString
            elif self.tempWarningLevel:
                warningDict = vmnengine.modules.adc.util.createStatusDict(self.bufferedPotID, "warning", self.tempWarningLevel, "temperature",
                                                                          self.sensor_wrapper.sensordict["temperature"][-1])
                warningString = json.dumps(warningDict)
                self.client.publish("vmnengine/event/notification/warning", warningString)
                print "Pushlished WARNING: " + warningString


    def checkHumidityAlert(self):
        if self.bufferedPotID:
            self.humAlertLevel = self.plant.humidityParams.is_alert(self.sensor_wrapper.sensordict["humidity"][-1])
            self.humWarningLevel = self.plant.humidityParams.is_warning(self.sensor_wrapper.sensordict["humidity"][-1])

            if self.humAlertLevel:
                alertDict = vmnengine.modules.adc.util.createStatusDict(self.bufferedPotID, "alert", self.humAlertLevel, "humidity",
                                                                        self.sensor_wrapper.sensordict["humidity"][-1])
                alertString = json.dumps(alertDict)
                self.client.publish("vmnengine/event/notification/alert", alertString)
                print "Pushlished ALERT: " + alertString
            elif self.humWarningLevel:
                warningDict = vmnengine.modules.adc.util.createStatusDict(self.bufferedPotID, "warning", self.humWarningLevel, "humidity",
                                                                          self.sensor_wrapper.sensordict["humidity"][-1])
                warningString = json.dumps(warningDict)
                self.client.publish("vmnengine/event/notification/warning", warningString)
                print "Pushlished WARNING: " + warningString

    def checkLightAlert(self):
        if self.bufferedPotID:
            self.lightAlertLevel = self.plant.lightParams.is_alert(self.sensor_wrapper.sensordict["light"][-1])
            self.lightWarningLevel = self.plant.lightParams.is_warning(self.sensor_wrapper.sensordict["light"][-1])

            if self.lightAlertLevel:
                alertDict = vmnengine.modules.adc.util.createStatusDict(self.bufferedPotID, "alert", self.lightAlertLevel, "light",
                                                                        self.sensor_wrapper.sensordict["light"][-1])
                alertString = json.dumps(alertDict)
                self.client.publish("vmnengine/event/notification/alert", alertString)
                print "Pushlished ALERT: " + alertString
            elif self.lightWarningLevel:
                warningDict = vmnengine.modules.adc.util.createStatusDict(self.bufferedPotID, "warning", self.lightWarningLevel, "light",
                                                                          self.sensor_wrapper.sensordict["light"][-1])
                warningString = json.dumps(warningDict)
                self.client.publish("vmnengine/event/notification/warning", warningString)
                print "Pushlished WARNING: " + warningString

