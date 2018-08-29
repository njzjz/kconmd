import os,time

class kconMD_CS(object):
    def __init__(self,server_path="/tmp/kconmd.server",client_path="/tmp/kconmd.client",sleeptime=1):
        self.server_path=server_path
        self.client_path=client_path
        self.sleeptime=sleeptime
        self.logging_prefix=self.CStype.upper()+":"
        self.rf=None
        self.wf=None

    def mkfifos(self):
        for path in (self.server_path,self.client_path):
            if os.path.exists(path):
                os.remove(path)
            os.mkfifo(path)

    def openfifo(self,path,readonly=True):
        if readonly:
            f=os.open(path, os.O_RDONLY)
        else:
            f=os.open(path, os.O_SYNC | os.O_CREAT | os.O_RDWR)
        return f

    def sendmessage(self,message):
        if self.wf==None:
            self.wf=self.openfifo(self.write_path,readonly=False)
        os.write(self.wf,bytes(message,'UTF-8'))
        print(self.logging_prefix,"Send message:",message)

    def response(self):
        while True:
            if self.rf==None:
                self.rf=self.openfifo(self.read_path,readonly=True)
            s=str(os.read(self.rf,1024),'UTF-8')
            if len(s)==0:
                time.sleep(self.sleeptime)
                continue
            print(self.logging_prefix,"Receive message:",s)
            if "Exit" in s:
                print(self.logging_prefix,"EXIT")
                break
            self.handleMessage(s)

    def handleMessage(self,message):
        pass

class kconMD_server(kconMD_CS):
    def __init__(self,kconMD,server_path="/tmp/kconmd.server",client_path="/tmp/kconmd.client",sleeptime=1):
        self.CStype="server"
        kconMD_CS.__init__(self,server_path=server_path,client_path=client_path,sleeptime=sleeptime)
        self.read_path=self.server_path
        self.write_path=self.client_path
        self.mkfifos()
        self.kconMD=kconMD
        self.kconMD.initcf()
        self.printforce=self.kconMD.printforce

    def handleMessage(self,message):
        if "Printforce" in message:
            print(self.logging_prefix,"Print Force")
            self.printforce()
            self.sendmessage("Exit")

class kconMD_client(kconMD_CS):
    def __init__(self,server_path="/tmp/kconmd.server",client_path="/tmp/kconmd.client",sleeptime=1):
        self.CStype="client"
        kconMD_CS.__init__(self,server_path=server_path,client_path=client_path,sleeptime=sleeptime)
        self.read_path=self.client_path
        self.write_path=self.server_path

    def printforce(self):
        self.sendmessage("Printforce")
        self.response()

    def exitserver(self):
        self.sendmessage("Exit")

