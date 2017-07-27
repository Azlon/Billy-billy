#!/usr/bin/python

import os
import time

from ABE_helpers import ABEHelpers

from graphBB.Drivers.ABEL import ADCPi

"""
================================================
ABElectronics ADC Pi 8-Channel ADC demo
Version 1.0 Created 09/05/2014
Version 1.1 16/11/2014 updated code and functions to PEP8 format

Requires python smbus to be installed
run with: python demo-read_voltage.py
================================================


Initialise the ADC device using the default addresses and sample rate,
change this value if you have changed the address selection jumpers

Sample rate can be 12,14, 16 or 18
"""

addr1_board1 = 0x68
addr2_board1 = 0x69

addr1_board2 = 0x6C
addr2_board2 = 0x6D


i2c_helper = ABEHelpers()
bus = i2c_helper.get_smbus()
adc1 = ADCPi(bus, addr1_board1, addr2_board1, 12)
adc2 = ADCPi(bus, addr1_board2, addr2_board2, 12)

while (True):

    # clear the console
    os.system('clear')

    # read from adc channels and print to screen
    print "Reading on 0x" + format(addr1_board1,"02x") + " and 0x" + format(addr2_board1,"02x")
    print ("Channel 1: %02f" % adc1.read_voltage(1))
    print ("Channel 2: %02f" % adc1.read_voltage(2))
    print ("Channel 3: %02f" % adc1.read_voltage(3))
    print ("Channel 4: %02f" % adc1.read_voltage(4))
    print ("Channel 5: %02f" % adc1.read_voltage(5))
    print ("Channel 6: %02f" % adc1.read_voltage(6))
    print ("Channel 7: %02f" % adc1.read_voltage(7))
    print ("Channel 8: %02f" % adc1.read_voltage(8))

    print "Reading on 0x" + format(addr1_board2,"02x") + " and 0x" + format(addr2_board2,"02x")
    print ("Channel 1: %02f" % adc2.read_voltage(1))
    print ("Channel 2: %02f" % adc2.read_voltage(2))
    print ("Channel 3: %02f" % adc2.read_voltage(3))
    print ("Channel 4: %02f" % adc2.read_voltage(4))
    print ("Channel 5: %02f" % adc2.read_voltage(5))
    print ("Channel 6: %02f" % adc2.read_voltage(6))
    print ("Channel 7: %02f" % adc2.read_voltage(7))
    print ("Channel 8: %02f" % adc2.read_voltage(8))
    # wait 0.5 seconds before reading the pins again
    time.sleep(0.5)
