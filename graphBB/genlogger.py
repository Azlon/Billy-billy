# -*- coding: utf-8 -*-

import ConfigParser
import argparse
import inspect
import itertools
import json
import operator
import os
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import threading
import time

__author__ = 'Maxim'
__copyright__= "Copyright ZoraBots"
__version__ = "20170627 v0.18"

# region Version history
    # MV 20170627 v0.18: Socket address reuse
    # MV 20170524 v0.17: BlueCherry installer toegevoegd
    # MV 20170413 v0.16: Vanaf nu gaat alles terug de gewone verwijderd functie gebruiken, behalve de folder/files (in install.json) die specifiek zegt dat het moet geshred worden
    # MV 20161207 v0.15: Grote schoonmaak gedaan; Classen en subclassen gebruikt; Socket communicatie gebruikt; ZIE CHANGELOG VOOR SPECIFIEKE ZAKEN
    # MV 20160727 v0.14: Gezorgd dat je ook behaviors kan toevoegen die opgestart wordt bij boot;De Composer converter geintergeerd; De wifi installer geintergeerd
    # MV 20160505 v0.13: Kan nu sql queries in de update.json steken en die worden dan uitgevoerd
    # MV 20160428 v0.12: Gezorgd dat de settings van behaviors; general_settings & behavior disable/enable overgenomen worden uit de vorige versie. & Enkel database in ZODataTemp
    # MV 20160422 v0.11: check if .org files (in renamefiles()) already exists, if so don't rename the file; cleanup code; remove versie txt bestand
    # CD 20160104 v0.10: changed remove behaviors (the DeleteBehaviors and not de AddBehaviors), improved snippets
    # CM 20150623 v0.9: added shred file + xShred
    # CM 20150505 v0.8: added qrcode + png python lib installs + alsaaudio.so
    # CM 20150325 v0.7: added wpa_supplicant & sudoers & change pw
    # CM 20150225 v0.6: added the delete all funct
    # CM 20150216 v0.5: added argparse, replace system sounds
    # CM 20150127 v0.4: merged with package script
    # CM 20150126 v0.3: changed to use logger
    # CM 20141106 v0.2: First working version
    # CM 20141021 v0.1: Original version
# endregion

# region Global var

autoExecute = True #HAS TO CHANGE TO TRUE FOR PRODUCTION

HOMEFOLDER = '/home/nao/'
LOGFILENAME = HOMEFOLDER + 'installation.log'
LOGFILEMAXSIZE = 1048576

DATAFILENAME = HOMEFOLDER + "data.log"
ZIPPASSWORD = "qbmt8400"


SOFTWAREZIP = '/home/nao/install.zip'
MIGRATEZIP = '/home/nao/ZOData_export.zip'
EXTRALANGUAGEZIP = '/home/nao/ZOData/extra_language.zip'
EXTRALANGUAGETEMPZIP = "/home/nao/ZODataTemp/extra_language.zip"
SOFTWARETEMP = '/home/nao/tmp/'
TEMPMODULESFOLDER = '/home/nao/tmp/ZOModules'
BEHAVIORSFOLDER = '/home/nao/.local/share/PackageManager/apps/'
BEHAVIORSTEMPFOLDER = '/home/nao/tmp/Behaviors'
SQLSCRIPTFOLDER = '/home/nao/tmp/SqlScripts'


MODULEFOLDER = "/home/nao/ZOModules"
RECORDINGFOLDER = "/home/nao/recordings"
ZODATAFOLDER = "/home/nao/ZOData"
ZODATATEMPFOLDER = "/home/nao/ZODataTemp"
EXTRALANGUAGETEMPFOLDER = "/home/nao/ZODataTemp/extra_languages"
MIGRATETEMPFOLDER = '/home/nao/ZODataExportTemp/'
ADVANCEDPAGE = "/var/www/updatepage"


INSTALLATIONFILE = "/home/nao/installation.json"
UPDATEFILE = "/home/nao/tmp/update.json"
INSTALLERFILE = "/home/nao/tmp/install.json"
INSTALLERFILEAFTERINSTALL = "/home/nao/ZOData/install.json"
UPDATEFILEAFTERINSTALL = "/home/nao/ZOData/update.json"
LANGUAGEREMOVEFILE = "/home/nao/ZOData/remove_languages.json"
DEFAULTLANGUAGEFILE = "/home/nao/ZOData/default_languages.json"
EXTRALANGUAGEFILE = "/home/nao/ZOData/extra_languages.json"
EXTRALANGUAGETEMPFILE = "/home/nao/ZODataTemp/extra_languages.json"

BEHAVIORSDATABASE = '/home/nao/.local/share/PackageManager/pm.db'
MIGRATEDATABASE = "/home/nao/ZODataTemp/zora-control_v2.0.db"
DATABASELOCATION = "/home/nao/ZOData/zora-control_v2.0.db"

logger = None
dlogger = None
parent = None
updater = None
installer = None
deleter = None
migrater = None
zipper = None

installationType = None
installMode = "none"
updateData = None
installData = None

startVersion = None
bodyID = None

errors = []
maxRetryCnt = 3

eyesThread = None
eyesThread_stop = threading.Event()
listenToClientThread = None

# endregion

class ParentHandler():
    '''
    Logger parent which encapsulates the main python logger module.
    '''
    helpers = {}
    t = None

    def __init__(self):
        '''
        Setup the logger and the helpers.
        '''
        global logging,dlogger
        fileFolderHelpers = FileFolderHandlers()
        databaseHelpers = DatabaseHandlers()
        generalHelpers = GeneralHandlers()
        self.socketHelpers = SocketHandlers()

        self.helpers["fileFolderHelpers"] = fileFolderHelpers
        self.helpers["databaseHelpers"] = databaseHelpers
        self.helpers["generalHelpers"] = generalHelpers
        self.helpers["socketHelpers"] = self.socketHelpers

        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handlers = []

    def configLogger(self):
        """
        Setup the logger, add the base level for letting messages through, configure the format of each entry, written in the
        logger file and finally set the each handlers which will relay the messages. In this case, a stream is required, plotting the log entries to
        the console (StreamHandler) and a file handler which will log the values but only for a specific amount of files
        :return:
        """
        global logger,dlogger

        logger = logging.getLogger('Sensor logging')
        dlogger = logging.getLogger('Sensor capture')

        logger.setLevel(logging.DEBUG)
        dlogger.setLevel(logging.DEBUG)

        try:

            #Makes file if  not exists?
            #set relay handlers

            self.fh = logging.handlers.RotatingFileHandler(LOGFILENAME, maxBytes=LOGFILEMAXSIZE, backupCount=5)
            self.dh = logging.handlers.RotatingFileHandler(DATAFILENAME, maxBytes=LOGFILEMAXSIZE, backupCount=10)
            self.ch = logging.StreamHandler()

            #set propagating level
            self.fh.setLevel(logging.DEBUG)
            self.dh.setLevel(logging.DEBUG)
            self.ch.setLevel(logging.DEBUG)

            #define format for propagating log strings
            chfrm = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fhfrm = logging.Formatter('%(levelname)s  -- %(message)s')
            dhfrm = logging.Formatter('%(message)s')

            #set format to handlers
            self.fh.setFormatter(chfrm)
            self.ch.setFormatter(fhfrm)
            self.dh.setFormatter(dhfrm)

            #add the handlers to the main logger (root)
            logger.addHandler(self.ch)
            logger.addHandler(self.fh)
            dlogger.addHandler(self.dh)


            self.handlers.extend([self.fh, self.ch,self.dh])

        except Exception as e:
            logger.critical("Error: " + str(e))
            print e
        return

    def setlogname(self, name):
        '''
        set the directory of the log file to homedir + name
        :param name:
        :return:
        '''
        global LOGFILENAME
        LOGFILENAME = HOMEFOLDER + name
        print "DEBUG set log directory to " + str(LOGFILENAME)

    def sethdir(self, home):
        '''
        set the home directory (set home directory) to 'home'
        :param home:
        :return:
        '''
        global HOMEFOLDER
        HOMEFOLDER = home
        print "DEBUG : set home dir to " + str(home)

    def setdname(self, name):
        '''
        set the directory of the data file (with json values) to homedir + name
        :param name:
        :return:
        '''
        global DATAFILENAME
        DATAFILENAME = HOMEFOLDER + name

        print "DEBUG : set data dir to " + str(DATAFILENAME)
    def modstrfrm(self,str):
        '''
        Chaning the format string if neccessary of the stream handler
        :param str:
        :return:
        '''
        global logging
        self.ch.setFormatter(logging.Formatter(str))
        #logger.addhandler?

    def modrffrm(self,str):
        '''
        Changing the file handler format if necessary
        :param str:
        :return:
        '''
        global logging
        self.fh.setFormatter(logging.Formatter(str))


    def modformat(self,str):
        '''
        Change the global format string if necessary
        :param str:
        :return:
        '''
        self.modrffrm(str)
        self.modstrfrm(str)

    def getProxy(self,moduleName):
        return ALProxy(moduleName,"127.0.0.1",9559)

    def executeMethod(self,method,params):
        if not autoExecute:
            answer = raw_input("Continue to execute method {} y/n: ".format(method))
            if str(answer) == "n":
                sys.exit(1)
        return self.execute(method,params)

    def execute(self,method,params):
        helper = self.findHelper(method)
        methodCall = getattr(helper,method)
        arguments = inspect.getargspec(methodCall).args
        arguments.pop(0)
        return methodCall(*params)

    def findHelper(self,method):
        for helper in self.helpers:
            methods = self.getChildMethods(inspect.getmembers(self.helpers[helper], predicate=inspect.ismethod))
            if method in methods:
                return self.helpers[helper]
        return None

    def getChildMethods(self,methods):
        childMethods = []
        for method in methods:
            if not hasattr(ParentHandler, method[0]):
                childMethods.append(method[0])

        return childMethods


    def jsonlog(self,json):
        dlogger.info(json)

    def error(self,message):
        global errors
        errors.append(message)
        logger.error(message)



    def showErrors(self):
        self.info(">>Script ended with {} error(s)".format(len(errors)),True)
        if len(errors) > 0:
            for error in errors:
                self.info("{}".format(error),True)
        self.info("<<",True)

    def info(self,message, sendToClient):
        if sendToClient:
            self.sendToClient(message)
        logger.info(message)

    def critical(self,message):
        logger.critical(message)

    def warning(self, message):
        logger.warning(message)


    def checkpoint(self,type):
        self.sendToClient("CHECKPOINT: {}".format(type))

    def startStopSocketServer(self,start):
        global listenToClientThread
        if start:
            self.socketHelpers.openSocketServer()
            listenToClientThread = threading.Thread(target=self.socketHelpers.acceptingClients)
            listenToClientThread.start()
        else:
            if listenToClientThread is not None:
                self.socketHelpers.closeSocketThread()
                listenToClientThread.join()
                listenToClientThread = None
                self.socketHelpers.closeSocketServer()

    def sendToClient(self, message):
        msg = str(message)+"\n"
        self.execute("sendMessage",[msg])


