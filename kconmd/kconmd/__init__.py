from ..force import ComputeForces
import time
import numpy as np
import logging


class kconMD:
    def __init__(self, pbfilename, xyzfilename="comb.xyz",
                 outputfilename="force.dat", cell=None, pbc=False, cutoff=6,
                 unit=1, vdw=False, nproc=None):
        self.pbfilename = pbfilename
        self.xyzfilename = xyzfilename
        self.cell = cell if cell else [0, 0, 0]
        self.pbc = pbc
        self.cutoff = cutoff
        self.outputfilename = outputfilename
        self.unit = unit
        self.vdw = vdw
        self.cf = None
        self.nproc = nproc

    def initcf(self):
        if self.cf == None:
            self.cf = ComputeForces(
                self.pbfilename, cell=self.cell, pbc=self.pbc,
                cutoff=self.cutoff, vdw=self.vdw, nproc=self.nproc)

    def printforce(self):
        time1 = time.time()
        self.initcf()
        forces = self.cf.predictforcesfromxyz(self.xyzfilename)
        forces *= self.unit
        np.savetxt(self.outputfilename, forces, fmt='%16.9f')
        time2 = time.time()
        logging.info(f"Compute Forces: Time cosumed: {time2-time1:.3f} s")
