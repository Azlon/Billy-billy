from mayavi import mlab
from numpy import random
import time
import threading

class sleepthread(threading.Thread):
    def __init__(self):
        super(sleepthread,self).__init__()
    def run(self):
        time.sleep(1)



@mlab.show
def image():
        mlab.imshow(random.random((10, 10)))

image()
time.sleep(1)
image()
time.sleep(1)
image()
time.sleep(1)