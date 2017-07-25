import json
import threading
import time

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider,Button
from visual import *

#lists
sceneobj = []
sensors = []
labels = []
tlabel = None
history = []
sizethreads = [None for i in range(1,13)]
values = [0 for i in range(1,13)]


# ---global parameters----- #
length, radius = 5,5    # lengte en straal van de cilinder
sm = 2                  # default straal van de bollen
bg = 4                  # maximale straal van de bollen
max_volt = 5            # High level voltage
size_inc = 0.01         # incrementatie van de straal van de bollen in update()
framerate = 50          # bovengrens van loop uitvoering / seconde
update_interval = 2     # update interval
max_size = 1.5          # maximale waarde waarvoor de bollen nog steeds groen uitslaan
max_plot = 200          # maximaal aantal punten die op 1 grafiek (axes) mag getekend worden
max_speed = 10          # Maximale snelheid van playback, zoals ook afgebeeld op de slider
multiplier = 1.1        # Factor om vochtigheidswaarden te vergroten zodat bol volumes zichtbaar worden

closed = False          #flag om aan te duiden of grafiek gesloten is
pauzed = False          # Flag om aan te duiden of grafiek gepauzeerd is

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
    #print "settting label: " + str(id) + "to " + str(getvalue(id))


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
    #deprecated:
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
    """
    calback dat uitgevoerd wordt als een keystroke gemaakt wordt in de vpython scene
    :param e: keyevent
    :return:
    """
    global closed
    while 1:
        k = e[0].kb.getkey()
        print k
        if k == "ctrl+s":
            print "open plot"
            closed = False


def handle_closed(e):
    """
    callback telkens de grafieken gesloten worden
    :param e: event
    :return:
    """
    global closed
    print "closed figure"
    closed = True


def pauze(e):
    """
    callback telkens de pauze knop wordt ingedrukt.
    :param e:
    :return:
    """
    global pauzed
    pauzed = not pauzed


def chintval(val):
    """
    callback telkens de slider van waarde verandert
    :param val:
    :return:
    """

    global update_interval
    print "Slider changed to " + str(val)
    update_interval = val
    # update_interval = slider.val
    # amp = sliderm.val

def getJSON(fn):

    """
    Get the data file with the json strings and return the entire file as a list of dictionnaries
    Only needs data file.
    :param fn: filename
    :return: totale lijst met jsons
    """

    total = []
    try:
        with open(fn, 'r') as file:
            for line in file:
                total.append(json.loads(line))
                # time.sleep(intval)
        return total
    except Exception as e:
        print e
def functimer(func):
    """
    Decorator wrapper om te timen hoe lang een methode duurt voordat ze afgesloten wordt. Toepassen door
    @functimer boven de methode te plaatsen
    :param func: functie waarvan de uitvoeringstijd geweten wil worden.
    :return:
    """
    def wrapper(*args):
        start = time.time()
        r = func(*args)
        stop = time.time()-start
        print "{method}() took {time} to execute".format(method = func.func_name,time = stop)
        return r
    return wrapper

class PlotSensor:
    """
    Klasse om het aanmaken van axes en de bijhorende attributen te vergemakkelijken.
    Instantieer door de bijhorende keywords mee te geven.
    """
    def __init__(self,**kwargs):
        self.name = kwargs.get("name")
        self.y = kwargs.get("y")
        self.ax = kwargs.get("ax")
        self.max = kwargs.get("max")
        if not self.y:
            self.y = [0] * self.max
        self.x = range(self.max)
        self.xlabel = kwargs.get("xlabel")
        self.ylabel = kwargs.get("ylabel")
        self.auto = kwargs.get("auto_plot")
        print "auto flag: " + str(self.auto)
        if not self.auto:
            self.auto = False

        self._configax()
        self.plotobj = None
        self.figure = kwargs.get("figure")
        self.subflag = kwargs.get("subflag")


    def _adjustax(self):
        """
        Pas de axes aan naarmate de punten geplot worden.
        :return:
        """
        maxx = max(self.x)
        minx = min(self.x)
        maxy = max(self.y)
        miny = min(self.y)
        self.ax.set_xlim(0.9*minx,1.1*maxx)
        self.ax.set_ylim(0.9*miny,1.1* maxy)

    def plot(self,x,y):
        """
        Plot de x en y lijsten als scatter punten op het bijhorende axe object zoals ingesteld bij constructie van de
        de klasse

        :param x: lijst van x waarden (tijd)
        :param y: lijst van y waarden (kg, lux,C,...)
        :return:
        """
        try:
            self._adjustax()
            self.plotobj = self.ax.scatter(x, y)

        except Exception as e:
            print e

    def incx(self):
        """
        Bijhouden van incrementaties en ervoor zorgen dat een maximaal aantal punten op de
        grafiek getekend wordt.
        :return:
        """
        t = self.x[-1]
        self.x = self.x[1:]
        self.x.append(t + 1)

    def addy(self,y):
        """
        Voeg een punt van buitenaf toe aan de lijst. Afhankelijk van de auto_plot atttribuut wordt automatisch
        de plot functie aangeroepen. auto_plot = False vereist nog een extra plot() call op instantie.
        :param y:
        :return:
        """
        self.incx()
        self.y = self.y[1:]
        self.y.append(y)
        if self.auto:
            self.plot(self.x,self.y)

    def mark(self,*args):
        pass

    def remove(self):
        """
        Scatter plot telkens opnieuw verwijderen zodat slechts een aantal punten in de volgende
         addy() calls op de grafiek getekend worden.
        :return:
        """
        self.plotobj.remove()


    @functimer
    def _configax(self):
        """
        Configureren van de scatter plots met naam, xlabel, ylabel en titel zoals aangegeven bij constructie van de
        klasse.
        :return:
        """
        self.ax.set(title=self.name, xlabel=self.xlabel, ylabel = self.ylabel)

