#!/usr/bin/env python3
# Jinzhe Zeng
# 2018/08/21
import numpy as np
from ase import Atoms
from ase.io import read
from ase.geometry import wrap_positions
from kconMD.kcnn.predictor import KcnnPredictor

class ComputeForces(object):
    def __init__(self,pbfilename,cell=[0,0,0],pbc=True,cutoff=6):
        self.clf = KcnnPredictor(pbfilename,fixed=True)
        self.cell=cell
        self.pbc=pbc
        self.cutoff=cutoff
        self.maxatoms=self.clf.transformer.max_occurs

    def predictatomforce(self,i,atoms):
        distances=atoms.get_distances(i,np.arange(self.N),mic=True)
        distances_cutoff=[(distances[i],i) for i in np.arange(self.N) if distances[i]<self.cutoff] if self.cutoff>0 else distances
        distances_cutoff.sort()
        atom_num={}
        indexs=[]
        for distance in distances_cutoff:
            symbol=atoms[distance[1]].symbol
            if symbol in atom_num:
                if atom_num[symbol]<self.maxatoms[symbol]:
                    atom_num[symbol]+=1
                    indexs.append(distance[1])
            else:
                if symbol in self.maxatoms:
                    atom_num[symbol]=1
                    indexs.append(distance[1])
        traj=Atoms([atoms[j] for j in indexs],cell=atoms.get_cell())
        traj.wrap(center=atoms[i].position/atoms.get_cell_lengths_and_angles()[0:3],pbc=atoms.get_pbc())
        index=indexs.index(i)
        force=np.array(self.clf.predict_forces(traj)[0][3*index:3*index+3])
        return force

    def predictforces(self,atoms):
        self.N=len(atoms)
        forces=np.zeros((self.N,3))
        for i in np.arange(self.N):
            forces[i]=self.predictatomforce(i,atoms)
        return forces

    def predictforcesfromxyz(self,xyzfilename):
        atoms=read(xyzfilename)
        atoms.set_cell(self.cell)
        atoms.set_pbc(self.pbc)
        return self.predictforces(atoms)
