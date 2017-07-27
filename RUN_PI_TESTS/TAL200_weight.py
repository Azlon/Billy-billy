import time

from Drivers.HX711 import hx711 as amp

cell = amp.HX711(dout = 22, pd_sck=27)
cell.set_reading_format("LSB","MSB")
cell.reset()

while 1:
    #checking read function
    print cell.read()
    #checking weight function
    print "Weight: " + str(cell.get_weight(1))

    time.sleep(1)