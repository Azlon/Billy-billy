import traceback

import util


def getSensorHandler(payload, topic, client, **kwargs):
    try:
        sensor_wrapper = kwargs['sensor_wrapper']
        sensorValues = sensor_wrapper.sensordict
        plant = kwargs['shared_plant']

        splitTopic = topic.split("/")
        if splitTopic[-1] == "temperature":
            statusJson = util.getStatusJson(plant, sensorValues, "temperature")
            client.publish("vmnengine/response/" + payload['key'] + "/temperature", statusJson)
            print "Published temperature sensor status ON DEMAND: " + statusJson
        elif splitTopic[-1] == "humidity":
            statusJson = util.getStatusJson(plant, sensorValues, "humidity")
            client.publish("vmnengine/response/" + payload['key'] + "/humidity", statusJson)
            print "Published humidity sensor status ON DEMAND: " + statusJson
        elif splitTopic[-1] == "light":
            statusJson = util.getStatusJson(plant, sensorValues, "light")
            client.publish("vmnengine/response/" + payload['key'] + "/light", statusJson)
            print "Published light sensor status ON DEMAND: " + statusJson
    except Exception as exc:
        print "Exception thrown in getSensorHandler; " + str(exc)
        traceback.print_exc()