class SocketHandlers(ParentHandler):
    serverIp = ""
    port = 0
    server = None
    connection = None

    def __init__(self):
        self.serverIp = "0.0.0.0"
        self.port = 1025

    def openSocketServer(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.serverIp,self.port))
            self.server.listen(5)
            self.info("Server created, ready to accept clients",False)
        except socket.error as e:
            self.warning("Socket error, open socket: {}".format(e))
            self.server = None

    def closeSocketServer(self):
        try:
            if self.server is not None:
                self.server.close()
                self.connection = None
                self.server = None
        except socket.error as e:
            self.warning("Socket error, close socket: {}".format(e))

    def closeSocketThread(self):
        if self.connection is None:
            tmpSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            tmpSocket.connect(("127.0.0.1",self.port))
            tmpSocket.close()

    def acceptingClients(self):
        try:
            self.connection, addr = self.server.accept()
            self.info("Connected with {}:{}".format(addr[0],str(addr[1])),False)
            self.sendMessage("Robot is connected with you\n")
        except socket.error as e:
            self.warning("Socket error, accepting clients: {}".format(e))
            self.connection = None

    def sendMessage(self,message):
        try:
            if self.server is not None and self.connection is not None:
                print "Sending {}".format(message)
                self.connection.send(message)
            else:
                print "Not sending {}".format(message)
        except Exception as e:
            self.warning("Socket error, send message: {}".format(e))

class FileFolderHandlers(ParentHandler):
    def __init__(self):
        pass

    def getAllTheFilesInFolderAndSubfolders(self,srcFolder):
        result = []
        for root, dirs, files in os.walk(srcFolder.encode('utf-8')):
            try:
                for f in files:
                    try:
                        self.info(f.encode('utf-8'),False)
                        result.append(os.path.join(root, f))
                    except Exception as e:
                        self.warning("Could not encode to utf-8, ignore file: {}".format(e))
            except Exception as e:
                self.warning("Could not loop over files, due to ascii encoding problems: {}".format(e))
        return result


    def createFolder(self,foldername):
        try:
            if not os.path.exists(foldername):
                self.info("Create folder {}".format(foldername),False)
                os.makedirs(foldername)
            else:
                self.info("Folder {} already exists".format(foldername),False)
        except:
            txt = "Could not create folder: {}".format(foldername)
            self.error(txt)


    def deleteFolder(self,foldername):
        try:
            if os.path.exists(foldername):
                self.info("Delete folder {}".format(foldername),False)
                delCommand = "rm -rf {}".format(foldername)
                os.system(delCommand)
            else:
                self.info("Could not delete what doesn't exists {}".format(foldername),False)
        except:
            self.error("Couldn't delete folder: {}".format(foldername))

    def shredFolder(self,foldername):
        try:
            if os.path.exists(foldername):
                self.info("Shred folder {}".format(foldername),False)
                shredCommand = "find "+foldername+" -type f -exec shred -fvun 1 {} \;"
                os.system(shredCommand)
                shutil.rmtree(foldername)
            else:
                self.info("Could not shred what doesn't exists {}".format(foldername),False)
        except:
            self.error("Couldn't shred folder: {}".format(foldername))

    def deleteFolderWithExceptions(self,foldername,exceptions):
        try:
            if not os.path.exists(foldername):
                self.info("Can't delete folder with exceptions when it doesn't exists",False)
                return
            files = [os.path.join(foldername,file) for file in os.listdir(foldername) if os.path.splitext(file)[1] not in exceptions]

            for file in files:
                if os.path.isfile(file):
                    self.deleteFile(file)
                if os.path.isdir(file):
                    self.deleteFolder(file)
        except Exception as e:
            print e
            self.error("Could not delete folder {} with exceptions {}".format(foldername,str(exceptions)))

    def shredFolderWithExceptions(self,foldername,exceptions):
        try:
            if not os.path.exists(foldername):
                self.info("Can't delete folder with exceptions when it doesn't exists",False)
                return
            files = [os.path.join(foldername,file) for file in os.listdir(foldername) if os.path.splitext(file)[1] not in exceptions]

            for file in files:
                if os.path.isfile(file):
                    self.shredFile(file)
                if os.path.isdir(file):
                    self.shredFolder(file)
        except Exception as e:
            print e
            self.error("Could not quick delete folder {} with exceptions {}".format(foldername,str(exceptions)))

    def renameFolder(self,srcFolder,destFolder):
        try:
            if not os.path.exists(srcFolder):
                self.info("Can't rename what doesn't exists {}".format(srcFolder),False)
                return
            self.info("Rename folder from {} to {}".format(srcFolder,destFolder),False)
            if os.path.exists(destFolder):
                self.deleteFolder(destFolder)
            os.rename(srcFolder, destFolder)
        except:
            try:
                self.execute("executeCmdCommand",["mv {} {}".format(srcFolder,destFolder)])
            except:
                self.error("Could not rename folder from {} to {}".format(srcFolder,destFolder))


    def createFile(self,filename,content,append):
        f = None
        try:
            if append:
                f = open(filename,'a')
                self.info("Appending file {} with '{}'".format(filename,content),False)
            else:
                f = open(filename,"w")
                self.info("Writing file {} with {}".format(filename,content),False)
            f.write(content)
        except:
            if append:
                self.error("Could not append to file: {}".format(filename))
            else:
                self.error("Could not create file: {}".format(filename))
        finally:
            if f is not None:
                f.close()

    def deleteFile(self,filename):
        try:
            if os.path.isfile(filename):
                self.info("Delete file {}".format(filename),False)
                delCommand = "rm -rf {}".format(filename)
                os.system(delCommand)
            else:
                self.info("Could not find file {}".format(filename),False)
        except:
            self.error("Couldn't delete file: {}".format(filename))

    def shredFile(self,filename):
        try:
            if os.path.isfile(filename):
                self.info("Shred file {}".format(filename),False)
                shredCommand = "shred -ufvn 1 {}".format(filename)
                os.system(shredCommand)
            else:
                self.info("Could not find file {}".format(filename),False)
        except:
            self.error("Couldn't shred file: {}".format(filename))

    def renameFile(self,orgName,newName):
        try:
            if not os.path.exists(newName):
                self.info("rename {} to {}".format(orgName, newName),False)
                os.rename(orgName, newName)
            else:
                self.info("{} already exists".format(newName),False)
        except:
            try:
                self.execute("executeCmdCommand",["mv {} {}".format(orgName,newName)])
            except:
                self.error("Could not rename {} to {}".format(orgName,newName))


    def unzip(self,zipPath,unzipPath,xRemoveExisting,password):
        try:
            if not os.path.exists(zipPath):
                self.error("Zip file {} does not exists".format(zipPath))
                return False
            if os.path.exists(unzipPath) and xRemoveExisting:
                self.deleteFolder(unzipPath)

            if not os.path.exists(unzipPath):
                self.createFolder(unzipPath)

            self.info("Unzipping {} to {}".format(zipPath, unzipPath),False)

            zipLocation = re.escape(zipPath)
            if password:
                cmd = "unzip -P {password} {zipLocation} -d {destinationLocation}".format(password=ZIPPASSWORD,zipLocation=zipLocation,destinationLocation=unzipPath)
            else:
                cmd = "unzip {zipLocation} -d {destinationLocation}".format(zipLocation=zipLocation,destinationLocation=unzipPath)
            os.system(cmd)

            return True
        except Exception as e:
            print e
            self.error("Could not unzip {} to {}".format(zipPath,unzipPath))
            return False

    def zip(self,srcFolder,zipName,fileToZip,password,ignoreCommand):
        if not password:
            cmd = "cd {srcFolder} && zip -r0 {zipName} {fileToZip} -x {ignoreCommand} && cd /home/nao/".format(srcFolder=srcFolder,zipName=zipName,fileToZip=fileToZip,ignoreCommand=ignoreCommand)
        else:
            cmd = "cd {srcFolder} && zip -P {password} -r0 {zipName} {fileToZip} -x {ignoreCommand} && cd /home/nao/".format(srcFolder=srcFolder,zipName=zipName,fileToZip=fileToZip,password=ZIPPASSWORD,ignoreCommand=ignoreCommand)

        print cmd

        os.system(cmd)

    def openJson(self,path):
        data = None
        f = None
        try:
            if not os.path.exists(path):
                self.info("JSON file {} does not exists".format(path),False)
            else:
                self.info("Open JSON file {}".format(path),False)
                f = open(path)
                data = json.load(f)
        except:
            self.error("Could not open the json file {}".format(path))
        finally:
            if f is not None:
                f.close()
            return data

    def writeJson(self,path,data):
        f = None
        try:
            self.info("writing  JSON file {}".format(path),False)
            f = open(path,'w')
            json.dump(data,f,encoding='utf-8',indent=4)
        except:
            self.error("Could not open the json file {}".format(path))
        finally:
            if f is not None:
                f.close()
            return data

    def openConfigIni(self,path):
        config = ConfigParser.RawConfigParser()
        configFile = os.path.join(path, 'zora.ini')
        config.read(configFile)
        return config


    def fullCleanup(self):
        try:
            for file in os.listdir(HOMEFOLDER):
                if file.endswith(".zip") or file == "tmp" or file.endswith(".json"):
                    path = os.path.join(HOMEFOLDER,file)
                    if os.path.isdir(path):
                        self.deleteFolder(path)
                    if os.path.isfile(path):
                        if file.startswith(bodyID):
                            self.shredFile(path)
                        else:
                            self.deleteFile(path)
        except:
            self.error("Could not cleanup, please check manually")

    def removeWithSpecificExtention(self,folder,extentions):
        try:
            for file in os.listdir(folder):
                extention = os.path.splitext(file)[1]
                if extention in extentions:
                    path = os.path.join(folder,file)
                    self.deleteFile(path)
        except Exception as e:
            print e
            self.error("Could not remove with extentions {}".format(extentions))

