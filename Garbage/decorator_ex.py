import time

def defwrapper(func):
    def wrapper(*args):
        t = time.time()
        r = func(*args)
        delta = time.time()-t
        print "Function took {delta} time to execute".format(delta = delta)
        print func.func_name
        return r
    return wrapper

@defwrapper
def wait(t):
    time.sleep(t)
    return "Im here"

f = wait(2)
print f