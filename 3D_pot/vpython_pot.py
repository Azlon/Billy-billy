from visual import *
import time
import threading
sceneobj = []
sensors= []
length, radius = 5,5
sm_rad = 2
def createscene(name):
    display(title=name, x=0, y=0, center=(0, 0, 0), background=(0, 1, 1))

def removeobject(obj):
    obj.visible = False
    del obj


def createCylinder(length= 5):
    c = cylinder(pos=(0, 0, 0), axis=(0, length, 0), color=color.red, radius=5)
    sceneobj.append(c)
    return c

def createRingoballs(height,sm_rad = 1):
    labelpos = height + sm_rad
    if not sensors:
        sensid = 0
    else:
        sensid = len(sensors)
    label(pos = (radius,labelpos,0), text ="sensor %d" % sensid)
    sensid += 1
    s1 = sphere(pos=(radius, height, 0), radius=sm_rad, color=color.green)

    label(pos=(0, labelpos, -radius), text="sensor %d" % sensid)
    sensid +=1
    s2 = sphere(pos=(0, height, -radius), radius=sm_rad, color=color.green)

    label(pos=(0, labelpos, radius), text="sensor %d" % sensid)
    sensid +=1
    s3 = sphere(pos=(0, height, radius), radius=sm_rad, color=color.green)

    label(pos=(-radius, labelpos, 0), text="sensor %d" % sensid)
    sensid +=1
    s4 = sphere(pos=(-radius, height, 0), radius=sm_rad, color=color.green)

    list = s1,s2,s3,s4
    [sceneobj.append(x) for x in list]
    [sensors.append(x) for x in list]
    return list

class sizeThread(threading.Thread):
    def __init__(self):
        super(sizeThread,self).__init__()

    def run(self):
      while 1:
          for i in sensors:
              if i.radius > 4:
                  i.color = color.red
              else:
                  i.color = color.green

class setsizeThread(threading.Thread):
    def __init__(self,id,newsize):
        super(setsizeThread,self).__init__()
        self.id = id
        self.newsize = newsize
    def run(self):
        print "change size of " + str(self.id)
        settoradius(sensors[self.id], self.newsize)

class shrinkThread(threading.Thread):
    def __init__(self,list):
        super(shrinkThread,self).__init__()
        self.list = list

    def run(self):
        print "Started thread to shrink"
        settoradius(self.list[3], 1)
        print "Done shrinking"
        inccylmultiple()
        createRingoballs(10)

def getCylinder():
    for i in sceneobj:
        if isinstance(i,cylinder):
            return i
def grow(obj,finalsize):
    while obj.radius < finalsize:
        rate(100)
        obj.radius += 0.01


def shrink(obj,finalsize):
    while obj.radius > finalsize:
        rate(100)
        obj.radius -= 0.01


def settoradius(obj,rad):
    if obj.radius > rad:
        shrink(obj,rad)
    else:
        grow(obj,rad)
def inccylmultiple():
    c = getCylinder()
    oax = c.axis[1]
    increasecylinder(c,oax + length)

def increasecylinder(old,newlength):
    removeobject(old)
    createCylinder(newlength)

# change = [(x.x,length,x.z) for x in bottom]
# for i,index in enumerate(change):
#      top.append(sphere(pos = change[i], radius = 2, color = color.green))

createscene("billy-billy")
c = createCylinder(length)
bottom, top = createRingoballs(0), createRingoballs(length)



while 1:
    shrinkThread(top).start()
    sizeThread().start()
    for i,item in enumerate(sensors):
        setsizeThread(i,4).start()
        time.sleep(1)
    for i,item in enumerate(sensors):
        setsizeThread(i,2).start()
        time.sleep(1)

# grow(bottom[2],3)
# shrink(bottom[2],1)