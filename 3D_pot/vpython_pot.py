from visual import *
from visual.graph import gcurve
import time
import threading


sceneobj = []
sensors = []
values = []
length, radius = 5,5
sm = 2
size_inc = 0.1
framerate = 100

def normalize():
    for i in sceneobj:
        if isinstance(i,sphere):
            i.radius = sm

def getvalue(id):
    return 0

def removeobject(i,obj):
    obj.visible = False
    del obj
    del sceneobj[i]


def createCylinder(length= 5):
    c = cylinder(pos=(0, 0, 0), axis=(0, length, 0), color=color.red, radius=5)
    sceneobj.append(c)
    return c

def createRingoballs(height,sm_rad = 1,rad = radius):

    labelpos = height + sm_rad
    if not sensors:
        sensid = 0
    else:
        sensid = len(sensors)

    label(pos = (rad,labelpos,0), text ="ABEL %d:\nValue:%0.1f" % (sensid,getvalue(sensid)))
    sensid += 1
    s1 = sphere(pos=(rad, height, 0), radius=sm_rad, color=color.green)

    label(pos=(0, labelpos, -rad), text="ABEL %d" % sensid)
    sensid +=1
    s2 = sphere(pos=(0, height, -rad), radius=sm_rad, color=color.green)

    label(pos=(0, labelpos, rad), text="ABEL %d" % sensid)
    sensid +=1
    s3 = sphere(pos=(0, height, rad), radius=sm_rad, color=color.green)

    label(pos=(-rad, labelpos, 0), text="ABEL %d" % sensid)
    sensid +=1
    s4 = sphere(pos=(-rad, height, 0), radius=sm_rad, color=color.green)

    temp = s1,s2,s3,s4
    [sceneobj.append(x) for x in temp]
    [sensors.append(x) for x in temp]
    total  = zip(sensors,values)

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

def getCylinder():
    for i,val in enumerate(sceneobj):
        if isinstance(val,cylinder):
            return i,val
            pass
    print "no item found..."
    return -1,-1

def getObject(obj):
    for i, val in enumerate(sceneobj):
        if val == obj:
            return i, val
    print "no item found..."
    return -1,-1
def grow(obj,finalsize):
    while obj.radius < finalsize:
        rate(framerate)
        obj.radius += size_inc


def shrink(obj,finalsize):
    while obj.radius > finalsize:
        rate(framerate)
        obj.radius -= size_inc


def settoradius(obj,rad):
    if obj.radius > rad:
        shrink(obj,rad)
    else:
        grow(obj,rad)

def addlevel():
    i,c = getCylinder()
    if i == -1:
        oax = 0
    else:
        oax = c.axis[1]+length
    print "length cylinder : "  + str(oax)
    increasecylinder(c,oax )
    createRingoballs(oax)

def increasecylinder(old,newlength):
    i,c = getObject(old)
    if i != -1:
        removeobject(i, c)

    createCylinder(newlength)


# change = [(x.x,length,x.z) for x in bottom]
# for i,index in enumerate(change):
#      top.append(sphere(pos = change[i], radius = 2, color = color.green))



def createscene(name):
    d = display(title=name, x=0, y=0, center=(0, 0, 0), background=(0, 1, 1))
    d.stereo = 'active'
    createRingoballs(0,rad=2)
    createRingoballs(0)
    createRingoballs(length)

    increasecylinder(None, length)
    sizeThread().start()



def pulse():
    while 1:
        for i,val in enumerate(sensors):
            setsizeThread(i,4).start()
            time.sleep(0.5)
        changecamera()
        addlevel()
        for i,val in enumerate(sensors):
            setsizeThread(i,1).start()
            time.sleep(0.5)


def changecamera():
    d = display.get_selected()

if __name__== "__main__":
    createscene("Billy")

