import threading
import time

class thr(threading.Thread):
    def __init__(self):
        super(thr,self).__init__()

    def run(self):
        print "starting the main thread"
        time.sleep(2)

class brother(threading.Thread):
    def __init__(self,other ):
        super(brother,self).__init__()
        self.other = other

    def run(self):
        self.other.join()
        print "I waited nicely"


test = thr()
bro = brother(test)
test.start()
bro.start()
