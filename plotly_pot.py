import os
import time

import plotly
import plotly.plotly as py
import plotly.tools as tools
from plotly.graph_objs import Scatter, Figure

from graphBB.SensorManager import SensorManager


class plotly_pot:
    def __init__(self,user=None):
        if user is None:
            user = 'billy-billy'
            api_key = 'CvrH1saCD1wrq5Ye4II2'
            stream_tokens = ['gmnwwr1zfx',
                             'bdg9doa78p',
                             '0dm9l4rw79',
                             'jowywz7sad',
                             '3p4wzpsnnl',
                             '76c1c77q9d',
                             'w9bqchwv8u',
                             '40yosz2gtw',
                             'afcw2ruo4o',
                             'if10e1sr8g',
                             'awjk1nulrr',
                             'kurmyxjs6i',
                             'aykdpu63ku']

            self.plot_cred = dict(username=user, api_key=api_key, stream_tokens=stream_tokens)
        else:
            self.plot_cred = plotly.tools.get_credentials_file()

        self.man = SensorManager()
        self.streams = []

    def checkCredentialsfile(self):
        if os.path.exists('/home/pi/.plotly/.credentials'):
            dcred = plotly.tools.get_credentials_file()
            print "*items from .credentials"
            for key, item in enumerate(dcred.items()):

                print "values for " + str(key) + ":" + str(item)

            print "*items from settings:"
            for key,item in enumerate(self.plot_cred.items()):
                print "values for " + str(key) + ":" + str(item)

    def createFigure(self,rows,cols):
            '''
            Create a subplots with al the sensorvalues (12 streaming tokens needed)
            :return: plotly figure object
            '''

            self.checkCredentialsfile()
            size = 12
            titles = tuple("Sensor " + str(i+1) for i in range(0,size))
            fig = tools.make_subplots(rows = rows, cols = cols,subplot_titles=titles)
            for i in range(0,rows):
                for j in range(0,cols):
                    scatter = Scatter(x = [],y= [], stream = dict(token = self.plot_cred['stream_tokens'][i*cols+j], maxpoints = 200))
                    fig.append_trace(scatter,i+1,j+1)
            return fig

    def createwFigure(self):
            print "Checking weight plot credentials here"
            self.checkCredentialsfile()
            print 'Failing here?'
            wscat = Scatter(x = [],y= [], stream = dict(token = self.plot_cred['stream_tokens'][12], maxpoints = 200))
            print 'Scatter object made for weight'
            return wscat

    def createHeatmap(self):
            pass

    def openStreams(self):
            fig = self.createFigure(3,4)
            print "figure made for sensors"
            wfig = Figure(data = [self.createwFigure()])
            print "Figure made for weight"
            #heatmap
            # h = Heatmap(z=[],stream = dict(token = self.plot_cred['stream_tokens'][12]))
            print py.plot(wfig, filename = "Weight from load cell")
            print py.plot(fig, filename='Humidity sensor values 1 - 12')
            for i in range(0,13):
                temp = py.Stream(self.plot_cred['stream_tokens'][i])
                self.streams.append(temp)
                temp.open()

            # print self.streams[0].get_streaming_specs()

            #try heatmap

            # heat = py.Stream(self.plot_cred['stream_tokens'][12])
            # self.streams.append(heat)


    def closeStreams(self):
            for i in self.streams:
                i.close()

    def stream(self):
        """
        Streamt de 12 vochtigheidswaarden naar bijhorende plots op plot.ly/consoleurl
        Zolang de sensorwaarden sequentieel opgeslagen worden , blijft de stream functionaliteit werken.
        :return:
        """

        try:
            self.openStreams()

            while True:
                t = time.strftime("%H:%M:%S")
                print "self.man.getValByID(0): " + str(self.man.getValByID(0))
                for index, value in enumerate(self.man.getValByID(0)):
                    self.streams[index].write({'x': t, 'y': value})
                self.streams[12].write({'x': t, 'y': self.man.getValByID(3)})
                time.sleep(0.5)
        except Exception as e:
            print e
            self.closeStreams()

if __name__ == "__main__":
    pot = plotly_pot()
    pot.stream()

