import threading, time
import jsonrw
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider,Button
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
tlabel = None
history = []
sizethreads = [None for i in range(1,13)]
values = [0 for i in range(1,13)]


#---global parameters-----#
length, radius = 5,5    #lengte en straal van de cilinder
sm = 2                  #default straal van de bollen
bg = 4                  #maximale straal van de bollen
max_volt = 5
size_inc = 0.01         #incrementatie van de straal van de bollen in update()
framerate = 50          #bovengrens van loop uitvoering / seconde
update_interval = 2     #update interval
max_size = 2            #Maximale waarde waarvoor de bollen nog steeds groen uitslaan
multiplier = 1.1

closed = False
pauzed = False

#3D object methoden


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


def removeobject(i, obj):
    '''
    Verwijder de models uit het plane en array
    :param i:
    :param obj:
    :return:
    '''
    obj.visible = False
    del obj
    del sceneobj[i]


def createcylinder(length= 5):
    '''
    Maakt telkens eeen cilinder met een bepaalde lengte
    :param length: lengte van de cilinder
    :return: cilinderobject
    '''
    c = cylinder(pos=(0, 0, 0), axis=(0, length, 0), color=color.red, radius=5)
    sceneobj.append(c)
    return c


def getcylinder():
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

def inccylinder(old, newlength):
    '''
    Verwijdert de vorige cilinder uit de ruimten en plaatst een nieuwe grotere cilinder in de plaats
    :param old:
    :param newlength:
    :return:
    '''
    i,c = getobj(old)
    if i != -1:
        removeobject(i, c)

    createcylinder(newlength)


def createringoballs(height, sm_rad = 1, rad = radius):
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
    s3 = sphere(pos=(-rad, height, 0), radius=sm_rad, color=color.green)

    labels.append(label(pos=(0, labelpos, rad), text ="ABEL %d:\nValue:%0.1f" % (sensid,getvalue(sensid))))
    sensid +=1
    s4 = sphere(pos=(0, height, rad), radius=sm_rad, color=color.green)


    temp = s1,s2,s3,s4
    [sceneobj.append(x) for x in temp]
    [sensors.append(x) for x in temp]
    total  = zip(sensors,values)

    return total


class SizeThr(threading.Thread):
    '''
    Thread om op elk moment de straal van de bollen na te gaan op het overschrijden van een maximale straal
    '''
    def __init__(self):
        super(SizeThr, self).__init__()

    def run(self):
      while 1:
          for i in sensors:
              if i.radius > max_size:
                  i.color = color.red
              else:
                  i.color = color.green


class SetsizeThr(threading.Thread):
    '''
    Laat de bollen krimpen / groeien volgens de waarden die in de 'values' lijst aanwezig zijn.
    '''

    def __init__(self,id,newsize):
        '''

        :param id: SensorID
        :param newsize: nieuwe straal van bol
        '''
        super(SetsizeThr, self).__init__()
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


def getobj(obj):
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
    i,c = getcylinder()
    if i == -1:
        oax = 0
    else:
        oax = c.axis[1]+length
    print "length cylinder : "  + str(oax)
    inccylinder(c, oax)
    createringoballs(oax)



# change = [(x.x,length,x.z) for x in bottom]
# for i,index in enumerate(change):
#      top.append(sphere(pos = change[i], radius = 2, color = color.green))


def createthreads():
    '''
    Maak een lijst van threads aan.
    :return:
    '''
    for i in range(0,12):
        t = SetsizeThr(i, 1)
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
        thr = SetsizeThr(i, getvalue(i))
        thr.start()
        # thr.setprev(sizethreads[i])
        sizethreads[i] = thr
    addtohistory()
    time.sleep(intval)


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


def createscene(name):
    '''
    Maak een nieuwe scene met een cilinder en 3 bol niveaus
    :param name: titel van de scene
    :return:
    '''
    d = display(title=name, x=0, y=0, center=(0, 0, 0), background=(0, 0, 1))
    d.stereo = 'active'

    threading.Thread(target = keycallback, args = [d]).start()

    createringoballs(0, rad=2)
    createringoballs(length / 2)
    createringoballs(length)
    inccylinder(None, length)
    SizeThr().start()

    # print "updating"
    # update(update_interval)


def pulse():
    '''
    Test of de bollen zich aan de waarden kunnen aanpassen
    :return:
    '''
    while 1:
        for i,val in enumerate(sensors):
            SetsizeThr(i, 4).start()
            time.sleep(0.5)
        changecamera()
        addlevel()
        for i,val in enumerate(sensors):
            SetsizeThr(i, 1).start()
            time.sleep(0.5)


def keycallback(*e):
    global closed
    while 1:
        k = e[0].kb.getkey()
        print k
        if k == "ctrl+s":
            print "open plot"
            closed = False


