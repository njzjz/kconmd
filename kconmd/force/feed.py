import numpy as np
from ase import Atoms


class Feed:
    def __init__(self, transformer, cutoff):
        self.cutoff = cutoff
        self._transformer = transformer
        self.maxatoms = self._transformer.max_occurs

    def runmp(self, atoms, pool):
        self.atoms = atoms
        self.N = len(atoms)
        feeds = pool.imap(self.getfeedfromatoms, np.arange(self.N))
        return feeds

    def getfeedfromatoms(self, i):
        traj, index = self.gettraj(i)
        feed = self.get_feed_dict(traj, index)
        return feed

    def get_feed_dict(self, atoms_or_trajectory, index):
        transform_func = self._transformer.transform
        species = atoms_or_trajectory.get_chemical_symbols()
        transformed = transform_func(atoms_or_trajectory)
        ck2 = self._transformer.ck2
        features = transformed.features.reshape((1, 1, -1, ck2))
        weights = transformed.binary_weights.reshape((1, 1, -1, 1))
        occurs = transformed.occurs.reshape((1, 1, 1, -1))
        split_dims = transformed.split_dims
        coefficients = transformed.coefficients.reshape((1, -1, ck2 * 6))
        indexing = transformed.indexing.reshape(
            (1, 3*(len(self._transformer._species)-self._transformer._num_ghosts), -1))
        feed_dict = {"inputs": features,
                     "occurs": occurs,
                     "weights": weights,
                     "split_dims": split_dims,
                     "coefficients": coefficients,
                     "indexing": indexing,
                     "index": index}
        return feed_dict

    def gettraj(self, i):
        distances = self.atoms.get_distances(i, np.arange(self.N), mic=True)
        distances_cutoff = [(distances[i], i) for i in np.arange(
            self.N) if distances[i] < self.cutoff] if self.cutoff > 0 else distances
        distances_cutoff.sort()
        atom_num = {}
        indexs = []
        for distance in distances_cutoff:
            symbol = self.atoms[distance[1]].symbol
            if symbol in atom_num:
                if atom_num[symbol] < self.maxatoms[symbol]:
                    atom_num[symbol] += 1
                    indexs.append(distance[1])
            else:
                if symbol in self.maxatoms:
                    atom_num[symbol] = 1
                    indexs.append(distance[1])
        traj = Atoms([self.atoms[j]
                      for j in indexs], cell=self.atoms.get_cell())
        traj.wrap(center=self.atoms[i].position/self.atoms.get_cell_lengths_and_angles()[
                  0:3], pbc=self.atoms.get_pbc())
        index = indexs.index(i)
        return traj, index