class GeneralHandlers(ParentHandler):
    def __init__(self):
        pass

    def executeCmdCommand(self,command):
        try:
            self.info("Executing the command {}".format(command),False)
            os.system(command)
        except Exception as e:
            self.error("Could not execute the command {}, {}".format(command,e.message))

    def executeCommand(self, folder, command):
        try:
            if os.path.isdir(folder):
                for f in os.listdir(folder):
                    path = os.path.join(folder,f)
                    if os.path.isdir(path):
                        self.info("Folder: {}".format(path),False)
                        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, cwd=path)
                        (output,err) = p.communicate()
                        p_status = p.wait()
                        self.info("Execute command: {}".format(command),False)
        except Exception as e:
            self.error("Could not execute command {} in {}".format(command,folder))

    def executePythonScript(self,scriptCommand):
        try:
            self.info("Executing script: {}".format(scriptCommand),True)
            output = subprocess.check_output(scriptCommand, shell=True)
            self.info("Script output: {}".format(output),True)
        except Exception as e:
            self.error("Something went wrong while executing the script {}: {}".format(scriptCommand,e))


    def convertingCompositions(self):
        if 'composerConverter.py' in os.listdir(HOMEFOLDER):
            self.info(">>Start converting compositions",True)
            self.executePythonScript("python /home/nao/composerConverter.py")
            self.info("<<Finnished converting compositions",True)

    def installWifi(self):
        if "wifiInstaller.py" in os.listdir(HOMEFOLDER) and "wifi.zip" in os.listdir(HOMEFOLDER):
            self.info(">>Start installing ZoraBots wifi",True)
            self.executePythonScript("python /home/nao/wifiInstaller.py -i")
            self.info("<<Finnished installing ZoraBots wifi",True)

    def deleteWifi(self):
        if "wifiInstaller.py" in os.listdir(HOMEFOLDER):
            self.info(">>Start deleting ZoraBots wifi",True)
            self.executePythonScript("python /home/nao/wifiInstaller.py -d")
            self.info("<<Finnished deleting ZoraBots wifi",True)


    def installBlueCherry(self):
        if "bluecherryInstaller.py" in os.listdir(HOMEFOLDER) and "bluecherry.zip" in os.listdir(HOMEFOLDER):
            self.info(">>Start installing BlueCherry",True)
            self.executePythonScript("python /home/nao/bluecherryInstaller.py -i")
            self.info("<<Finnished installing BlueCherry",True)

    def deleteBlueCherry(self):
        if "bluecherryInstaller.py" in os.listdir(HOMEFOLDER):
            self.info(">>Start deleting BlueCherry",True)
            self.executePythonScript("python /home/nao/bluecherryInstaller.py -d")
            self.info("<<Finnished deleting BlueCherry",True)

    def unzipSoftware(self):
        global bodyID
        memoryProxy = self.getProxy("ALMemory")
        bodyID = memoryProxy.getData("Device/DeviceList/ChestBoard/BodyId")
        modulesFile = None

        for file in os.listdir(HOMEFOLDER):
            if file.startswith(bodyID):
                modulesFile = file
                self.info("Modules found",True)


        if not self.execute("unzip",[SOFTWAREZIP,SOFTWARETEMP,True,False]):
            self.warning("Software could not be installed, cancel further installation!")
            return False

        if (modulesFile != None):
            modulesZip = os.path.join(HOMEFOLDER,modulesFile)
            if not self.execute("unzip",[modulesZip,TEMPMODULESFOLDER,True,False]):
                self.warning("Modules could not be installed, cancel further installation!")
                return False

        return True

    def checkAutoloadini(self):
        encrypted = False
        if not os.path.isdir(TEMPMODULESFOLDER):
            self.error("NO Modules folder present on the robot")

        for file in os.listdir(TEMPMODULESFOLDER):
            if file.endswith(".pyenc"):
                encrypted = True
                break

        if encrypted:
            self.execute("deleteFile",[os.path.join(TEMPMODULESFOLDER,"autoloadNotEncrypted.ini")])
            self.execute("renameFile",[os.path.join(TEMPMODULESFOLDER,"autoloadEncrypted.ini"),os.path.join(TEMPMODULESFOLDER,"autoload.ini")])
        else:
            self.execute("deleteFile",[os.path.join(TEMPMODULESFOLDER,"autoloadEncrypted.ini")])
            self.execute("renameFile",[os.path.join(TEMPMODULESFOLDER,"autoloadNotEncrypted.ini"),os.path.join(TEMPMODULESFOLDER,"autoload.ini")])

    def orangeInstallCheck(self):
        memory = ALProxy("ALMemory","127.0.0.1",9559)
        version = str(memory.getData("RobotConfig/Head/BaseVersion"))
        color = str(memory.getData("RobotConfig/Head/Color"))


        if version == "V4.0" and color == "0":
            self.info("Orange robot(install)",False)
            initialFile = "/media/internal/DeviceHeadInternalGeode.xml"
            orgFile = "/media/internal/DeviceHeadInternalGeode.xml.org"
            newFile = "/home/nao/tmp/Aldebaran_override/DeviceHeadInternalGeode.xml"


            self.execute("renameFile",[initialFile,orgFile])
            self.execute("renameFile",[newFile,initialFile])

    def orangeDeleteCheck(self):
        memory = ALProxy("ALMemory","127.0.0.1",9559)
        color = str(memory.getData("RobotConfig/Head/Color"))

        if color == "OrangeP1645C":
            self.info("Orange robot(delete)",False)

            initialFile = "/media/internal/DeviceHeadInternalGeode.xml"
            orgFile = "/media/internal/DeviceHeadInternalGeode.xml.org"

            self.execute("deleteFile",[initialFile])
            self.execute("renameFile",[orgFile,initialFile])



    def disableAutonomousLife(self,disable):
        try:
            autoStart = "0" if disable == "1" else "1"
            lifeAndDialog = "1" if disable == "1" else "0"

            cmd1 = 'qicli call ALPreferenceManager.setValue --json \\"com.aldebaran.settings\\" \\"AutostartInteractiveConfig\\" \\"{}\\"'.format(autoStart)
            cmd2 = 'qicli call ALPreferenceManager.setValue --json \\"com.aldebaran.debug\\" \\"DisableLifeAndDialog\\" \\"{}\\"'.format(lifeAndDialog)
            self.executeCmdCommand(cmd1)
            self.executeCmdCommand(cmd2)
        except:
            self.warning("Could not disable autonomous life")

    def changePassword(self,password):
        try:
            self.info("Change robot password",False)
            cmd = "passwd nao"
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            p.stdin.write(password + '\n')
            p.stdin.write(password)
            p.stdin.flush()
            (output, err) = p.communicate()
            self.info('passwd:' + str(output) + ':' + str(err),False)
            p_status = p.wait()
            self.info("passwd exit status/return code : " + str(p_status),False)
        except:
            self.error("Could not change password to {}".format(password))

    def disableFallmanager(self,disable):
        try:

            prefProxy = self.getProxy("ALPreferences")
            motionProxy = self.getProxy("ALMotion")

            value = True if disable == "1" else False
            self.info("Change fallmanager: {} - {}".format(disable,value),False)
            motionPref = prefProxy.readPrefFile("ALMotion",False)
            keyExist = False

            for i in range(len(motionPref)):
                if motionPref[i][0] == "ENABLE_DEACTIVATION_OF_FALL_MANAGER":
                    motionPref[i][2] = value
                    keyExist = True

            if not keyExist:
                motionPref.append(["ENABLE_DEACTIVATION_OF_FALL_MANAGER",
                                   "If true the deactivation of Fall Manager is allowed",
                                   value,bool])
            prefProxy.writePrefFile("ALMotion",motionPref,True)
            motionProxy.setMotionConfig([["ENABLE_DEACTIVATION_OF_FALL_MANAGER",value]])

        except Exception as e:
            self.error("Error in disableFallmanager: {}".format(e))

    def changeRobotname(self,robotname):
        try:
            self.info("Change robotname to {}".format(robotname),False)
            systemProxy = self.getProxy("ALSystem")
            systemProxy.setRobotName(str(robotname))
        except Exception as e:
            self.error("Error in changerobotname: {}".format(e))

    def changeTimezone(self,timezone):
        try:
            self.info("Change the timezone to {}".format(timezone),False)
            systemProxy = self.getProxy("ALSystem")
            systemProxy.setTimezone(str(timezone))
        except Exception as e:
            self.error("Error in changeTimezone: {}".format(e))


    def addBehaviors(self,behaviors):
        for behavior in behaviors:
            self.execute("renameFolder",[os.path.join(BEHAVIORSTEMPFOLDER,behavior["source"]),os.path.join(BEHAVIORSFOLDER,behavior["path"])])
            self.execute("addBehaviorToAldebaranDatabase",[behavior])

    def deleteBehaviors(self,behaviors):
        for behavior in behaviors:
            self.removeBehaviorFromBoot(behavior["source"])
            if behavior["shred"] == "0":
                self.execute("deleteFolder",[os.path.join(BEHAVIORSFOLDER,behavior["path"])])
            else:
                self.execute("shredFolder",[os.path.join(BEHAVIORSFOLDER,behavior["path"])])
            self.execute("removeBehaviorFromAldebaranDatabase",[behavior["uuid"]])

    def removeBehaviorFromBoot(self,behavior):
        try:
            self.info("Removing behavior {} from boot process".format(behavior),False)
            behaviorProxy = self.getProxy("ALBehaviorManager")
            behaviorProxy.removeDefaultBehavior(str(behavior))
        except:
            self.info("Behavior {} not part of the boot process".format(behavior),False)

