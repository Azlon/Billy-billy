import json

from common.decorators.jobs import safe_job


def create_web_sample_job(**kwargs):

    @safe_job
    def job():
        if (not (kwargs["shared_plant"].potID == "")):
            currentSensorData = kwargs['sensor_wrapper'].getDeepCopy()

            lastTemperature = currentSensorData["temperature"][-1]
            lastHumidity = currentSensorData["humidity"][-1]
            lastLight = currentSensorData["light"][-1]
            lastFrontLight = currentSensorData["light_front"][-1]
            lastBackLight = currentSensorData["light_back"][-1]

            potID = kwargs["shared_plant"].potID

            lastSensorDictionary = {'pot': potID, 'temperature': lastTemperature, 'humidity': lastHumidity,
                                    'light_front': lastFrontLight, 'light_back': lastBackLight, 'light': lastLight, }

            jsonstring = json.dumps(lastSensorDictionary)
            kwargs["client"].publish("vmndb/push/sensor/volatile", jsonstring)

            print "Published last sensor values to vmndb/push/sensor/volatile, message: " + jsonstring

    return job