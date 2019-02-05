from math import exp

import numpy as np
from ase.io import read


class f_vdw:
    def __init__(self, cutoff=6):
        self.cutoff = cutoff
        self.kcal_to_eV = 1./23.06035

        swa = 0.00
        swb = 10.00
        d1 = swb - swa
        d7 = pow(d1, 7.0)
        swa2 = swa ** 2
        swa3 = swa ** 3
        swb2 = swb ** 2
        swb3 = swb ** 3

        Tap = [0 for i in range(8)]
        Tap[7] = 20.0 / d7
        Tap[6] = -70.0 * (swa + swb) / d7
        Tap[5] = 84.0 * (swa2 + 3.0*swa*swb + swb2) / d7
        Tap[4] = -35.0 * (swa3 + 9.0*swa2*swb + 9.0*swa*swb2 + swb3) / d7
        Tap[3] = 140.0 * (swa3*swb + 3.0*swa2*swb2 + swa*swb3) / d7
        Tap[2] = -210.0 * (swa3*swb2 + swa2*swb3) / d7
        Tap[1] = 140.0 * swa3 * swb3 / d7
        Tap[0] = (-35.0*swa3*swb2*swb2 + 21.0*swa2*swb3 *
                  swb2 + 7.0*swa*swb3*swb3 + swb3*swb3*swb) / d7
        self.Tap = Tap

        # r_vdW D alpha
        self._twbps = {"C": [1.9133, 0.1853, 9.7602],
                       "H": [1.5904, 0.0419, 9.3557],
                       "O": [1.9236, 0.0904, 10.2127],
                       "CH": [1.4000, 0.1219, 9.8442],
                       "HO": [1.6800, 0.0344, 10.3247],
                       "CO": [1.8523, 0.1131, 9.8442]
                       }
        self.twbpname = {
            "C": {"C": "C", "H": "CH", "O": "CO"},
            "H": {"C": "CH", "H": "H", "O": "HO"},
            "O": {"C": "CO", "H": "HO", "O": "O"}}

    def calculate_forces(self, atoms):
        Tap = self.Tap
        n = len(atoms)
        distances = atoms.get_all_distances(mic=True)
        forces = np.zeros((n, n))
        for i in range(n):
            for j in range(i+1, n):
                r_ij = distances[i][j]
                if r_ij <= self.cutoff:
                    r_vdW, D, alpha = self._twbps[self.twbpname[atoms[i].symbol]
                                                  [atoms[j].symbol]]

                    Tap1 = Tap[7] * r_ij + Tap[6]
                    Tap1 = Tap1 * r_ij + Tap[5]
                    Tap1 = Tap1 * r_ij + Tap[4]
                    Tap1 = Tap1 * r_ij + Tap[3]
                    Tap1 = Tap1 * r_ij + Tap[2]
                    Tap1 = Tap1 * r_ij + Tap[1]
                    Tap1 = Tap1 * r_ij + Tap[0]

                    dTap = 7*Tap[7] * r_ij + 6*Tap[6]
                    dTap = dTap * r_ij + 5*Tap[5]
                    dTap = dTap * r_ij + 4*Tap[4]
                    dTap = dTap * r_ij + 3*Tap[3]
                    dTap = dTap * r_ij + 2*Tap[2]
                    dTap += Tap[1]/r_ij

                    exp1 = exp(alpha * (1.0 - r_ij / r_vdW))
                    exp2 = exp(0.5 * alpha * (1.0 - r_ij / r_vdW))

                    e_vdW = D * (exp1 - 2.0 * exp2)

                    CEvd = dTap*e_vdW - Tap1 * D * \
                        (alpha / r_vdW) * (exp1 - exp2) / r_ij

                    forces[i][j] = -CEvd
                    forces[j][i] = -CEvd

        atomforce = np.zeros((n, 3))
        for i in range(n):
            for j in range(i+1, n):
                atomforce_ij = atoms.get_distance(
                    i, j, mic=True, vector=True)/np.linalg.norm(distances[i][j])*forces[i][j]
                atomforce[i] += -atomforce_ij
                atomforce[j] += atomforce_ij

        atomforce *= self.kcal_to_eV
        return atomforce