class DatabaseHandlers(ParentHandler):
    def __init__(self):
        self.add = dict()
        self.delete = dict()

    #General helper functions
    def getConnectionString(self):
        config = self.execute("openConfigIni",[updateData["zoraini"]])
        connectionString = config.get('database', 'location')
        return connectionString

    def connect(self,connectionString):
        return sqlite3.connect(connectionString)

    def getZoraControlVersion(self,connectionString):
        result = ""
        try:
            conn = self.connect(connectionString)
            cursor = conn.cursor()
            result = cursor.execute('SELECT * FROM version').fetchall()[0][0]
            conn.close()
        except:
            result = "0.7.2"
        finally:
            self.info("The Zora-control version is {}".format(result),False)
            return str(result)

    def getZoraName(self,connectionString):
        result = ""
        try:
            conn = self.connect(connectionString)
            cur = conn.cursor()
            result = cur.execute("SELECT value FROM general_settings WHERE name='robot_name'").fetchall()[0][0]
            conn.close()
        except:
            result = "Zora"
        finally:
            self.info("The robot name from the database is {}".format(result),False)
            return str(result)

    def makeTupleArray(self,row):
        temp = 0
        insertvalues = ""
        for k, v in row.iteritems():
            temp = temp + 1
            if (isinstance(v, basestring)):
                insertvalues = insertvalues + '"' + v
            elif (isinstance(v, int)):
                insertvalues = insertvalues + str(v)
            else:
                insertvalues = insertvalues + '"' + str(v)

            if (temp < len(row)):
                if (isinstance(v, int)):
                    insertvalues = insertvalues + ","
                else:
                    insertvalues = insertvalues + '",'
            if (temp == len(row) and not isinstance(v, int)):
                insertvalues = insertvalues + '"'
        return insertvalues

    def getColumnNames(self,table,connectionString):
        conn = self.connect(connectionString)
        cur = conn.cursor()
        query = "SELECT * FROM {}".format(table)
        cur.execute(query)
        columns = list(map(lambda x: x[0], cur.description))
        if 'id' in columns:
            columns.remove('id')
        return columns

    def executeQueryAndWrite(self,cur,query,params):
        sql = query
        lenParams = len(params)
        if lenParams > 0:
            for i in range(0,lenParams):
                txt = params[i]
                txt = txt.encode('utf-8') if type(params[i]) == unicode or type(params[i]) == str else txt
                query = query.replace('?',"'{}'".format(txt), 1)

        cur.execute(sql, params)
        return query

    def checkIfTableExistsInDatabase(self,connectionString,tablename):
        conn = self.connect(connectionString)
        cur = conn.cursor()
        self.info(self.executeQueryAndWrite(cur,"SELECT name FROM sqlite_master WHERE type='table' AND name=?",(tablename,)),False)
        result = cur.fetchall()
        conn.close()
        if len(result) > 0:
            return True
        else:
            return False

    def executeSql(self,query,connectionString):
        conn = self.connect(connectionString)
        cur = conn.cursor()
        self.info(self.executeQueryAndWrite(cur,query,()),False)
        conn.commit()
        conn.close()

    def executeSqlScripts(self,script):
        connectionString = self.getConnectionString()
        conn = self.connect(connectionString)
        sqlFile = open(script,'r').read()
        cur = conn.cursor()
        cur.executescript(sqlFile)

    #Backup & restore languages
    def getLanguageDetailsFromAldebaranDatabase(self):
        result = None
        try:
            conn = self.connect(BEHAVIORSDATABASE)
            self.info("Getting language from database",False)
            cur = conn.cursor()
            query = "SELECT * FROM packages WHERE uuid LIKE 'robot-language-%'"
            self.executeQueryAndWrite(cur,query,tuple())
            result = cur.fetchall()
            conn.close()
        except Exception as e:
            self.error(e)
            result = None
        finally:
            return result

    #For adding/deleting behaviors in aldebaran database
    def verifyBehaviorInAldebaranDatabase(self,behavior):
        conn = self.connect(BEHAVIORSDATABASE)
        result = ""
        try:
            self.info("Verify {}".format(behavior),True)
            cur = conn.cursor()
            query = "SELECT * FROM packages WHERE uuid = ?"
            self.executeQueryAndWrite(cur,query,(behavior,))
            if(len(cur.fetchall()) == 0):
                result = False
            else:
                result = True
        except:
            result = False
        finally:
            conn.close()
            return result

    def addBehaviorToAldebaranDatabase(self,behavior):
        retryCnt = 0

        while(True):
            try:
                conn = self.connect(BEHAVIORSDATABASE)
                self.info("Adding to db: {} ({})".format(behavior["uuid"],retryCnt),True)
                cur = conn.cursor()
                query = "INSERT INTO packages VALUES(?,?,?)"
                self.executeQueryAndWrite(cur, query, (behavior["uuid"],os.path.join(BEHAVIORSFOLDER,behavior["path"]),behavior["installer"]))
                conn.commit()
            except sqlite3.Error, e:
                self.warning("Database error: {}".format(e))
                conn.rollback()
            finally:
                conn.close()

            if self.verifyBehaviorInAldebaranDatabase(behavior["uuid"]):
                break

            retryCnt += 1
            if retryCnt > maxRetryCnt:
                self.error("Could not add {} to db".format(behavior["uuid"]))
                break

    def removeBehaviorFromAldebaranDatabase(self,behavior):
        try:
            self.info("Removing from db: {}".format(behavior),True)
            conn = self.connect(BEHAVIORSDATABASE)
            cur = conn.cursor()
            query = "DELETE FROM packages WHERE uuid=?"
            self.executeQueryAndWrite(cur,query,(behavior,))
            conn.commit()
            conn.close()
        except:
            self.error("Could not remove behavior {} from Aldebaran database".format(behavior))

    #Methods for updating
    def makeNewDbStructure(self, versionOrder, startVersion):
        try:
            self.info("Making new database structure",False)
            startMakingDbStructure = False

            self.add = dict()
            self.delete = dict()
            for version in versionOrder:

                if startMakingDbStructure:
                    for beh, value in updateData[version]["databaseStructureChanges"]["add"].iteritems():
                        for k, val in value.iteritems():
                            try:
                                self.add[beh][k] = val
                            except:
                                self.add[beh] = dict()
                                self.add[beh][k] = val
                    for behdel, valdel in updateData[version]["databaseStructureChanges"]["delete"].iteritems():
                        for deldata in valdel:
                            try:
                                self.delete[behdel].append(deldata)
                            except:
                                self.delete[behdel] = []
                                self.delete[behdel].append(deldata)

                if (version == startVersion):
                    startMakingDbStructure = True

            temp = dict()

            for k1, v1 in self.add.iteritems():
                for key, vk in v1.iteritems():

                    if (not self.delete.has_key(k1) or (self.delete.has_key(k1) and key not in self.delete[k1])):
                        try:
                            temp[k1][key] = vk
                        except:
                            temp[k1] = dict()
                            temp[k1][key] = vk
                    else:
                        if (self.delete.has_key(k1)):
                            self.delete[k1].remove(key)

            self.add = temp
        except Exception as e:
            self.error("Could not make new database structure")

    def copySnippets(self,newDbConnectionString, oldDbConnectionString, checkcol, table):
        try:
            conn = self.connect(oldDbConnectionString)
            conn.row_factory = sqlite3.Row
            conn.text_factory = str
            cursor = conn.cursor()
            rowData = cursor.execute('SELECT * FROM {}'.format(table)).fetchall()

            result = []
            for row in rowData:
                d = dict()
                for column in row.keys():
                    if (not self.delete.has_key(table)):
                        d[column] = row[column]
                    elif (self.delete.has_key(table) and column not in self.delete[table]):
                        d[column] = row[column]

                if (self.add.has_key(table)):
                    for addKey, addValue in self.add[table].iteritems():
                        d[addKey] = addValue

                result.append(d)

            conn.close()

            c = self.connect(newDbConnectionString)
            c.text_factory = str
            cur = c.cursor()

            for row in result:
                insertColumns = ", ".join(k for k in row)
                setValues = ",".join("{k}=?".format(k=k, v=v) for k, v in row.iteritems())
                values = (v for k, v in row.iteritems())
                insertvalues = self.makeTupleArray(row)
                try:
                    checkRowCountQuery = 'SELECT * FROM {}  WHERE {} = ?'.format(table,checkcol)
                    if cur.execute(checkRowCountQuery, (row[checkcol],)).fetchall().__len__() > 0:
                        updateQuery = 'UPDATE {} SET {} WHERE {} = ? '.format(table,setValues,checkcol)
                        self.info("Updating: {}".format(updateQuery),False)
                        cur.execute(updateQuery, tuple(values) + (row[checkcol],))
                    else:
                        insertQuery = 'INSERT INTO {} ({}) VALUES ({})'.format(table,insertColumns,insertvalues)
                        self.info("Inserting: {}".format(insertQuery),False)
                        cur.execute(insertQuery)
                except Exception as e:
                    self.error("There is a fault in the snippet: {}".format(e))
            c.commit()
            c.close()
        except Exception as e:
            self.error("Could not copy snippets: {} ({})".format(table,e))

    #Methods for getting the datasets

    def createDict(self,columns,values):
        v = list(values)
        v.pop(0)
        return dict(zip(columns,v))

    def getDefaultSettings(self,behaviorKeys,connectionString):
        conn = self.connect(connectionString)
        cur = conn.cursor()

        defaultSettings = []
        for behaviorKey in behaviorKeys:
            query = "SELECT * FROM settings WHERE behaviorId='{}_Default'".format(behaviorKey["table"])
            columns = self.getColumnNames("settings",connectionString)
            result = cur.execute(query).fetchall()
            tmp = {"table":behaviorKey["table"],"settings":[],"length":0}
            for line in result:
                defaultSetting = self.createDict(columns,line)
                tmp["settings"].append(defaultSetting)
            tmp["length"] = len(tmp["settings"])
            defaultSettings.append(tmp)
        return defaultSettings

    def compareSettings(self,oldSettings,newSettings):
        difference =  list(set([n["name"] for n in newSettings]) - set([o["name"] for o in oldSettings]))
        settings = []
        for newSetting in newSettings:
            for d in difference:
                if newSetting["name"] == d:
                    newSetting["rootTable"] = "settings"
                    settings.append(newSetting)
        return settings


    def getBehaviors(self, connectionString):
        conn = self.connect(connectionString)
        cur = conn.cursor()
        self.executeQueryAndWrite(cur,"SELECT * FROM behavior WHERE owner='user' OR owner='thirdparty'",())
        result = cur.fetchall()

        behaviorList = []
        columns = self.getColumnNames("behavior",connectionString)
        for line in result:
            behavior = self.createDict(columns,line)
            behavior["rootTable"] = "behavior"
            behaviorList.append(behavior)

        conn.close()
        return behaviorList

    def getDatasets(self, behaviors, connectionString):
        conn = self.connect(connectionString)
        cur = conn.cursor()
        datasetList = []
        for behavior in behaviors:
            if behavior["dataset_table"] is not None and behavior["behavior_key"] is not None:
                query = "SELECT * FROM {} WHERE behaviorId='{}'".format(behavior["dataset_table"],behavior["behavior_key"])
                self.executeQueryAndWrite(cur,query,())
                result = cur.fetchall()
                columns = self.getColumnNames(behavior["dataset_table"],connectionString)
                for line in result:
                    dataset = self.createDict(columns,line)
                    dataset["rootTable"] = behavior["dataset_table"]
                    datasetList.append(dataset)
        conn.close()
        return datasetList

    def getSettings(self, behaviors, connectionString):
        conn = self.connect(connectionString)
        cur = conn.cursor()
        settingsList = []
        for behavior in behaviors:
            if behavior["dataset_table"] is not None and behavior["behavior_key"] is not None:
                query = "SELECT * FROM settings WHERE behaviorId='{}'".format(behavior["behavior_key"])
                result = cur.execute(query).fetchall()
                columns = self.getColumnNames("settings",connectionString)
                for line in result:
                    setting = self.createDict(columns,line)
                    setting["rootTable"] = "settings"
                    settingsList.append(setting)
        conn.close()
        return settingsList

    def getBehaviorKey(self,behaviors, connectionString):
        conn = self.connect(connectionString)
        cur = conn.cursor()
        behaviorKeys = []
        for behavior in behaviors:
            if behavior["dataset_table"] is not None and behavior["behavior_key"] is not None:
                query = "SELECT behavior_key FROM behavior WHERE behavior_key like '{}' and behavior_key != '{}' and owner='QBMT' order by behavior_key DESC limit 1".format(behavior["dataset_table"]+"_%",behavior["dataset_table"]+"_Default")
                result = cur.execute(query).fetchall()
                if len(result) != 0:
                    lastBehaviorKeyQbmt = result[len(result)-1][0]
                    behaviorKeys.append(lastBehaviorKeyQbmt)
                else:
                    behaviorKeys.append(behavior["dataset_table"]+"_000")

        behaviorKeys = list(set(behaviorKeys))
        conn.close()
        return behaviorKeys

    def compareBehaviorKeys(self,old,new):
        compareList = []
        for i in range(0,len(old)):
            oldValues = old[i].split('_')
            newValues = new[i].split('_')
            value = int(newValues[1]) - int(oldValues[1])
            compare = {
                "table":newValues[0],
                "value":value
            }
            compareList.append(compare)
        return compareList

    def setNewBehaviorKeys(self, old, new, key):
        for oldBehaviorKey in old:
            if oldBehaviorKey[key] is not None:
                oldBehaviorKeyValues = oldBehaviorKey[key].split('_')
                newKey = filter(lambda n: n["table"] == oldBehaviorKeyValues[0], new)[0]
                oldBehaviorKey[key] = "{}_{}".format(oldBehaviorKeyValues[0],str(int(oldBehaviorKeyValues[1])+newKey["value"]).zfill(3))
        return old

    def getMissingSettings(self,behaviorKeys,settings,connectionString):
        defaultSettings = self.getDefaultSettings(behaviorKeys,connectionString)
        missingSettings = []
        behaviorIds = []
        tmp = []
        index = 0
        for ds in defaultSettings:
            filteredSettings = filter(lambda s: s['behaviorId'].split('_')[0] == ds["table"], settings)

            keyfunc = operator.itemgetter("behaviorId")
            groupedSettings = [list(grp) for key, grp in itertools.groupby(sorted(filteredSettings, key=keyfunc),key=keyfunc)]

            for gs in groupedSettings:
                behaviorIds.append(gs[0]["behaviorId"])
                tmp.extend(self.compareSettings(gs,ds["settings"]))


        for t in tmp:
            t["behaviorId"] = behaviorIds[index]
            missingSettings.append(dict(t))
            index = index+1

        return missingSettings

    def groupSettings(self,settings, missingsettings):
        settings = settings + missingsettings
        newSettings = []
        keyfunc = operator.itemgetter("behaviorId")
        groupedSettings = [list(grp) for key, grp in itertools.groupby(sorted(settings, key=keyfunc),key=keyfunc)]

        for gs in groupedSettings:
            newSettings.extend(gs)
        return newSettings

    def insertDataIntoNewDatabase(self,values,connectionString):
        conn = self.connect(connectionString)
        cur = conn.cursor()
        for value in values:
            table = value["rootTable"]
            value.pop('rootTable')

            columnValues = tuple()
            if self.existInDatabase(connectionString,table,value.values(),value.keys()):
                sql = self.createUpdataOrInsertQuery("update",table,value.keys(),value.keys())
                columnValues = tuple(value.values()+value.values())
            else:
                sql = self.createUpdataOrInsertQuery("insert",table,value.keys(),value.keys())
                columnValues = tuple(value.values())

            self.info(self.executeQueryAndWrite(cur,sql,columnValues),False)

        conn.commit()
        conn.close()

    #Methods for copying settings
    def compareSettingsAndUpdate(self,oldSettings, newSettings, connectionString):
        settings = []
        for oldSetting in oldSettings:
            for newSetting in newSettings:
                if oldSetting["name"] == newSetting["name"] and oldSetting["behaviorId"] == newSetting["behaviorId"]:
                    if oldSetting["value"] != newSetting["value"]:
                        newSetting["value"] = oldSetting["value"]
                        settings.append(newSetting)
                        break

        conn = self.connect(connectionString)
        cur = conn.cursor()
        for setting in settings:
            query = "UPDATE settings SET value=? WHERE name=? AND behaviorId = ?"
            self.info(self.executeQueryAndWrite(cur,query,(str(setting["value"]),str(setting["name"]),str(setting["behaviorId"]))),False)
        conn.commit()
        conn.close()

    def compareInformationAndUpdate(self,oldSettings,newSettings,connectionString,compareValue, checkValue, table):
        settings = []
        for oldSetting in oldSettings:
            for newSetting in newSettings:
                if oldSetting[compareValue] == newSetting[compareValue]:
                    if oldSetting[checkValue] != newSetting[checkValue]:
                        newSetting[checkValue] = oldSetting[checkValue]
                        settings.append(newSetting)
                        break

        conn = self.connect(connectionString)
        cur = conn.cursor()
        for setting in settings:
            query = "UPDATE {} SET {}=? WHERE {}=?".format(table,checkValue,compareValue)
            self.info(self.executeQueryAndWrite(cur,query,(str(setting[checkValue]),str(setting[compareValue]))),False)
        conn.commit()
        conn.close()

    def getInfoFromTable(self,connectionString,table,columns):
        conn = self.connect(connectionString)
        cur = conn.cursor()

        query = "SELECT {} FROM {}".format(','.join(columns),table)
        result = cur.execute(query).fetchall()
        conn.close()

        data = []
        for r in result:
            d = dict(zip(columns,list(r)))
            data.append(d)

        return data

    #Method for copying Tables
    def existInDatabase(self,connectionString,table,compareValues,columNames):
        conn = self.connect(connectionString)
        cur = conn.cursor()

        whereStatement = "{} = ?".format(columNames[0])
        i = 1
        while i < len(compareValues):
            whereStatement += " AND {} = ?".format(columNames[i])
            i += 1
        query = "SELECT * FROM {} WHERE {}".format(table,whereStatement)

        self.executeQueryAndWrite(cur,query,tuple(compareValues))
        result = cur.fetchall()
        conn.close()
        if len(result) > 0:
            return True
        else:
            return False

    def createUpdataOrInsertQuery(self,type,table,columsToChange,columnsToCheck):
        if type == "update":
            return "UPDATE {} SET {} WHERE {}".format(table,', '.join("{}=?".format(k) for k in columsToChange),' AND '.join("{}=?".format(k) for k in columnsToCheck))
        if type == "insert":
            qmarks = ', '.join(['?'] * len(columsToChange))
            return "INSERT INTO {} ({}) VALUES ({})".format(table,', '.join("{}".format(k) for k in columsToChange),qmarks)

    def updateTableFromDatabase(self,connectionString,data,table):
        conn = self.connect(connectionString)
        cur = conn.cursor()
        for d in data:
            compareValues = [str(d[info]) for info in table["whichColumnToCheckOn"]]
            if self.existInDatabase(connectionString,table["table"],compareValues,table["whichColumnToCheckOn"]):
                if table["allowUpdate"] == "1":
                    columnsToChange = {key:d[key] for key in d.keys() if key in table["whatHasToBeUpdated"]} if len(table["whatHasToBeUpdated"]) != 0 else {key:d[key] for key in d.keys() if key not in table["whichColumnToCheckOn"]}
                    columnsToCheck = {key:d[key] for key in d.keys() if key in table["whichColumnToCheckOn"]}
                    query = self.createUpdataOrInsertQuery("update",table["table"],columnsToChange,columnsToCheck)
                    self.info(self.executeQueryAndWrite(cur,query,tuple(columnsToChange.values() + columnsToCheck.values())),False)
            else:
                if table["allowInsert"] == "1":
                    info = d
                    if "id" in d.keys():
                        info.pop("id")
                    query = self.createUpdataOrInsertQuery("insert",table["table"],info,None)
                    self.info(self.executeQueryAndWrite(cur,query,tuple(d.values())),False)
        conn.commit()
        conn.close()


