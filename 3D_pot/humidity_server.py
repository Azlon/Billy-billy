import SocketServer
import json
import threading

class HumidityServer(SocketServer.TCPServer):
    def __init__(self,server_address,TCPHandler,manager):
        SocketServer.TCPServer.__init__(self,server_address,TCPHandler, bind_and_activate=True)
        self.manager = manager

class TCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def setup(self):
        pass
    def finish(self):
        pass

    def handle(self):
        pot = self.server.manager
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024)
        print "{} requested:".format(self.client_address[0])
        print self.data
        # just send back the same data, but upper-cased
        try:
            id = json.loads(self.data)['req_id']
            self.request.send(str(pot.getvalues()[id]))
        except Exception as e:
            print e

class serverThread(threading.Thread):
    def __init__(self,manager,host = "192.168.0.86" , port = 9999):
        super(serverThread, self).__init__()
        self.port = port
        self.host = host
        self.manager = manager

    def setManager(self,man):
        self.manager = man

    def run(self):
        print "----Started server from thread------"
        server = HumidityServer((self.host, self.port),TCPHandler,self.manager)
        server.serve_forever()

if __name__ == "__main__":
    from capture_humidity import SensorManager
    man = SensorManager()
    HOST, PORT = "192.168.0.86", 9999

    print "----Started server------"
    # Create the server, binding to localhost on port 9999
    server = HumidityServer((HOST, PORT), TCPHandler,man)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()