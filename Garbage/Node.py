import random as rand

class Node:
    def __init__(self,maxvalue = 1):
        self.humitity =0
        self.activated = False
        self.bretheren = []
        self.id = 0
        self.maxvalue = maxvalue

    def getvalue(self):
        if(self.humitity > self.maxvalue):
          return self.humitity
        else:
            print "Incorrect sensor reading"

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activate = False

    def linknode(self,node):
        self.bretheren.append(node)

    def __add__(self, other):
        return [other,self]

    def printstatus(self):
        print "Node " + str(self.id) + " has a humidity reading of " + str(self.humitity)

class Level:
    def __init__(self,stage = 1,maxtotal = 12):
        self.stage = stage
        self.nodes = []
        self.levelvalues = []
        self.total = []
        self.maxtotal = maxtotal

    def getsensorbyid(self,id):
        for i in self.nodes:
            if id == i.id:
                return i
        else:
            return -1

    def addsensor(self,node =None):
        if len(self.nodes) >= self.maxtotal:
            print "No more Nodes available"
        else:
            if node is None:
                tnode = Node()
                self.nodes.append(tnode)
            else:
                self.nodes.append(node)

    def delsensor(self,index):
        if index > len(self.nodes)-1:
            print "index exceeded"
        else:
            return self.nodes.pop(index)

    def getsize(self):
        return len(self.nodes)

    def printlevel(self):
        for i,node in enumerate(self.nodes):
            print "Nodes in level:" + str(self.stage)
            print node.printstatus()

    def calcAccList(self):
        values = []
        for i in self.nodes:
            values.append(i.humitity)
        self.total = zip(self.nodes, values)
        return values

    def getAccumulatedValue(self):

        values = self.calcAccList()
        sumnodes = sum(values)
        return sumnodes


class Pot:

    def __init__(self, count=12,levels= 3):
        self.levelcount = levels
        self.levels = []

    def addlevel(self,level):
        self.levels.append(level)

    def addnodetolevel(self,level,node):
        if self.levels[level] is not None:
            self.levels[level].addsensor(node)
        else:
            print "Level is already full"

    def changeidnode(self,id, level, newid):
        sensor = self.levels[level].getsensorbyid(id)
        if id != -1:
            sensor.id = newid
        else:
            print "failed to change id" + str(id) + "to " + str(newid)

    def printPotStatus(self):
        for i in self.levels:
            print i.printlevels

class Logger:

    def __init__(self,nodes):
        self.nodes = nodes

    def printnodes(self):
        for i in self.nodes:
            print i

    def removenode(self,node):
        if node in self.nodes:
            self.nodes.remove(node)
            print "Node removed"
            return True
        else:
            return False

    def addnode(self,node):
        self.nodes.append(node)

if __name__ == "__main__":
    n1 = Node()
    n2 = Node()
    n3 = n1 + n2
    print "N3: "
    for i in n3:
        print str(i)