class Runner():
    def __init__(self):
        self.parent = parent
        self.arguments = None
        self.shutdownThread = None

    def setArguments(self,arguments):
        self.arguments = arguments


    def main(self):
        global installMode
        try:
            installMode = 'none'

            self.parent.startStopSocketServer(True)
            time.sleep(1)

            self.stopRobotFromLogging()

            if self.arguments["version"]:
                self.parent.info("The author of this script is {}".format(__author__),True)
                self.parent.info("The version of the script is {}".format(__version__),True)
                self.parent.info("{}".format(__copyright__),True)
                return

            if self.arguments["delete"]:
                self.startStopWebserver("stop")
                self.mainDelete()
                return

            if self.arguments["install"]:
                self.startStopWebserver("stop")
                self.mainInstall("install")
                return

            if self.arguments["update"]:
                self.startStopWebserver("stop")
                self.mainInstall("update")
                return

            if self.arguments["migrate"]:
                self.mainMigrate()
                return

            if self.arguments["zip"]:
                self.mainZip()
                return

        except SystemExit as se:
            print "SYSTEM EXIT: {}".format(se)
        except KeyboardInterrupt as ke:
            print ke
        finally:
            self.parent.showErrors()
            self.stopEyeSpinner()
            self.startStopWebserver("start")

            self.parent.info("The system will shutdown in 5 seconds",True)
            self.parent.sendToClient("done")
            self.parent.info("---------------------", False)
            self.parent.startStopSocketServer(False)

            if self.arguments["shutdown"]:
                self.mainShutdown()

        return

    def mainInstall(self,mode):
        global updater, installer, eyesThread, installMode, installationType

        installMode = mode

        updater = Updater()
        installer = Installer()

        eyesThread = threading.Thread(target=self.startEyeSpinner, args=(0x00FF0000,eyesThread_stop,))
        eyesThread.start()

        self.parent.info("Initiating {} process".format(installMode),True)

        self.parent.checkpoint("Install/Update")
        self.parent.info(">>Unzipping software",True)
        if not self.parent.executeMethod("unzipSoftware",[]):
            self.parent.warning("Could not unzip installation software. Stopping installation!")
            self.parent.sendToClient("Could not unzip installation software. Stopping installation!\n")
            return

        self.parent.info("<<",True)

        if not self.getUpdateData() or not self.getInstallData():
            self.parent.warning("Could not read update/install file, Stopping installation!")
            self.parent.sendToClient("Could not read update/install file, Stopping installation!\n")
            return

        self.getInstallationType()
        self.parent.info("The installMode is {}".format(installMode), True)
        self.parent.info("The installation type is {}".format(installationType),True)

        if installMode == "update":
            updater.setStartVersion()

        installer.install()
        self.parent.checkpoint("Install/Update")
        self.parent.executeMethod("installWifi",[])
        self.parent.executeMethod("installBlueCherry",[])
        self.parent.checkpoint("Install/Update")
        self.parent.info(">>Cleaning up",True)
        self.parent.executeMethod("fullCleanup",[])
        self.parent.info("<<",True)

        self.parent.info("Successfully {} Zora software".format(installMode),True)

        return

    def mainDelete(self):
        global deleter, eyesThread

        eyesThread = threading.Thread(target=self.startEyeSpinner, args=(0x00FF9900,eyesThread_stop))
        eyesThread.start()
        self.parent.info("Initiating delete process",True)
        deleter = Deleter()
        deleter.removeEverything()
        return

    def mainMigrate(self):
        global updater, migrater, eyesThread

        eyesThread = threading.Thread(target=self.startEyeSpinner, args=(0x00FF00FF,eyesThread_stop))
        eyesThread.start()
        self.parent.info("Initiating migrate process",True)
        updater = Updater()
        migrater = Migrater()
        migrater.migrate()
        return

    def mainZip(self):
        global zipper,eyesThread

        eyesThread = threading.Thread(target=self.startEyeSpinner, args=(0x00FF00FF,eyesThread_stop))
        eyesThread.start()
        self.parent.info("Initiating zip process",True)
        zipper = Zipper()
        zipper.zipping()
        return

    def mainShutdown(self):
        time.sleep(5)
        self.parent.info("SEND COMMAND TO SHUTDOWN",False)
        self.parent.execute("executePythonScript",["shutdown -h now"])


    def startEyeSpinner(self,color,stop_event):
        leds = parent.getProxy("ALLeds")
        while (not stop_event.is_set()):
            leds.rotateEyes(color, 3.0, 4.0)
            stop_event.wait(2)
        leds.reset("FaceLeds")

    def stopEyeSpinner(self):
        global eyesThread
        eyesThread_stop.set()

    def stopRobotFromLogging(self):
        try:
            self.parent.info("Stop robot from logging information",True)
            zologger = self.parent.getProxy("ZOLogger")
            zologger.stopLoggingVariables()
            self.parent.info("Robot isn't logging information anymore",True)
        except:
            self.parent.info("The robot can't stop logging information, because there is no ZOLogger",True)

    def startStopWebserver(self,value):
        try:
            self.parent.info("{} the webserver".format(value.title()),False)
            cmd = "/etc/init.d/nginx {}".format(value)
            self.parent.executeMethod("executeCmdCommand",[cmd])
        except Exception as e:
            self.parent.warning("Couldn't stop webserver: {}".format(e))


    def getUpdateData(self):
        global updateData
        updateData = self.parent.executeMethod("openJson", [UPDATEFILE])
        if updateData is None:
            self.parent.warning("Could not successfully open the update file")
            return False
        return True

    def getInstallData(self):
        global installData
        installData = self.parent.executeMethod("openJson", [INSTALLERFILE])
        if installData is None:
            self.parent.warning("Could not successfully open the install file")
            return False
        return True

    def getInstallationType(self):
        global installationType, installData
        installationType = str(installData["type"])

