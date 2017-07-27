import time

import RPi.GPIO as GPIO

pins = [19,26,5,6,16,20,21,23,24]
GPIO.setmode(GPIO.BCM)
# [GPIO.setup(i, GPIO.OUT) for i in pins]

GPIO.setup(pins, GPIO.OUT)
def loop(pins):
    # print 'Looping pins' + str(pins)
    # [GPIO.output(i, True) for i in pins]
    # time.sleep(1)
    # [GPIO.output(i,False) for i in pins]

    print "Looping " + str(pins)
    GPIO.output(pins, True)
    time.sleep(2)
    GPIO.output(pins,False)
    time.sleep(2)

try:
    while 1:
        loop(pins)
except KeyboardInterrupt as e:
    GPIO.cleanup()