import time,json, datetime, random
import psutil
import genlogger as log
from SensorManager import SensorManager

class JsonRW:
    '''
    Class to write both a logger file, indicating the status of each sample
    and the actual data file on which read/write operations should be executed.
    Should be instantiated only when working with Rasp pi
    '''

    def __init__(self):

        '''
        Initiate the python logger, the sensormanager that encapsulates the sensor readings, the names of the files from
        which data should be read/written and the interval between subsequent samples
        '''

        #intialise default logger
        self.logger = log.ParentHandler()
        self.sensman = SensorManager()

        #apply log file settings
        tm = time.strftime("%Y-%m-%d %H:%M:%S")
        self.fnw = tm
        self.logger.sethdir('/home/pi/')
        self.setlogname(self.fnw)
        self.setdataname('data')
        self.capint = 0.2

        #setup actual logger
        self.logger.configLogger()
        self.logger.info('Name of the logger file is \''+ self.fnw + '\'',False)
        self.logger.info("Setted home directory to : " + log.HOMEFOLDER,False)
        self.logger.info("Setted log directory to: " + log.LOGFILENAME,False)


    def setlogname(self,name):
        '''
        set log directory
        :param name:
        :return:
        '''
        self.fnw = name
        self.logger.setlogname(str(name)+ '.log')

    def sethomedir(self,dir):
        '''
        set path to the home directory
        :param dir:
        :return:
        '''
        self.logger.sethdir(dir)

    def setdataname(self,name):
        self.logger.setdname(str(name) + '.log')

    def capdata(self):
        """
        Capture the sensor values into json strings and write to the corresponding files.
        A logger keeps track what happens in the process.
        :return: A logger file, logger output in console and a data file with only json strings
        """
        start = time.time()
        t = start
        h = 1
        i = 0

        try:
            self.logger.info("Starting capture loop",False)
            self.logger.info("To end process press ctrl+C",False)

            while 1:
                self.df()
                if self.tick(t,h) == -1:
                    i = i + 1
                    row = self.sensman.mkjson()
                    self.logger.jsonlog(row)
                    self.logger.info("Added JSON  " + str(i),False)
                else:
                    t = time.time()
                    h = h + 1

        except KeyboardInterrupt as e:
            self.logger.info("Captured " + str(i) + " Samples (" +  time.strftime("%H:%M:%S",time.gmtime(time.time() - start)) + ")",False)
            self.logger.warning("Capture ended by user")
            print e

        except Exception as e:
            self.logger.critical(str(e))
            print e

    def convsec(self,sec):
        return sec / (60 * 60 * 24)

    def capsimple(self):
        '''
        Writes the sensors values using the context manager, not the actual python logger.

        '''

        history = []
        start = time.time()

        try:
            while not self.htimer(start, 24):
                self.df()
                row = self.sensman.mkjson() + "\n"
                history.append(row)
                with open(self.fnw, 'a') as file:
                    file.write(row)
                time.sleep(self.capint)

            self.logger.info("Starting capture in new file",False)
            self.capsimple()


        except KeyboardInterrupt as e:
            self.logger.info("Interrupted capture process by user",False)
            print e

    def df(self):
        '''
        Log the current disk space usage, periodically logging the disk usage.
        When disk usage is over threshold, raise an exception
        '''

        rio = random.randint(0, 20)
        df = psutil.disk_usage('/').percent
        if rio == 10:
            if df < 20:
                self.logger.info("Plenty of disk space left (" + str(df) + ')',False)
            elif df > 20 and df < 50:
               self.logger.info("Gettting more full : " + str (df) + "%",False)
            elif df> 50 and df < 90:
                self.logger.warning("Disk space reaching limit (" + str(df) + ')')
            elif df > 90:
                self.logger.warning("No disk space left:" + str(df) + "%")
                raise Exception("No disk space")

    def tick(self,start,hours):
        if self.htimer(start,1):
            self.logger.info("Sensor have been actively been plotted for " + str(hours),False)
            return 1
        else:
            return -1

    def htimer(self, start, hours):
        '''
        Standard timer checking whether the time between start timestamp en current time stamp exceeds
        the # hours
        :param start: start time
        :param hours: maximum hours
        :return:
        '''

        stop = time.time()
        if self.convsec(stop-start) > hours:
            return True
        else:
            return False

def playback(fn):
    '''
    Get the data file with the json strings and return the entire file as a list of dictionnaries
    Only needs data file.
    '''

    total = []
    try:
        with open(fn, 'r') as file:
            for line in file:
                total.append(json.loads(line))
                #time.sleep(intval)
        return total
    except Exception as e:
        print e


if __name__ == "__main__":
    mode = "LOGGER"
    rw = JsonRW()

    if mode.upper() == "LOGGER":
        rw.capdata()

    elif mode.upper() == "SIMPLE":
        rw.capsimple()

    # playback("test.txt")