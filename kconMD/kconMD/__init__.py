from kconMD.force import ComputeForces
from kconMD import kconmd_logging
import time
class kconMD(object):
    def __init__(self,pbfilename,xyzfilename,outputfilename,cell=[0,0,0],pbc=True,cutoff=6,unit=1,vdw=False,nproc=None):
        self.pbfilename=pbfilename
        self.xyzfilename=xyzfilename
        self.cell=cell
        self.pbc=pbc
        self.cutoff=cutoff
        self.outputfilename=outputfilename
        self.unit=unit
        self.vdw=vdw
        self.cf=None
        self.nproc=nproc

    def initcf(self):
        if self.cf==None:
            self.cf=ComputeForces(self.pbfilename,cell=self.cell,pbc=self.pbc,cutoff=self.cutoff,vdw=self.vdw,nproc=self.nproc)

    def printforce(self):
        time1=time.time()
        self.initcf()
        forces=self.cf.predictforcesfromxyz(self.xyzfilename)
        forces*=self.unit
        with open(self.outputfilename,'w') as f:
            for force in forces:
                print(*("%16.9f"%x for x in force),sep='',file=f)
        time2=time.time()
        kconmd_logging("Compute Forces: Time cosumed:",time2-time1,"s")

if __name__=='__main__':
    kconMD("ch4all-120762.pb","ch4.xyz","force",cell=[31.219299,31.219299,31.219299]).printforce()
