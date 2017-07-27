import json

import matplotlib.pyplot as plt
import numpy as np

from compensate import compensate

figs = []
vals = None

'''
interessante grafieken:
    13: Bloempot op het einde van de dag water gekregen?
    17: Water gegeven over de middag?
    20: Duidelijkste beeld compensatie requirement
    21,22 : Stijgend verloop temperatuur / vochtigheid op hetzelfde moment

'''


class THProvider:
    '''
    Klasse om alle date uit de JSON's op te slaan. Normering van variabelen :
    t = temperatuur
    h = vochtigheid
    a = 'all'
    norm = normalisatie
    acc = accumulatie
    '''

    __URL__ = "http://billybot.be/api/pot-details/207/day/2017/{month}/{id}/"
    __TEMPNAME__ = "billylog{id}.txt"
    __TEMPDIR__ = "../Log/"

    def __init__(self):
        self.tvals, self.hvals, self.hnorm, self.tnorm, self.acch, self.acct = [np.array([])] * 6
        self.id = 17
        self.allid = [14, 15, 16, 17, 18, 19, 20, 21, 22, 30]
        self._dir_ = None
        self.setall_th()
        self.setcur_th(self.id, True)

    def getnorm_t(self):
        '''
        Normaliseer de temperatuurdata om te vergelijken met vochtigheidsdata
        :return:
        '''
        self.tnorm = (self.tvals - min(self.tvals)) / (max(self.tvals) - min(self.tvals))
        print "tnorm " + str(self.tnorm)

    def getnorm_h(self):
        '''
        Normaliseer de vochtigheidsdata om te vergelijken met de temperatuurdata
        :return:
        '''
        self.hnorm = (self.hvals - min(self.hvals)) / (max(self.hvals) - min(self.hvals))
        print "hnorm " + str(self.hnorm)

    def setdir(self, num):
        '''
        zet het pad naar het huidige bestand met json data
        :param num:
        :return:
        '''
        self.__dir__ = THProvider.__TEMPDIR__ + THProvider.__TEMPNAME__.format(id=num)
        return self.__dir__

    def checksize(self):
        '''
        Controleer of lengte van de temperatuurdata en vochtigheidsdata lijst dezelfde zijn.
        :return:
        '''
        if len(self.hvals) != len(self.tvals):
            raise Exception("TEMP en HUM arrays are not same size")

    def setall_th(self):
        '''
        Accumuleer alle vochtigheid en temperatuur data onder 2 lijst
        :return:
        '''
        for id in self.allid:
            self.setcur_th(id,True)
            self.acch = np.append(self.acch, self.hvals)
            self.acct = np.append(self.acct, self.tvals)
        print "All H values : " + str(self.acch)
        print 'All T values' + str(self.acct)

    def setID(self, id):
        '''
        Zet de huidige nummer van het bestand waaruit data gehaald wordt
        :param id:
        :return:
        '''
        self.id = id
        self.setcur_th(id, True)

    def shift(self, array, samples):
        '''
        Optioneel instellen van een shift tussen de temperatuur en vochtigheidsdata om delay, door het
        opwarmen van de pot geintroduceed,  te compenseren.

        :param array:
        :param samples:
        :return:
        '''
        print "Shifted by {n} samples".format(n=samples)
        return np.roll(array, samples)

    def setcur_th(self, id, phasediff=False):
        '''
        Haal de vochtigheids en temperatuur waarden uit 1 bestand
        :param id:
        :param phasediff:
        :return:
        '''
        # afhankelijk van de Colin's json formaat
        # = beter: {'x':[...],'y':[... ]

        self.setdir(id)
        with open(self.__dir__) as file:
            vals = json.loads(file.read())

        xy = vals["measurement_plot"]
        self.tvals = np.array([dx["y"] for dx in xy["temperature"]], dtype=float)
        self.hvals = np.array([dx["y"] for dx in xy["humidity"]], dtype=float)

        if phasediff:
            self.hvals = self.shift(self.hvals, -100)

        print "{t} temperature values  ".format(t=self.tvals)
        print "{h} humidity values ".format(h=self.hvals)
        print "length temperaturelist {lt}".format(lt=len(self.tvals))
        print "length Humidity list {ht}".format(ht=len(self.hvals))

        self.getnorm_h()
        self.getnorm_t()
        self.checksize()


