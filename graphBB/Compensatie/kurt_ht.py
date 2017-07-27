import json

import matplotlib.pyplot as plt
import numpy as np

from condcompensate import compensate

figs = []
vals = None

class GradHelper:

    __TEMPNAME__ = "billylog{id}.txt"
    __TEMPDIR__ = "./"

    def __init__(self):
        # ref naar figuren voor on_click
        self.figs = []
        self.currentid = 21

        #huidige json
        self.setdir()

        #plot data
        self.x = []
        self.axes = []
        self.tvals = np.array([])
        self.hvals = np.array([])

        # [f.canvas.mpl_connect('button_press_event', self._onclick) for f in self.figs]
        self.getdata()
        self.setdata()

        print "passed show in init"

    def _next(self,e):
        print "Current id from next : " + str(self.currentid)
        self.currentid += 1
        self._onclick(None)

    def _prev(self,e):
        print "Current id from prev : " + str(self.currentid)
        self.currentid -= 1
        self._onclick(None)

    def setdata(self):
        f1 = plt.figure(1)
        f2 = plt.figure(2)
        self.figs.extend([f1,f2])
        # locnext = [0.9, 0.9, 0.1, 0.1]
        # locprev = [0, 0.9, 0.1, 0.1]
        #
        # for p in self.figs:
        #     axn = p.add_axes(locnext)
        #     axp = p.add_axes(locprev)
        #     bn = widget.Button(axn, "Next")
        #     bp = widget.Button(axp, "Prev")
        #     bn.on_clicked(self._next)
        #     bp.on_clicked(self._prev)

        f1 = self.figs[0]
        self.htax = f1.add_subplot(211)
        self.axes.append(self.htax)

        self.htax.set(title="Normalized")
        self.htax.legend(loc='best')
        self.htax.plot(self.x, self.tnorm, label="Temperature")
        self.htax.plot(self.x, self.hnorm, label="Humidity")

        self.tax = f1.add_subplot(223)
        self.axes.append(self.tax)
        self.tax.set(title="Temperature", ylabel="C", xlabel="#samples")

        self.hax = f1.add_subplot(224)
        self.axes.append(self.hax)
        self.hax.set(title="Humidity", ylabel="%H", xlabel="#samples")

        self.tp = self.tax.plot(self.tvals, c='b', marker='.')
        self.hp = self.hax.plot(self.hvals, c='g', marker='+')

        f2 = self.figs[1]

        thgrad = f2.add_subplot(221)
        self.axes.append(thgrad)
        thgrad.set(title = "Afgeleiden",ylabel = "d(T,H)/s")
        tgrad = np.gradient(self.tvals)
        hgrad = np.gradient(self.hvals)
        thgrad.plot(tgrad,label = "dT/dt")
        thgrad.plot(hgrad,label = "dH/dt")
        thgrad.legend(loc = "best")

        fth = f2.add_subplot(222)
        self.axes.append(fth)
        fth.set(title = "Hum - Temp",ylabel = "%H",xlabel = "C")
        fth.plot(self.tvals,self.hvals)

        s = slice(400,800)
        sx = self.x[s]
        tz = np.polyfit(sx,self.tvals[s],1)
        hz = np.polyfit(sx,self.hvals[s],1)
        tf = np.poly1d(tz)
        hf = np.poly1d(hz)
        self.tax.plot(sx,tf(sx) , label="Lin",c = 'y',marker = '.')
        self.hax.plot(sx,hf(sx),label = "Lineair", c= 'y', marker ='.')
        totgrad = hz[0]/ tz[0]
        print "total gradient H/T : " + str(totgrad)

        chvals = compensate(self.tvals,self.hvals,totgrad)
        cax = f2.add_subplot(223)

        cax.plot(chvals,label ='Compensated humidity', c = 'r', marker = '.')
        plt.show()


    def getdata(self):
        # afhankelijk van de Colin's json formaat
        # = beter: {'x':[...],'y':[... ]
        print " onclicked !!"
        self.setdir()
        with open(self.__dir__) as file:
            vals = json.loads(file.read())

        xy = vals["measurement_plot"]
        self.tvals = [dx["y"] for dx in xy["temperature"]]
        self.hvals = [dx["y"] for dx in xy["humidity"]]
        self.tvals = np.array(self.tvals, dtype=float)
        self.hvals = np.array(self.hvals, dtype=float)

        print "{t} temperature values \n {h} humidity values".format(t=self.tvals, h=self.hvals)
        print "length temperaturelist {lt}, length Humidity list {ht}".format(lt=len(self.tvals), ht=len(self.hvals))
        self.x = np.arange(len(self.tvals))

        self.tnorm = (self.tvals - min(self.tvals)) / (max(self.tvals) - min(self.tvals))
        self.hnorm = (self.hvals - min(self.hvals)) / (max(self.hvals) - min(self.hvals))

        print "tnorm " + str(self.tnorm)
        print "hnrom " + str(self.hnorm)


    def _onclick(self,e):
        self.getdata()
        [p.clear() for p in self.axes]
        # self.setdata()

    def setdir(self):
        self.__dir__ = GradHelper.__TEMPDIR__ + GradHelper.__TEMPNAME__.format(id = self.currentid)
        return self.__dir__

if __name__ == "__main__":

    print 'clicked setting passed'
    g = GradHelper()

