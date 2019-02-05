#!/usr/bin/env python3
# Jinzhe Zeng
# 2018/08/21
from multiprocessing import Pool, cpu_count

import numpy as np
from ase.io import read

from ..kcnn.predictor import KcnnPredictor
from .f_vdw import f_vdw
from .feed import Feed


class ComputeForces:
    def __init__(
            self, pbfilename, cell=None,
            pbc=False, cutoff=6, vdw=False, nproc=None):
        self.clf = KcnnPredictor(pbfilename, fixed=True)
        self.cell = cell if cell else [0, 0, 0]
        self.pbc = pbc
        self.cutoff = cutoff
        self.maxatoms = self.clf.transformer.max_occurs
        self.feedobject = Feed(self.clf.transformer, self.cutoff)
        self.nproc = nproc if nproc else cpu_count()
        self._pool = Pool(self.nproc)
        self.vdw = vdw

    def predictforces(self, atoms):
        self.N = len(atoms)
        forces = np.zeros((self.N, 3))
        # NN forces
        feeds = self.feedobject.runmp(atoms, self._pool)
        for i, feed in enumerate(feeds):
            forces[i] = np.array(self.computeforcefromfeed(
                feed)[0][3*feed['index']:3*feed['index']+3])
        # vdw forces
        if self.vdw:
            forces += f_vdw(cutoff=self.cutoff).calculate_forces(atoms)
        # Make the resultant force equal to 0
        if np.abs(np.sum(forces)) > 0:
            forces -= np.abs(forces)/np.sum(np.abs(forces),
                                            0)*np.sum(forces, 0)
        return forces

    def computeforcefromfeed(self, feed):
        feed_dict = {self.clf._placeholder_inputs: feed["inputs"],
                     self.clf._placeholder_occurs: feed["occurs"],
                     self.clf._placeholder_weights: feed["weights"],
                     self.clf._placeholder_split_dims: feed["split_dims"],
                     self.clf._placeholder_coefficients: feed["coefficients"],
                     self.clf._placeholder_indexing: feed["indexing"]}
        f_atomics = self.clf._sess.run(
            self.clf._operator_f_nn, feed_dict=feed_dict)
        return f_atomics

    def predictforcesfromxyz(self, xyzfilename):
        atoms = read(xyzfilename)
        atoms.set_cell(self.cell)
        atoms.set_pbc(self.pbc)
        return self.predictforces(atoms)