class GradHelper:
    """
    Klasse om de data uit Provider te plotten.
    """

    def __init__(self):
        # ref naar figuren voor on_click
        self.figs = []

        # plot data
        self.axes = []
        f1 = plt.figure(1)
        f2 = plt.figure(2)
        f3 = plt.figure(3)
        self.figs.extend([f1, f2, f3])

        self.pro = THProvider()
        self.pro.setID(23)

    def plotfigures(self):
        """
        Methode om figuren, axes, attributen en data in te stellen en te plotten.
        :return:
        """
        tvals = self.pro.tvals
        hvals = self.pro.hvals
        tnorm = self.pro.hnorm
        hnorm = self.pro.tnorm
        print "curr norm" + str(tnorm)
        atvals = self.pro.acct
        ahvals = self.pro.acch
        x = np.arange(len(tvals))
        xall = np.arange(len(ahvals))

        f1 = self.figs[0]
        # plotten genormaliseerde figuur
        self.htax = f1.add_subplot(211)
        self.axes.append(self.htax)
        self.htax.set(title="Normalized voor dag : " + str(self.pro.id))
        self.htax.plot(hnorm, label="Temperature")
        self.htax.plot(tnorm, label="Humidity")
        self.htax.legend(loc='best')

        self.tax = f1.add_subplot(223)
        # plotten van temperatuur grafiek
        self.axes.append(self.tax)
        self.tax.set(title="Temperature", ylabel="C", xlabel="#samples")
        self.tp = self.tax.plot(tvals, c='b', marker='.')

        self.hax = f1.add_subplot(224)
        #plotten van vochtigheidswaarden
        self.axes.append(self.hax)
        self.hax.set(title="Humidity", ylabel="%H", xlabel="#samples")
        self.hp = self.hax.plot(hvals, c='g', marker='+')

        f2 = self.figs[1]
        thgrad = f2.add_subplot(223)
        #plotten van afgeleiden van H/ T
        thgrad.set(title="Afgeleiden", ylabel="d(T,H)/s")
        self.axes.append(thgrad)

        tgrad = np.gradient(tvals)
        hgrad = np.gradient(hvals)

        thgrad.plot(tgrad, label="dT/dt")
        thgrad.plot(hgrad, label="dH/dt")
        thgrad.legend(loc="best")

        fth = f2.add_subplot(224)
        #plotten van H/T grafiek
        self.axes.append(fth)
        fth.set(title="Hum - Temp", ylabel="%H", xlabel="C")
        fth.plot(tvals, hvals)

        # bepalen welke domeinen van de functie gebruikt worden om de TVC te berekenen. Normaal gezien rond de 2 % / C
        sh = slice(200, 700)
        st = slice(200, 700)
        stx = x[st]
        shx = x[sh]

        # rico bepalen en plotten
        tz = np.polyfit(stx, tvals[stx], 1)
        hz = np.polyfit(shx, hvals[shx], 1)
        tf = np.poly1d(tz)
        hf = np.poly1d(hz)

        print 'lineair H ' + str(tf)
        print 'lineair T ' + str(hf)
        self.tax.plot(stx, tf(stx), label="Lineair", c='y', marker='.')
        self.hax.plot(shx, hf(shx), label="Lineair", c='y', marker='.')

        # totale dH/dT berekenen. Afzonderlijk, omdat de directe H = f(T) grafiek geen 1 op 1 relatie heeft
        print "Humidity gradient : " + str(hz[0])
        print "Temperature gradient : " + str(tz[0])
        totgrad = hz[0] / tz[0]
        print "Totale gradient H/T : " + str(totgrad)

        # compensatie op vochtigheidswaarden toepassen en vervolgens plotten voor dag(id)
        ds = slice(0, len(tvals))
        chvals = compensate(tvals[ds], hvals[ds],2.)
        print "Compensated humidity :" + str(chvals)

        cax = f2.add_subplot(211)
        #compensatie op alle vochtigheidswaarden toepassen en vervolgens plotten voor alle dagen
        cax.set(title="Compensated humidity", ylabel="%H", xlabel="# samples")
        cax.plot(chvals, label='Compensated humidity', c='r', marker='.')
        cax.plot(hvals, label='Original measur.', c='b', marker='.')
        cax.legend(loc="best")

        # verschillende dagen plotten
        f3 = self.figs[2]
        plt.title("Overzicht Dagen " + str(self.pro.allid))
        # plt.plot(ahvals, label='all H values', marker='.', c='g')
        plt.plot(compensate(atvals, ahvals, 2.), label='all comp. H values', marker='.', c='r')
        ca = np.polyfit(xall, ahvals, 20)
        za = np.poly1d(ca)

        # plt.plot(xall, za(xall), marker='.', c='y', label="beste manuele fit")
        plt.plot(atvals, label='all T values', marker='.', c='b')
        plt.legend(loc='best')
        plt.show()


if __name__ == "__main__":
    g = GradHelper()
    g.plotfigures()

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
