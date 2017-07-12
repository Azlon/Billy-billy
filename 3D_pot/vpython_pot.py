import random
import threading
import time
import json
from visual import *

# try:
#     from Garbage import ADC_values as adc
#
#     setup = adc.Boards()
#     values = setup.getvalues()
#
# except Exception as e:
#     print e
#     setup = None
#     values = []

#lists
sceneobj = []
sensors = []
labels = []
history = []
sizethreads = [None for i in range(1,13)]
values = [0 for i in range(1,13)]

#---global parameters-----#
length, radius = 5,5    #lengte en straal van de cilinder
sm = 2                  #default straal van de bollen
size_inc = 0.01         #incrementatie van de straal van de bollen in update()
framerate = 50          #bovengrens van loop uitvoering / seconde
update_interval = 2     #update interval
max_size = 2            #Maximale waarde waarvoor de bollen nog steeds groen uitslaan
multiplier = 10         #Vergroten van sensorwaarden, indien de straal aanpassing niet zichtbaaar is.

def normalize():
    """
    De straal van elke bol naar 'sm' aanpassen
    :return:
    """
    for i in sceneobj:
        if isinstance(i,sphere):
            i.radius = sm

def getvalue(id):
    '''

    :param id: de ID van de sensor
    :return: De sensorwaarde
    '''

    if not values:
        print "No values"
        return -1
    else:

        return values[id]


def changevaluelabel(id):
    '''
    Past de label voor elke bol met de nieuwe sensorwaarden aan
    :param id: SensorID
    :return:
    '''
    setlabel(id,"ABEL %d:\nValue:%0.1f" % (id, getvalue(id)))
    print "settting label: " + str(id) + "to " + str(getvalue(id))

def setlabel(id,string):
    '''
    Aanpassen van de label array
    :param id:
    :param string:
    :return:
    '''

    if not labels:
        print "No labels"
    else:
        labels[id].text = string



def removeobject(i,obj):
    '''
    Verwijder de models uit het plane en array
    :param i:
    :param obj:
    :return:
    '''
    obj.visible = False
    del obj
    del sceneobj[i]


def createCylinder(length= 5):
    '''
    Maakt telkens eeen cilinder met een bepaalde lengte
    :param length: lengte van de cilinder
    :return: cilinderobject
    '''
    c = cylinder(pos=(0, 0, 0), axis=(0, length, 0), color=color.red, radius=5)
    sceneobj.append(c)
    return c

def definestaticradia(val_sens):
    '''
    Past de straal van elke bol met de waarden in val_sens lijst aan.
    :param val_sens: Lijst met alle corresponderende sensorwaarden
    :return:
    '''
    global values
    values = [i*multiplier for i in val_sens]

    for index,item in enumerate(val_sens):
        changevaluelabel(index)
        sensors[index].radius = item * multiplier

def createRingoballs(height,sm_rad = 1,rad = radius):
    '''
    Maakt een ring van bollen op een zekere hoogte en met een zekere straal.
    :param height: Hoogte van plaatsing bollen
    :param sm_rad: Straal van de bollen
    :param rad: straal van de ring
    :return: tuple lijst van ballen en sensorwaarden
    '''
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

    labels.append(label(pos=(-rad, labelpos, 0), text ="ABEL %d:\nValue:%0.1f" % (sensid,getvalue(sensid))))
    sensid +=1
    s4 = sphere(pos=(-rad, height, 0), radius=sm_rad, color=color.green)

    labels.append(label(pos=(0, labelpos, rad), text ="ABEL %d:\nValue:%0.1f" % (sensid,getvalue(sensid))))
    sensid +=1
    s3 = sphere(pos=(0, height, rad), radius=sm_rad, color=color.green)


    temp = s1,s2,s3,s4
    [sceneobj.append(x) for x in temp]
    [sensors.append(x) for x in temp]
    total  = zip(sensors,values)

    return total

class checksizeThread(threading.Thread):
    '''
    Thread om op elk moment de straal van de bollen na te gaan op het overschrijden van een maximale straal
    '''
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
    '''
    Laat de bollen krimpen / groeien volgens de waarden die in de 'values' lijst aanwezig zijn.
    '''

    def __init__(self,id,newsize):
        '''

        :param id: SensorID
        :param newsize: nieuwe straal van bol
        '''
        super(setsizeThread,self).__init__()
        self.id = id
        self.newsize = newsize
        self.prev = None

    def run(self):
        print "started changing size, but waiting on " + "'" + str(self.prev) + "'" + "(" + str(self.name)+ ")"
        if self.prev !=None:
            self.prev.join()
        print " done waiting" + "(" + str(self.name) + ")"
        print "change size of " + str(self.id)

        settoradius(sensors[self.id], self.newsize)

    def setprev(self,thr):
        self.prev = thr

