import json

def createStatusDict(pot, type, level, sensor, value):
    notificationDict = {"pot" : pot, "type" : type, "level" : level, "sensor" : sensor, "value" : value}

    return notificationDict

def createStatusDictUsingBothLevels(pot, type, alertLevel, warningLevel,  sensor, value):
    notificationDict = {"pot" : pot, "type" : type, "level" : 0, "sensor" : sensor, "value" : value}

    if alertLevel:
        notificationDict["level"] = alertLevel
    elif warningLevel:
        notificationDict["level"] = warningLevel

    return notificationDict

def createOdpStatusDict(pot, type, alertLevel, warningLevel, sensor, value, ordercoefficient):
    odpstatusdict = createStatusDictUsingBothLevels(pot, type, alertLevel, warningLevel, sensor, value)
    odpstatusdict["ordercoefficient"] = ordercoefficient
    return odpstatusdict

def getStatusJson(plant, sensorDict, quantity):
    param = plant.getBySensor(quantity)

    alertLevel = param.is_alert(sensorDict[quantity][-1])
    warningLevel = param.is_warning(sensorDict[quantity][-1])
    statusDict = createStatusDictUsingBothLevels(plant.potID, "good", alertLevel, warningLevel, quantity,
                                    sensorDict[quantity][-1])
    if alertLevel:
        statusDict["type"] = "alert"
    elif warningLevel:
        statusDict["type"] = "warning"

    return json.dumps(statusDict)

def createSensorDict(potID, temperature, humidity, light):
    sensorDict = {"pot": potID, "temperature": temperature, "humidity": humidity, "light": light}
    return sensorDict

def createSensorJsonByParams(potID, temperature, humidity, light):
    sensorDict = createSensorDict(potID, temperature, humidity, light)
    return json.dumps(sensorDict)

def createSensorJsonBySensorData(potID, sensorData):
    sensorDict = createSensorDict(potID, sensorData['temperature'][-1], sensorData['humidity'][-1], sensorData['light'][-1])
    return json.dumps(sensorDict)