class Updater():
    def __init__(self):
        self.parent = parent
        self.startVersion = None
        self.latestVersion = None
        self.oldDatabaseConnection = ""
        self.newDatabaseConnection = ""


    def settingStartVersion(self,startVersion):
        self.startVersion = startVersion

    def setStartVersion(self):
        try:
            config = self.parent.executeMethod("openConfigIni",[updateData["zoraini"]])
            connectionString = config.get('database', 'location')
            self.startVersion = self.parent.executeMethod("getZoraControlVersion",[connectionString])
            return True
        except Exception:
            self.parent.error('Zora ini not found')



    def update(self):
        if self.startVersion == None:
            return

        self.parent.info(">>Running update",True)
        versionOrder = updateData["VersionOrder"].split(",")
        self.latestVersion = versionOrder[len(versionOrder)-1]

        self.getDatabaseConnections()
        self.parent.checkpoint("Update")
        self.parent.executeMethod("makeNewDbStructure",[versionOrder,self.startVersion])

        self.parent.checkpoint("Update")
        self.copySnippets()
        self.parent.checkpoint("Update")
        self.copySettings()
        self.parent.checkpoint("Update")
        self.copyTables()
        self.parent.checkpoint("Update")
        self.copyDatasets()
        self.parent.checkpoint("Update")
        self.executeSqlQueries()
        self.parent.checkpoint("Update")
        self.copyFolders()

        self.parent.executeMethod("convertingCompositions",[])
        self.parent.info("<<Finnished update",True)


    def getDatabaseConnections(self):
        self.oldDatabaseConnection = updateData[self.startVersion]["databaseLinkOld"]
        self.newDatabaseConnection = updateData[self.latestVersion]["databaseLinkNew"]

        self.parent.info("Old connectionstring: {}".format(self.oldDatabaseConnection),False)
        self.parent.info("New connectionstring: {}".format(self.newDatabaseConnection),False)


    def copyDatasets(self):
        self.parent.info(">>Copying datasets to new database",True)

        behaviors = self.parent.executeMethod("getBehaviors",[self.oldDatabaseConnection])
        datasets = self.parent.executeMethod("getDatasets",[behaviors, self.oldDatabaseConnection])
        settings = self.parent.executeMethod("getSettings",[behaviors,self.oldDatabaseConnection])
        oldBehaviorKeys = self.parent.executeMethod("getBehaviorKey",[behaviors,self.oldDatabaseConnection])

        newBehaviorKeys = self.parent.executeMethod("getBehaviorKey",[behaviors,self.newDatabaseConnection])
        behaviorKeys = self.parent.executeMethod("compareBehaviorKeys",[oldBehaviorKeys,newBehaviorKeys])

        behaviors = self.parent.executeMethod("setNewBehaviorKeys",[behaviors,behaviorKeys,"behavior_key"])
        datasets = self.parent.executeMethod("setNewBehaviorKeys",[datasets,behaviorKeys,"behaviorId"])
        settings = self.parent.executeMethod("setNewBehaviorKeys",[settings,behaviorKeys,"behaviorId"])
        missingSettings = self.parent.executeMethod("getMissingSettings",[behaviorKeys,settings,self.newDatabaseConnection])
        settings = self.parent.executeMethod("groupSettings",[settings,missingSettings])

        self.parent.executeMethod("insertDataIntoNewDatabase",[behaviors,self.newDatabaseConnection])
        self.parent.executeMethod("insertDataIntoNewDatabase",[datasets,self.newDatabaseConnection])
        self.parent.executeMethod("insertDataIntoNewDatabase",[settings,self.newDatabaseConnection])

        self.parent.info("<<",True)

    def copyFolders(self):
        self.parent.info(">>Copying folder",True)
        for copyFolder in updateData[self.latestVersion]["copyFolders"]:
            if copyFolder["active"] == "1":
                for file in self.parent.executeMethod("getAllTheFilesInFolderAndSubfolders",[copyFolder["fromdir"]]):
                        src = str(file).encode('utf-8')
                        dest = str(file).replace(copyFolder["fromdir"],copyFolder["to"]).encode('utf-8')
                        if os.path.exists(dest):
                            if copyFolder["overrideExisting"] == "1":
                                self.parent.execute("deleteFile",[dest])
                                self.parent.execute("renameFile",[src, dest])
                        else:
                            self.parent.execute("renameFile",[src, dest])
        self.parent.info("<<",True)

    def copySnippets(self):
        self.parent.info(">>Copying snippets to new database",True)
        self.parent.executeMethod("copySnippets",[self.newDatabaseConnection,self.oldDatabaseConnection,"id","speechSnippet"])
        self.parent.executeMethod("copySnippets",[self.newDatabaseConnection,self.oldDatabaseConnection,"id","snippet_category"])
        self.parent.info("<<",True)

    def copySettings(self):
        self.parent.info(">>Copying settings to new database",True)

        oldSettings = self.parent.execute("getInfoFromTable",[self.oldDatabaseConnection,"settings",["name","behaviorId","value"]])
        newSettings = self.parent.execute("getInfoFromTable",[self.newDatabaseConnection,"settings",["name","behaviorId","value"]])

        oldGeneralSettings = self.parent.execute("getInfoFromTable",[self.oldDatabaseConnection,"general_settings",["name","value"]])
        newGeneralSettings = self.parent.execute("getInfoFromTable",[self.newDatabaseConnection,"general_settings",["name","value"]])

        oldBehaviors = self.parent.execute("getInfoFromTable",[self.oldDatabaseConnection,"behavior",["name","status"]])
        newBehaviors = self.parent.execute("getInfoFromTable",[self.newDatabaseConnection,"behavior",["name","status"]])


        self.parent.executeMethod("compareSettingsAndUpdate",[oldSettings,newSettings,self.newDatabaseConnection])
        self.parent.executeMethod("compareInformationAndUpdate",[oldBehaviors,newBehaviors,self.newDatabaseConnection,"name","status","behavior"])
        self.parent.executeMethod("compareInformationAndUpdate",[oldGeneralSettings,newGeneralSettings,self.newDatabaseConnection,"name","value","general_settings"])

        self.parent.info("<<",True)

    def copyTables(self):
        self.parent.info(">>Copy tables to new database",True)
        for data in updateData[self.latestVersion]["copyTables"]:
            if data["active"] == "1":
                if self.parent.execute("checkIfTableExistsInDatabase",[self.oldDatabaseConnection,data["table"]]) and self.parent.execute("checkIfTableExistsInDatabase",[self.newDatabaseConnection,data["table"]]):
                    columnNames = self.parent.execute("getColumnNames",[data["table"],self.oldDatabaseConnection])
                    info = self.parent.execute("getInfoFromTable",[self.oldDatabaseConnection,data["table"],columnNames])
                    self.parent.executeMethod("updateTableFromDatabase",[self.newDatabaseConnection,info,data])
                else:
                    self.parent.warning("{} does not exists in the older database or in the new database".format(data["table"]))
        self.parent.info("<<",True)

    def executeSqlQueries(self):
        self.parent.info(">>Excute SQL queries",True)
        for data in updateData[self.latestVersion]["sqlQueries"]:
            if self.latestVersion == self.startVersion:
                if data["changinInSameVersion"] == "1":
                    self.parent.execute("executeSql",[data["query"],self.newDatabaseConnection])
            else:
                self.parent.execute("executeSql",[data["query"],self.newDatabaseConnection])
        self.parent.info("<<",True)