def handle_closed(e):
    global closed
    print "closed figure"
    closed = True


def pauze(e):
    global pauzed
    pauzed = not pauzed


def chintval(val):
    global update_interval
    print "Slider changed to " + str(val)
    update_interval = val
    # update_interval = slider.val
    # amp = slider.val


def playback(filename, intval=1):
    '''
    neemt de waarden uit een  file en past de straal van de corresponderende bollen aan.
    :param filename: pad, ten opzichte van de uitvoering van python script.
    :param intval: tijd tussen opeenvolgende straal aannpassingen
    :return: Lijst van alle dictionnaries
    '''
    global update_interval,tlabel
    update_interval = intval

    #complete lijsten
    loghum=[]
    logtemp = []
    loglight = []
    logmass = []
    x = []
    axhum = []

    #lijst van json strings
    total =  jsonrw.playback(filename)

    try:
        i = 0
        start = time.time()

        axint = plt.axes([0, .97, .8, 0.03])
        axbutt = plt.axes([0.9, .90, .1, 0.05])

        sint = Slider(axint, 'Speed', 1, 10, valinit=1)
        sint.on_changed(chintval)
        butt = Button(axbutt,"Pauze")
        butt.on_clicked(pauze)
        f = plt.figure(1)
        fh = plt.figure(2)


        f.canvas.mpl_connect('close_event', handle_closed)

        # fig , axes = plt.subplots(2,2)
        # titles = ["Weight Sensor","Light Sensors","Temperature"]
        # ylabels = ["Kg","Lux","C"]
        # xlabels = "Times" * 3
        # print axes
        # [ax[0].set(title = title, xlabel = xlabel,ylabel = ylabel) for ax,title,xlabel,ylabel in zip(axes,titles,xlabels,ylabels)]
        # fig, axes = plt.subplots(nrows=6)
        # styles = ['r-', 'g-', 'y-', 'm-', 'k-', 'c-']
        # lines = [ax.plot(x, y, style)[0] for ax, style in zip(axes, styles)]
        #       # axes[0].set_ylim([0,30])
        # axes[1].set_ylim([0,1000])


        ax1 = f.add_subplot(221)
        ax2 = f.add_subplot(222)
        ax3 = f.add_subplot(223)

        ax3.set(title = "Weight sensor",xlabel = "Time", ylabel ="Kg")
        ax2.set(title = "Light sensor" , xlabel = "Time", ylabel = "lux")
        ax1.set(title = "Temperature sensor" ,xlabel = "Time", ylabel = "C")

        ax1.set_ylim([0,30])
        ax2.set_ylim([0,1000])



        for i in range(0, 4):
            for j in range(0, 3):
                index = (i) * 3 + (j)
                t = fh.add_subplot(3, 4, index)
                t.set_xlabel("Time")
                t.set_ylabel("Voltage(V)")
                t.set_title("Sensor: " + str(index))
                axhum.append(t)

        stop = time.time()
        print "Setup took : " + str(stop-start) + " seconds"
        plt.ion()
        for line in total:
            print line
            i  = i + 1
            x.append(i)

            #each sensor has it's static place in the json string
            hum = line['Sensors'][0]['values']
            light =line['Sensors'][1]['values']
            temp =line['Sensors'][2]['values']
            mass = line['Sensors'][3]['values']
            ctime = line['Time']
            tlabel = label(pos = (0,-5,0), text ="Time: %s\n" % (ctime))

            #change spheres according to list (12 elements)
            definestaticradia(hum)

            #complete lists, updated as progressing through playback
            logtemp.append(temp)
            loglight.append(light)
            logback,logfront = zip(*loglight)
            back,front = light
            logmass.append(mass)
            loghum.append(hum)

            #plot points in a scatter fashion
            # markers = ['-','v','^']
            # colors  = ['b','r','r']
            # [a.scatter(i,temp,marker = marker,color = color) for a,marker,color in zip(axes,markers,colors)]

            ax1.scatter(i, temp)
            ax2.scatter(i, front, marker='v', color='r')
            ax2.scatter(i, back, marker='^', color='r')
            ax3.scatter(i, mass)
            for index,item in enumerate(axhum):
                item.scatter(i,hum[index])

            #when paused, loop keeps waiting but GUI remains active
            while pauzed:
                plt.pause(0.001)

            #slider changes update interval
            plt.pause(1/update_interval)

        print "end of file"
        plt.close('all')
    except Exception as e:
        plt.close()
        print e


def changecamera():
    d = display.get_selected()

if __name__== "__main__":
    createscene("Billy")
    # playback("D:\VakantieJob 2017\Implementatie\graphBB\Values.txt")
    playback("./log/data.log")

