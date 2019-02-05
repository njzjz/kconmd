import os
import time
import logging


class kconMD_CS(object):
    def __init__(self, server_path="/tmp/kconmd.server",
                 client_path="/tmp/kconmd.client", sleeptime=1):
        self.server_path = server_path
        self.client_path = client_path
        self.sleeptime = sleeptime
        self.rf = None
        self.wf = None
        self._logger = logging.getLogger(self.CStype.upper())

    def mkfifos(self):
        for path in (self.server_path, self.client_path):
            if os.path.exists(path):
                os.remove(path)
            os.mkfifo(path)

    def openfifo(self, path, readonly=True):
        if readonly:
            f = os.open(path, os.O_RDONLY)
        else:
            f = os.open(path, os.O_SYNC | os.O_CREAT | os.O_RDWR)
        return f

    def sendmessage(self, message):
        if self.wf == None:
            self.wf = self.openfifo(self.write_path, readonly=False)
        os.write(self.wf, bytes(message, 'UTF-8'))
        self._logger.info(f"Send message: {message}")

    def response(self):
        while True:
            if self.rf == None:
                self.rf = self.openfifo(self.read_path, readonly=True)
            s = str(os.read(self.rf, 1024), 'UTF-8')
            if len(s) == 0:
                time.sleep(self.sleeptime)
                continue
            self._logger.info(f"Receive message: {s}")
            if "Exit" in s:
                self.self._logger.info("EXIT")
                break
            self.handleMessage(s)

    def handleMessage(self, message):
        pass


class kconMD_server(kconMD_CS):
    def __init__(self, kconMD, server_path="/tmp/kconmd.server",
                 client_path="/tmp/kconmd.client", sleeptime=1):
        kconMD_CS.__init__(self, server_path=server_path,
                           client_path=client_path, sleeptime=sleeptime)
        self._CStype = 'server'
        self.mkfifos()
        self.kconMD = kconMD
        self.kconMD.initcf()
        self._logger.info("Initialization is complete.")

    @property
    def printforce(self):
        return self.kconMD.printforce

    @property
    def read_path(self):
        return self.server_path

    @property
    def write_path(self):
        return self.client_path

    @property
    def CStype(self):
        return 'server'

    def handleMessage(self, message):
        if "Printforce" in message:
            self._logger.info("Print Force")
            self.printforce()
            self.sendmessage("Exit")


class kconMD_client(kconMD_CS):
    def __init__(self, server_path="/tmp/kconmd.server",
                 client_path="/tmp/kconmd.client", sleeptime=1):
        kconMD_CS.__init__(self, server_path=server_path,
                           client_path=client_path, sleeptime=sleeptime)

    @property
    def read_path(self):
        return self.client_path

    @property
    def write_path(self):
        return self.server_path

    @property
    def CStype(self):
        return 'client'

    def printforce(self):
        self.sendmessage("Printforce")
        self.response()

    def exitserver(self):
        self.sendmessage("Exit")