class Installer():
    def __init__(self):
        self.parent = parent

    def install(self):
        global installationType

        if installationType == "full":
            self.fullInstall()
            return

        if installationType == "language":
            self.removeFiles()
            self.installBehaviors()
            return

        if installationType == "behavior":
            self.removeFiles()
            self.installBehaviors()
            self.runSqlScripts()
            return

        if installationType == "module":
            self.parent.executeMethod("checkAutoloadini",[])
            self.parent.checkpoint("Activate")
            self.deleteFolders()
            self.parent.checkpoint("Activate")
            self.removeFiles()
            self.parent.checkpoint("Activate")
            self.renameFiles()
            self.parent.checkpoint("Activate")
            self.copyFolders()
            self.parent.checkpoint("Activate")
            self.copyFiles()
            self.parent.checkpoint("Activate")
            self.executeCommands()

    def fullInstall(self):
        self.parent.executeMethod("checkAutoloadini",[])
        self.parent.executeMethod("orangeInstallCheck",[])
        self.parent.checkpoint("Install/Update")
        self.deleteFolders()
        self.parent.checkpoint("Install/Update")
        self.renameFiles()
        self.parent.checkpoint("Install/Update")
        self.createFolders()
        self.parent.checkpoint("Install/Update")
        self.removeFiles()

        if installMode == "update":
            self.parent.executeMethod("renameFolder",[ZODATAFOLDER,ZODATATEMPFOLDER])

        self.parent.checkpoint("Install/Update")
        self.copyFolders()
        self.parent.checkpoint("Install/Update")
        self.copyFiles()
        self.parent.checkpoint("Install/Update")
        self.executeCommands()

        self.runSqlScripts()

        if installMode == "update":
            updater.update()
            self.parent.executeMethod("deleteFolderWithExceptions",[ZODATATEMPFOLDER,[".db"]])

        self.parent.checkpoint("Install/Update")
        self.installBehaviors()
        self.parent.executeMethod("executeCmdCommand",["chmod -R 755 /home/nao/.local/share/PackageManager/apps/"])
        self.parent.checkpoint("Install/Update")
        self.config()



    def deleteFolders(self):
        self.parent.info(">>Deleting folders",True)
        for data in installData["deleteFolders"]:
            if data["active"] == "1":
                if data["shred"] == "0":
                    self.parent.executeMethod("deleteFolder",[data["path"]])
                else:
                    self.parent.executeMethod("shredFolder",[data["path"]])
        self.parent.info("<<",True)

    def renameFiles(self):
        self.parent.info(">>Renaming files",True)
        for data in installData["renameFiles"]:
            if data["active"] == "1":
                self.parent.executeMethod("renameFile",[data["fromdir"], data["to"]])
        self.parent.info("<<",True)

    def createFolders(self):
        self.parent.info(">>Creating folders",True)
        for data in installData["createFolders"]:
            if data["active"] == "1":
                self.parent.executeMethod("createFolder",[data["path"]])
        self.parent.info("<<",True)

    def removeFiles(self):
        self.parent.info(">>Removing files",True)
        for data in installData["deleteFiles"]:
            if data["active"] == "1":
                if data["shred"] == "0":
                    self.parent.executeMethod("deleteFile",[data["path"]])
                else:
                    self.parent.executeMethod("shredFile",[data["path"]])



        self.parent.info("<<",True)

    def copyFolders(self):
        self.parent.info(">>Copy folders",True)
        for data in installData["copyFolders"]:
            if data["active"] == "1":
                self.parent.executeMethod("renameFolder",[data["fromdir"], data["to"]])
        self.parent.info("<<",True)

    def copyFiles(self):
        self.parent.info(">>Copy files",True)
        for data in installData["copyFiles"]:
            if data["active"] == "1":
                srcPath = os.path.join(data["fromdir"],data["file"])
                destPath = os.path.join(data["to"],data["file"])
                if os.path.exists(srcPath):
                    self.parent.execute("deleteFile",[destPath])
                self.parent.executeMethod("renameFile",[srcPath, destPath])
        self.parent.info("<<",True)

    def executeCommands(self):
        self.parent.info(">>Execute commands",True)
        for data in installData["command"]:
            if data["active"] == "1":
                if data["changeDir"] == "0":
                    self.parent.executeMethod("executeCmdCommand",[data["command"]])
                else:
                    self.parent.executeMethod("executeCommand",[data["path"],data["command"]])
        self.parent.info("<<",True)

    def installBehaviors(self):
        self.parent.info(">>Installing behaviors",True)
        self.parent.executeMethod("deleteBehaviors",[installData["DeleteBehaviors"]])
        self.parent.executeMethod("addBehaviors",[installData["AddBehaviors"]])
        self.parent.info("<<",True)

    def config(self):
        self.parent.info(">>Robot configuration",True)
        for data in installData["config"]:
            if data["active"] == "1":
                self.parent.executeMethod(str(data["method"]),[str(data["value"])])
        self.parent.info("<<",True)

    def runSqlScripts(self):
        self.parent.info(">>Running SQL scripts",True)
        for data in installData["scripts"]:
            if data["active"] == "1":
                script = os.path.join(SQLSCRIPTFOLDER,str(data["name"]))
                self.parent.executeMethod("executeSqlScripts",[script])
        self.parent.info("<<",True)

