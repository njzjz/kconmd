#!/usr/bin/env python3
# Jinzhe Zeng
# 2018/08/21
import numpy as np
from ase.io import read
from kconMD.kcnn.predictor import KcnnPredictor
from kconMD.force.feed import Feed
from multiprocessing import Pool

class ComputeForces(object):
    def __init__(self,pbfilename,cell=[0,0,0],pbc=True,cutoff=6,vdw=False):
        self.clf = KcnnPredictor(pbfilename,fixed=True)
        self.cell=cell
        self.pbc=pbc
        self.cutoff=cutoff
        self.maxatoms=self.clf.transformer.max_occurs
        self.feedobject=Feed(self.clf.transformer,self.cutoff)
        self._pool=Pool()
        self.vdw=vdw

    def predictforces(self,atoms):
        self.N=len(atoms)
        forces=np.zeros((self.N,3))
        # NN forces
        feeds=self.feedobject.runmp(atoms,self._pool)
        for i,feed in enumerate(feeds):
            forces[i]=np.array(self.computeforcefromfeed(feed)[0][3*feed['index']:3*feed['index']+3])
        # vdw forces
        if self.vdw:
            forces+=vdw().calculate_forces(atoms)
        # Make the resultant force equal to 0
        if np.abs(np.sum(forces))>0:
            forces-=np.abs(forces)/np.sum(np.abs(forces),0)*np.sum(forces,0)
        return forces

    def computeforcefromfeed(self,feed):
        feed_dict = {self.clf._placeholder_inputs: feed["inputs"],
                     self.clf._placeholder_occurs: feed["occurs"],
                     self.clf._placeholder_weights: feed["weights"],
                     self.clf._placeholder_split_dims: feed["split_dims"],
                     self.clf._placeholder_coefficients: feed["coefficients"],
                     self.clf._placeholder_indexing: feed["indexing"]}
        f_atomics = self.clf._sess.run(self.clf._operator_f_nn, feed_dict=feed_dict)
        return f_atomics

    def predictforcesfromxyz(self,xyzfilename):
        atoms=read(xyzfilename)
        atoms.set_cell(self.cell)
        atoms.set_pbc(self.pbc)
        return self.predictforces(atoms)
