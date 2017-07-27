import json

import numpy as np
from common.decorators.jobs import safe_job


def create_minute_sample_job(**kwargs):

    @safe_job
    def job():
        sensorDataLastMinute = kwargs['sensor_wrapper'].getDeepCopy()
        kwargs['sensor_wrapper'].shrinkSensorDataToLastMeasured()

        if(not (kwargs["shared_plant"].potID == "")):
            npTemperatureData = np.array(sensorDataLastMinute['temperature'])
            npHumidityData = np.array(sensorDataLastMinute['humidity'])
            npLightData = np.array(sensorDataLastMinute['light'])

            meanTemperature = np.mean(npTemperatureData)
            meanHumidity = np.mean(npHumidityData)
            meanLight = np.mean(npLightData)

            potID = kwargs['shared_plant'].potID

            sensorMeanDictionary = {'pot': potID, 'temperature': meanTemperature, 'humidity': meanHumidity, 'light': meanLight}

            jsonstring = json.dumps(sensorMeanDictionary)
            kwargs["client"].publish("vmnengine/event/sensor", jsonstring)

            print "Published mean sensor values to vmnengine/event/sensor, message: " + jsonstring

    return job