class Deleter():
    def __init__(self):
        self.parent = parent
        self.deleteData = None
        self.languageData = None

    def removeEverything(self):
        self.parent.info("Start removing everything...",True)

        if not self.getDeleteData():
            self.parent.warning("Could not read delete file, Stopping installation!")
            return

        self.languageData = self.parent.executeMethod("openJson", [LANGUAGEREMOVEFILE])
        self.parent.checkpoint("Delete")
        self.deleteBehaviors()
        self.parent.checkpoint("Delete")
        self.deleteLanguages()
        self.parent.checkpoint("Delete")
        self.deleteFolders()
        self.parent.checkpoint("Delete")
        self.deleteFiles()
        self.parent.checkpoint("Delete")
        self.revertRenameChanges()

        self.parent.checkpoint("Delete")
        self.parent.executeMethod("shredFolder",[MODULEFOLDER])
        self.parent.checkpoint("Delete")
        self.parent.executeMethod("deleteFolder",[ZODATATEMPFOLDER])
        self.parent.checkpoint("Delete")
        self.parent.executeMethod("deleteFolder",[RECORDINGFOLDER])
        self.parent.checkpoint("Delete")
        self.parent.executeMethod("deleteFolder",[ADVANCEDPAGE])
        self.parent.checkpoint("Delete")
        self.parent.executeMethod("deleteFolder",[ZODATAFOLDER])
        self.parent.executeMethod("orangeDeleteCheck",[])


        self.parent.checkpoint("Delete")
        self.parent.executeMethod("deleteWifi",[])
        self.parent.executeMethod("deleteBlueCherry",[])

        self.parent.executeMethod("removeWithSpecificExtention",[HOMEFOLDER,[".py",".log",".zip",".txt",'.json']])

        self.parent.checkpoint("Delete")
        self.revertConfig()

        self.parent.info("Removed all QBMT firmware from this robot ...",True)
        return


    def getDeleteData(self):
        self.deleteData = self.parent.executeMethod("openJson", [INSTALLERFILEAFTERINSTALL])
        if self.deleteData is None:
            self.parent.error("Could not successfully open the install file")
            return False
        return True


    def deleteBehaviors(self):
        self.parent.info(">>Deleting behaviors",True)
        self.parent.executeMethod("deleteBehaviors",[self.deleteData["AddBehaviors"]])
        self.parent.info("<<",True)

    def deleteLanguages(self):
        self.parent.info(">>Deleting languages",True)
        self.parent.executeMethod("deleteBehaviors",[self.languageData])
        self.parent.info("<<",True)

    def deleteFolders(self):
        self.parent.info(">>Deleting folders",True)
        for data in self.deleteData["createFolders"]:
            if data["active"] == "1":
                if data["shred"] == "0":
                    self.parent.executeMethod("deleteFolder",[data["path"]])
                else:
                    self.parent.executeMethod("shredFolder",[data["path"]])
        self.parent.info("<<",True)

    def deleteFiles(self):
        self.parent.info(">>Deleting files",True)
        for data in self.deleteData["copyFiles"]:
            if data["active"] == "1":
                file = os.path.join(data["to"],data["file"])
                if data["shred"] == "0":
                    self.parent.execute("deleteFile",[file])
                else:
                    self.parent.execute("shredFile",[file])
        self.parent.info("<<",True)

    def revertRenameChanges(self):
        self.parent.info(">>Reverting rename files",True)
        for data in self.deleteData["renameFiles"]:
            if data["active"] == "1":
                self.parent.executeMethod("renameFile",[data["to"],data["fromdir"]])
        self.parent.info("<<",True)

    def revertConfig(self):
        self.parent.info(">>Reverting robot configurations",True)
        for data in self.deleteData["config"]:
            if data["active"] == "1":
                self.parent.executeMethod(data["method"],[data["revertValue"]])
        self.parent.info("<<",True)

class Migrater():
    def __init__(self):
        self.parent = parent
        self.success = False
        self.installingExtraLanguages = False

    def migrate(self):
        self.parent.info("Start migrating ZOData...", True)
        try:
            self.success = False
            self.parent.executeMethod("renameFolder",[ZODATATEMPFOLDER,MIGRATETEMPFOLDER])

            if not self.unzipData():
                self.parent.warning("Could not unzip migration folder. Stopping migration!")
                self.parent.sendToClient("Could not unzip migration folder. Stopping migration!\n")
                return

            if not self.openUpdateFile():
                self.parent.warning("Could not read update file, Stopping migration!")
                self.parent.sendToClient("Could not read update file, Stopping migration!\n")
                return


            if not self.checkVersion():
                self.parent.info("Export version is greater than current version, can't migrate", True)
                return

            updater.update()
            if self.installingExtraLanguages:
                self.installExtraLanguages()

            self.success = True
        except Exception as e:
            self.parent.error("There is an error with the migration process {}".format(e))
        finally:
            self.cleanup()
            self.parent.info("Done with migrating ZOData",True)


    def unzipData(self):
        self.parent.info(">>Unzip ZOData_export",True)
        value = self.parent.executeMethod("unzip",[MIGRATEZIP,ZODATATEMPFOLDER,True,False])
        self.installingExtraLanguages = self.parent.executeMethod("unzip",[EXTRALANGUAGETEMPZIP,EXTRALANGUAGETEMPFOLDER,False,True])
        self.parent.info("<<",True)
        return value

    def openUpdateFile(self):
        global updateData
        updateData = self.parent.executeMethod("openJson", [UPDATEFILEAFTERINSTALL])
        if updateData is None:
            self.parent.warning("Could not successfully open the update file")
            return False
        return True

    def checkVersion(self):
        migrateZoraVersion = self.parent.execute("getZoraControlVersion",[MIGRATEDATABASE])
        currentZoraVersion = self.parent.execute("getZoraControlVersion",[DATABASELOCATION])

        updater.settingStartVersion(migrateZoraVersion)

        if str(migrateZoraVersion) > str(currentZoraVersion):
            return False
        else:
            return True

    def installExtraLanguages(self):
        languages = self.parent.execute("getLanguageDetailsFromAldebaranDatabase",[])
        languages = self.processLanguages(languages)
        needToInstallLanguages = self.compareLanguages(languages)

        for lang in needToInstallLanguages:
            src = os.path.join(EXTRALANGUAGETEMPFOLDER,lang["path"])
            dest = os.path.join(BEHAVIORSFOLDER,lang["path"])
            self.parent.execute("renameFolder",[src,dest])
            self.parent.execute("addBehaviorToAldebaranDatabase",[lang])

    def processLanguages(self,languages):
        languagesObject = []
        try:
            for language in languages:

                langObject = {
                    "uuid":str(language[0]),
                    "path":str(language[0]),
                    "installer":str(language[2])
                }
                languagesObject.append(langObject)
        except Exception as e:
            self.parent.info(e,False)
            self.parent.error("Could not process languages")
            languagesObject = []
        finally:
            return languagesObject

    def compareLanguages(self,languages):
        extraLanguages = self.parent.execute("openJson",[EXTRALANGUAGETEMPFILE])
        needToInstallLanguages = [i for i in extraLanguages if i not in languages]
        self.parent.info(needToInstallLanguages,False)
        return needToInstallLanguages

    def cleanup(self):
        self.parent.info("Cleaning up migration data",True)
        self.parent.executeMethod("deleteFolderWithExceptions",[ZODATATEMPFOLDER,[".db"]])

        if self.success:
            self.parent.executeMethod("deleteFolder",[MIGRATETEMPFOLDER])
        else:
            self.parent.executeMethod("deleteFolder",[ZODATATEMPFOLDER])
            self.parent.executeMethod("renameFolder",[MIGRATETEMPFOLDER,ZODATATEMPFOLDER])

        self.parent.executeMethod("deleteFile",[MIGRATEZIP])

class Zipper():
    def __init__(self):
        self.parent = parent
        self.extraLanguages = None

    def zipping(self):
        self.backupLanguage()
        self.backupZOData()
        self.removeLanguages()

    def backupZOData(self):
        self.parent.info(">>Start zipping ZOData",True)
        self.parent.execute("zip",["/home/nao/ZOData","/home/nao/ZOData_export.zip","*",False,"ZO*.py"])
        self.parent.info("<<",True)

    def backupLanguage(self):
        self.parent.info(">>Backup languages",True)
        languages = self.parent.execute("getLanguageDetailsFromAldebaranDatabase",[])
        languages = self.processLanguages(languages)
        self.extraLanguages = self.compareLanguages(languages)

        if(len(self.extraLanguages) != 0):
            self.parent.execute("writeJson",[EXTRALANGUAGEFILE,self.extraLanguages])

        self.getLanguageFolders(self.extraLanguages)
        self.parent.info("<<",True)

    def processLanguages(self,languages):
        languagesObject = []
        try:
            for language in languages:

                langObject = {
                    "uuid":str(language[0]),
                    "path":str(language[0]),
                    "installer":str(language[2])
                }
                languagesObject.append(langObject)
        except Exception as e:
            self.parent.info(e,False)
            self.parent.error("Could not process languages")
            languagesObject = []
        finally:
            return languagesObject

    def compareLanguages(self,languages):
        defaultLanguages = self.parent.execute("openJson",[DEFAULTLANGUAGEFILE])
        extraLanguages = [i for i in languages if i not in defaultLanguages]
        return extraLanguages

    def getLanguageFolders(self,languages):
        files = ""
        for language in languages:
            files += " {}".format(language["path"])

        self.parent.execute("zip",[BEHAVIORSFOLDER,EXTRALANGUAGEZIP,files,True,""])

    def removeLanguages(self):
        self.parent.execute("deleteFile",[EXTRALANGUAGEZIP])
        self.parent.execute("deleteFile",[EXTRALANGUAGEFILE])


if __name__ == "__main__":
    parent = ParentHandler()
    run = Runner()

    parent.configLogger()
    parent.info("--------------",False)

    if (not os.getuid() == 0):
        parent.warning("This script can only run in su mode")
        parent.warning("Alleviate and start again!")
        sys.exit(1)

    parent.info('Script running from : ' + os.path.dirname(os.path.abspath(__file__)),False)

    parser = argparse.ArgumentParser(description='Zora installer')
    parser.add_argument('-v', '--version', action='store_true', help='Show the script version number')
    parser.add_argument('-i', '--install', action='store_true', help='Start a full install')
    parser.add_argument('-u', '--update', action='store_true', help='Update instead of full install')
    parser.add_argument('-d', '--delete', action='store_true', help='Remove all QBMT firmware from the robot')
    parser.add_argument('-m', '--migrate', action='store_true', help='Migrates ZOData to newer version')
    parser.add_argument('-z', '--zip', action='store_true', help='Zip ZOData')
    parser.add_argument('-shutdown', '--shutdown', action='store_true',help='The robot will be shutdown after installation')

    args = parser.parse_args()

    parent.info("Version:" + __version__,False)

    arguments = {arg:getattr(args,arg) for arg in vars(args)}
    run.setArguments(arguments)
    run.main()
    sys.exit(0)