from visual import *
from visual.graph import gcurve
import time
import threading
import random
try:
    import ADC_values as adc

    setup = adc.Boards()
    values = setup.getvalues()

except Exception as e:
    print e
    setup = None
    values = []

sceneobj = []
sensors = []
labels = []
sizethreads = [None for i in range(1,13)]

length, radius = 5,5
sm = 2
size_inc = 0.1
framerate = 100
update_interval = 2
max_size = 1.5

values = [random.randint(0,5) for i in range(1, 13)]

def normalize():
    for i in sceneobj:
        if isinstance(i,sphere):
            i.radius = sm

def getvalue(id):
    if not values:
        print "No values"
        return -1
    else:
        print "failing id? : " + str(id)
        print values
        return values[id]

def changevaluelabel(id):

    setlabel(id,"ABEL %d:\nValue:%0.1f" % (id, getvalue(id)))
    print "setttin label: " + str(id) + "to " + str(getvalue(id))

def setlabel(id,string):
    if not labels:
        print "No labels"
    else:
        labels[id].text = string

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

    labels.append(label(pos = (rad,labelpos,0), text ="ABEL %d:\nValue:%0.1f" % (sensid,getvalue(sensid))))
    sensid += 1
    s1 = sphere(pos=(rad, height, 0), radius=sm_rad, color=color.green)

    labels.append(label(pos=(0, labelpos, -rad), text ="ABEL %d:\nValue:%0.1f" % (sensid,getvalue(sensid))))
    sensid +=1
    s2 = sphere(pos=(0, height, -rad), radius=sm_rad, color=color.green)

    labels.append(label(pos=(0, labelpos, rad), text ="ABEL %d:\nValue:%0.1f" % (sensid,getvalue(sensid))))
    sensid +=1
    s3 = sphere(pos=(0, height, rad), radius=sm_rad, color=color.green)

    labels.append(label(pos=(-rad, labelpos, 0), text ="ABEL %d:\nValue:%0.1f" % (sensid,getvalue(sensid))))
    sensid +=1
    s4 = sphere(pos=(-rad, height, 0), radius=sm_rad, color=color.green)

    temp = s1,s2,s3,s4
    [sceneobj.append(x) for x in temp]
    [sensors.append(x) for x in temp]
    total  = zip(sensors,values)

    return list

class checksizeThread(threading.Thread):
    def __init__(self):
        super(checksizeThread, self).__init__()

    def run(self):
      while 1:
          for i in sensors:
              if i.radius > max_size:
                  i.color = color.red
              else:
                  i.color = color.green

class setsizeThread(threading.Thread):
    def __init__(self,id,newsize):
        super(setsizeThread,self).__init__()
        self.id = id
        self.newsize = newsize
        self.prev = None

    def run(self):
        print "started changing size, but waiting"
        if self.prev !=None:
            self.prev.join()
        print " done waiting"
        print "change size of " + str(self.id)
        settoradius(sensors[self.id], self.newsize)

    def setprev(self,thr):
        self.prev = thr

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

def createthreads():
    for i in range(0,12):
        t = setsizeThread(i,1)
        sizethreads[i] = t

def update(intval):
    for i in range(0,12):
    #labels updaten
        changevaluelabel(i)
    #straal updaten
        thr = setsizeThread(i,getvalue(i))
        thr.start()
        thr.setprev(sizethreads[i])
        sizethreads[i] = thr

    time.sleep(intval)


def createscene(name):
    d = display(title=name, x=0, y=0, center=(0, 0, 0), background=(0, 0, 1))
    d.stereo = 'active'
    createRingoballs(0,rad=2)
    createRingoballs(0)
    createRingoballs(length)
    increasecylinder(None, length)
    checksizeThread().start()


    print "updating"
    update(update_interval)




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
    while 1:
        values = [random.uniform(0, 2) for i in range(1, 13)]
        update(update_interval)