def getCylinder():
    '''
    Verkrijg de index en cilinder object uit de lijst
    :return: tuple van lijstindex en cilinderobject
    '''
    for i,val in enumerate(sceneobj):
        if isinstance(val,cylinder):
            return i,val
            pass
    print "no item found..."
    return -1,-1

def getObject(obj):
    '''
    Zoek een bepaald object in de lijst
    :param obj:
    :return: tuple van index en object
    '''
    for i, val in enumerate(sceneobj):
        if val == obj:
            return i, val
    print "no item found..."
    return -1,-1

def grow(obj,finalsize):
    '''
    Incrementeert de straal van een object
    :param obj: object (bol) waarvoor de straal moet groeien
    :param finalsize: Te behalen straal
    :return:
    '''
    while obj.radius < finalsize:
        rate(framerate)
        obj.radius += size_inc


def shrink(obj,finalsize):
    '''
    Decrementeert de straal van een object
    :param obj: object (bol ) waarvoor de straal moet krimpen
    :param finalsize: Te behalen straal
    :return:
    '''
    while obj.radius > finalsize:
        rate(framerate)
        obj.radius -= size_inc


def settoradius(obj,rad):
    '''
    Bepaalt of er gegroeid of gekrompen moet worden.
    :param obj:
    :param rad: Vorige straal waarde
    :return:
    '''
    if obj.radius > rad:
        shrink(obj,rad)
    else:
        grow(obj,rad)

def addlevel():
    '''
    Voeg een nieuwe ring van bollen toe bovenop de vorige
    :return:
    '''
    i,c = getCylinder()
    if i == -1:
        oax = 0
    else:
        oax = c.axis[1]+length
    print "length cylinder : "  + str(oax)
    increasecylinder(c,oax )
    createRingoballs(oax)

def increasecylinder(old,newlength):
    '''
    Verwijdert de vorige cilinder uit de ruimten en plaatst een nieuwe grotere cilinder in de plaats
    :param old:
    :param newlength:
    :return:
    '''
    i,c = getObject(old)
    if i != -1:
        removeobject(i, c)

    createCylinder(newlength)


# change = [(x.x,length,x.z) for x in bottom]
# for i,index in enumerate(change):
#      top.append(sphere(pos = change[i], radius = 2, color = color.green))

def createthreads():
    '''
    Maak een lijst van threads aan.
    :return:
    '''
    for i in range(0,12):
        t = setsizeThread(i,1)
        sizethreads[i] = t

def addtohistory():
    '''
    Voegt de huidige sensorwaarden lijst toe aan een nieuwe lijst om de geschiedenis te monitoren.
    :return:
    '''
    history.append(values)

def update(intval):
    '''
    Laat de threads de bollen en labels aanpassen.
    :param intval: Tijd tussen updates
    :return:
    '''
    for i in range(0,12):
    #labels updaten
        changevaluelabel(i)
    #straal updaten
        thr = setsizeThread(i,getvalue(i))
        thr.start()
        # thr.setprev(sizethreads[i])
        sizethreads[i] = thr
    addtohistory()
    time.sleep(intval)


def createscene(name):
    '''
    Maak een nieuwe scene met een cilinder en 3 bol niveaus
    :param name: titel van de scene
    :return:
    '''
    d = display(title=name, x=0, y=0, center=(0, 0, 0), background=(0, 0, 1))
    d.stereo = 'active'
    createRingoballs(0,rad=2)
    createRingoballs(0)
    createRingoballs(length)
    increasecylinder(None, length)
    checksizeThread().start()
    # print "updating"
    # update(update_interval)




def pulse():
    '''
    Test of de bollen zich aan de waarden kunnen aanpassen
    :return:
    '''
    while 1:
        for i,val in enumerate(sensors):
            setsizeThread(i,4).start()
            time.sleep(0.5)
        changecamera()
        addlevel()
        for i,val in enumerate(sensors):
            setsizeThread(i,1).start()
            time.sleep(0.5)


def playback(filename, intval=1):
    '''
    neemt de waarden uit een .txt file en past de straal van de corresponderende bollen aan.
    :param filename: pad, ten opzichte van de uitvoering van python script.
    :param intval: tijd tussen opeenvolgende straal aannpassingen
    :return: Lijst van alle dictionnaries
    '''

    total = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                print line
                jline = json.loads(line)
                definestaticradia(jline['value'])
                total.append(jline)
                time.sleep(intval)
        print total
        return total

    except Exception as e:
        print e

def changecamera():
    d = display.get_selected()

if __name__== "__main__":
    createscene("Billy")
    # playback("D:\VakantieJob 2017\Implementatie\3D_pot\Values.txt")
    playback("Values.txt")
    # while 1:
    #     values = [random.uniform(0, 2) for i in range(1, 13)]
    #     update(update_interval)