def playback(filename, intval=1):
    '''
    neemt de waarden uit een  file en past de straal van de corresponderende bollen aan.
    :param filename: pad, ten opzichte van de uitvoering van python script.
    :param intval: tijd tussen opeenvolgende straal aannpassingen
    :return: Lijst van alle dictionnaries
    '''

    global update_interval,tlabel
    update_interval = intval

    #activeren van interactive mode
    plt.ion()

    #lijst van gemaakte axes
    plots = []
    hplots = []

    #lijst van json strings
    total = getJSON(filename)
    start = time.time()

    #primaire figuur
    f = plt.figure(1)
    fh = plt.figure(2)

    #slider en button
    axint = plt.axes([0.1, .97, .7, 0.03])
    axbutt = plt.axes([0.9, .90, .1, 0.05])
    sint = Slider(axint, 'Speed', 1, max_speed, valinit=1, valfmt = "%1.2f sample(s)/seconde")
    sint.on_changed(chintval)
    butt = Button(axbutt,"Pauze")
    butt.on_clicked(pauze)


    f.canvas.mpl_connect('close_event', handle_closed)

    # plot objecten
    pltw = PlotSensor(name = "Weight Sensor",ylabel = "Weight (gram) ",xlabel = "Time", max = max_plot, ax = f.add_subplot(221),auto_plot=True)
    pltt = PlotSensor(name = "Temperature Sensor ",ylabel = "Temp (C)",xlabel = "Time", max = max_plot, ax = f.add_subplot(222),auto_plot=True)
    pltl = PlotSensor(name = "Light Sensor ",ylabel = "Lux",xlabel = "Time", max = max_plot, ax = f.add_subplot(223),auto_plot=True)

    plots.extend([pltw,pltt,pltl])

    # markeren van geldig interval waarin punten zich kunnen bevinden. (todo)
    pltw.mark([0,10])
    pltt.mark([10,30])
    pltl.mark([0,1000])

    #humidity sensoren toevoegen op een andere figuur
    for i in range(0, 4):
        for j in range(0, 3):
            index = (i) * 3 + (j)
            name = "Sensor: " + str(index)
            tplot = PlotSensor(name = name,ylabel = "volt (U) ",xlabel = "Time", max = max_plot, ax = fh.add_subplot(3, 4, index),auto_plot=True)
            hplots.append(tplot)
            fh.subplots_adjust(hspace = 0.5)
    stop = time.time()
    print "Setup took : " + str(stop-start) + " seconds"

    #Start met JSON extractie en toevoeging aan de plot
    for line in total:
        start  = time.time()
        print line
        #iedere sensor heeft een statische plaats in de json string, moet aangepast worden als sensoren anders
        #geinit() worden

        try:
            hum = line['Sensors'][0]['values']
            light =line['Sensors'][1]['values']
            temp =line['Sensors'][2]['values']
            weight = line['Sensors'][3]['values']
            ctime = line['Time']
            tlabel = label(pos = (0,-5,0), text ="Time: %s\n" % (ctime))

        except:
            print "JSON doesn't have correct formatting"

        #verander de stralen van de bollen
        definestaticradia(hum)

        #voeg elementen toe aan de axes
        pltt.addy(temp[0])
        pltw.addy(weight[0])
        pltl.addy(light[0])
        for plot,value in zip(hplots,hum):
            plot.addy(value)


        #when paused, loop keeps waiting but GUI remains active
        while pauzed:
            plt.pause(0.001)
        print "waiting for pauze GUI"

        #slider changes update interval
        stop = time.time() - start
        print "plotting  values took {time}".format(time=stop)
        plt.pause(1/update_interval)

        [plot.remove() for plot in plots]
        [plot.remove() for plot in hplots]

    print "end of file"
    plt.close('all')


def changecamera():
    d = display.get_selected()

if __name__== "__main__":

    createscene("Billy")
    playback("./log/data.log")

