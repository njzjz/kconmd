from kconMD.force import ComputeForces
import time
class kconMD(object):
    def __init__(self,pbfilename,xyzfilename,outputfilename,cell=[0,0,0],pbc=True,cutoff=6,unit=1):
        self.pbfilename=pbfilename
        self.xyzfilename=xyzfilename
        self.cell=cell
        self.pbc=pbc
        self.cutoff=cutoff
        self.outputfilename=outputfilename
        self.unit=unit

    def printforce(self):
        time1=time.time()
        cf=ComputeForces(self.pbfilename,cell=self.cell,pbc=self.pbc,cutoff=self.cutoff)
        forces=cf.predictforcesfromxyz(self.xyzfilename)
        forces*=self.unit
        with open(self.outputfilename,'w') as f:
            for force in forces:
                print("".join("%16.9f"%x for x in force),file=f)
        time2=time.time()
        print("Time cosumed:",time2-time1)

if __name__=='__main__':
    kconMD("ch4all-120762.pb","ch4.xyz","force",cell=[31.219299,31.219299,31.219299]).printforce()
