from capture_humidity import SensorManager
import json
import vpython_pot as pot
import time
play_intval= 1

#get data from sensor and store in text file
playback_from = "/home/pi/Values.txt"
s = SensorManager()
# filename = "Values-" + d.datetime.today().strftime("%H_%M_%S") + ".txt"
s.capture("Values.txt",1)

#playback data from the text file
all = s.playback(playback_from,1)



