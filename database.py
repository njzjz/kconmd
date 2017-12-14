#!coding=utf-8
"""
This module defines the utility function to extract xyz files.
"""
from __future__ import print_function, absolute_import

import re
import sys
import time
import numpy as np
from ase.atoms import Atom, Atoms
from ase.db import connect
from ase.calculators.calculator import Calculator
from os.path import splitext, isfile
from os import remove
from constants import hartree_to_ev, SEED
from collections import namedtuple, Counter
from sklearn.model_selection import train_test_split

__author__ = 'Xin Chen'
__email__ = 'Bismarrck@me.com'

"""
A convenient data structure for organizing settings for different xyz files.
"""
XyzFormat = namedtuple(
  "XyzFormat",
  ("name", "energy_patt", "string_patt", "default_unit", "parse_forces")
)

"""
The format of xyz files generated by ASE. Cell and pbc are defined in the header
part. Atomic forces are included.
"""
_ase_xyz = XyzFormat(
  name="ase",
  energy_patt=re.compile(r"Lattice=\"(.*)\".*"
                         r"energy=([\d.-]+)\s+pbc=\"(.*)\""),
  string_patt=re.compile(r"([A-Za-z]{1,2})\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)"
                         r"\s+\d+\s+\d.\d+\s+\d+\s+([\d.-]+)\s+([\d.-]+)\s+"
                         r"([\d.-]+)"),
  default_unit=1.0,
  parse_forces=True
)

"""
The most simple xyz format.
"""
_xyz = XyzFormat(
  name="xyz",
  energy_patt=re.compile(r"([\w.-]+)"),
  string_patt=re.compile(r"([A-Za-z]+)\s+([\w.-]+)\s+([\w.-]+)\s+([\w.-]+)"),
  default_unit=hartree_to_ev,
  parse_forces=False,
)


class ProvidedCalculator(Calculator):
  """
  A simple calculator which just returns the provided energy and forces.
  """

  implemented_properties = ["energy", "forces"]

  def __init__(self, atoms=None):
    """
    Initialization method.

    Args:
      atoms: an optional `ase.Atoms` object to which the calculator will be
        attached.

    """
    Calculator.__init__(self, label="provided", atoms=atoms)

  def set_atoms(self, atoms):
    """
    Set the attached `ase.Atoms` object.
    """
    self.atoms = atoms

  def calculate(self, atoms=None, properties=None, system_changes=None):
    """
    Set the calculation results.
    """
    super(ProvidedCalculator, self).calculate(atoms, properties=properties,
                                              system_changes=system_changes)
    self.results = {
      'energy': self.atoms.info.get('provided_energy', 0.0),
      'forces': self.atoms.info.get('provided_forces',
                                    np.zeros((len(self.atoms), 3)))
    }


def xyz_to_database(xyzfile, num_examples=None, xyz_format='xyz', verbose=True,
                    unit_to_ev=None, restart=False):
  """
  Convert the xyz file to an `ase.db.core.Database`.

  Args:
    xyzfile: a `str` as the file to parse.
    num_examples: a `int` as the maximum number of examples to parse. If None,
      all examples in the given file will be saved.
    xyz_format: a `str` representing the format of the given xyz file.
    verbose: a `bool` indicating whether we should log the parsing progress.
    unit_to_ev: a `float` as the unit for converting energies to eV. Defaults
      to None so that default units will be used.
    restart: a `bool`. If True, the database will be re-built even if already
      existed.

  Returns:
    db: an `ase.db.core.Database`.

  """
  if xyz_format.lower() == 'ase':
    formatter = _ase_xyz
  else:
    formatter = _xyz

  database = "{}.db".format(splitext(xyzfile)[0])
  if isfile(database) and restart:
    remove(database)

  unit = unit_to_ev or formatter.default_unit
  parse_forces = formatter.parse_forces
  count = 0
  ai = 0
  natoms = 0
  stage = 0
  atoms = None
  num_examples = num_examples or np.Infinity

  db = connect(name=database)
  tic = time.time()
  if verbose:
    sys.stdout.write("Extract cartesian coordinates ...\n")
  with open(xyzfile) as f:
    for line in f:
      if count == num_examples:
        break
      line = line.strip()
      if line == "":
        continue
      if stage == 0:
        if line.isdigit():
          natoms = int(line)
          atoms = Atoms(calculator=ProvidedCalculator())
          if parse_forces:
            atoms.info['provided_forces'] = np.zeros((natoms, 3))
          stage += 1
      elif stage == 1:
        m = formatter.energy_patt.search(line)
        if m:
          if xyz_format.lower() == 'extxyz':
            energy = float(m.group(3)) * unit
          elif xyz_format.lower() == 'ase':
            energy = float(m.group(2)) * unit
            atoms.set_cell(
              np.reshape([float(x) for x in m.group(1).split()], (3, 3)))
            atoms.set_pbc(
              [True if x == "T" else False for x in m.group(3).split()])
          else:
            energy = float(m.group(1)) * unit
          atoms.info['provided_energy'] = energy
          stage += 1
      elif stage == 2:
        m = formatter.string_patt.search(line)
        if m:
          atoms.append(Atom(symbol=m.group(1),
                            position=[float(v) for v in m.groups()[1:4]]))
          if parse_forces:
            atoms.info['provided_forces'][ai, :] = [float(v) * unit
                                                    for v in m.groups()[4:7]]
          ai += 1
          if ai == natoms:
            atoms.calc.calculate()
            db.write(atoms)
            ai = 0
            stage = 0
            count += 1
            if verbose and count % 1000 == 0:
              sys.stdout.write(
                "\rProgress: %7d  /  %7d" % (count, num_examples))
    if verbose:
      print("")
      print("Total time: %.3f s\n" % (time.time() - tic))
    return db


class Database:
  """
  A manager class for manipulating the `ase.db.core.Database`.
  """

  def __init__(self, db, random_seed=None):
    """
    Initialization method.

    Args:
      db: a `ase.db.core.Database` object.
      random_seed: an `int` as the random seed or None to use the default seed.

    """
    self._db = db
    self._random_state = random_seed or SEED
    self._energy_range = None
    self._splitted = False
    self._ids_of_training_examples = None
    self._ids_of_testing_examples = None
    self._max_occurs = None
    self._natoms_counter = None

  def __len__(self):
    """
    Return the total number of examples stored in this database.
    """
    return len(self._db)

  def __getitem__(self, index):
    """
    Get one or more structures.

    Args:
      index: an `int` or a list of `int` as the zero-based id(s) to select.

    Returns:
      sel: an `ase.Atoms` or a list of `ase.Atoms`.

    """
    if isinstance(index, int):
      if index < 1:
        raise ValueError("The minimum id is 1 but not 0!")
      objects = self._db.get_atoms('id={}'.format(index))

    elif isinstance(index, (list, tuple, np.ndarray, slice)):

      if isinstance(index, slice):
        step = index.step or 1
        indices = list(range(index.start, index.stop, step))
      else:
        indices = list(index)

      if min(indices) < 1:
        raise ValueError("The minimum id is 1 but not 0!")

      self._db.update(indices, selected=True)
      objects = [self._get_atoms(row) for row in self._db.select(selected=True)]
      self._db.update(indices, selected=False)

    else:
      raise ValueError('The index should be an int or a list of ints!')

    return objects

  @staticmethod
  def _get_atoms(row):
    """
    Convert the database row to `ase.Atoms` while keeping the info dict.

    Args:
      row: an `ase.db.row.AtomsRow`.

    Returns:
      atoms: an `ase.Atoms` object representing a structure.

    """
    atoms = row.toatoms()
    atoms.info.update(row.key_value_pairs)
    return atoms

  @property
  def num_examples(self):
    """
    Return the total number of examples stored in this database.
    """
    return len(self._db)

  @property
  def ids_of_training_examples(self):
    """
    Return the ids for all training examples.
    """
    if not self._ids_of_training_examples:
      self.split()
    return self._ids_of_training_examples

  @property
  def ids_of_testing_examples(self):
    """
    Return the ids for all testing examples.
    """
    if not self._ids_of_training_examples:
      self.split()
    return self._ids_of_testing_examples

  @property
  def energy_range(self):
    """
    Return the energy range of this database.
    """
    if not self._energy_range:
      self._go_through()
    return self._energy_range

  @property
  def max_occurs(self):
    """
    Return the maximum occur of each type of atom.
    """
    if not self._max_occurs:
      self._go_through()
    return self._max_occurs

  def get_atoms_size_distribution(self):
    """
    Return the distribution of the sizes of the `ase.Atoms` structures.
    """
    return self._natoms_counter

  def _go_through(self):
    """
    Go through all database records to determine the energy range, max occurs
    and the distribution of the sizes of the `ase.Atoms` structures.
    """
    counter = Counter()
    y_min = np.inf
    y_max = -np.inf
    max_occurs = {}
    for row in self._db.select('id<={}'.format(len(self))):
      y_min = min(row.energy, y_min)
      y_max = max(row.energy, y_max)
      for atom, n in Counter(row.symbols).items():
        max_occurs[atom] = max(max_occurs.get(atom, 0), n)
      counter[row.natoms] += 1
    self._max_occurs = max_occurs
    self._energy_range = (y_min, y_max)
    self._natoms_counter = counter

  def split(self, test_size=0.2, random_state=None):
    """
    Split this database into training set and testing set.

    Args:
      test_size: a `float` or `int`. If float, should be between 0.0 and 1.0 and
        represent the proportion of the dataset to include in the test split. If
        int, represents the absolute number of test samples.
      random_state: a `int` as the pseudo-random number generator state used for
        random sampling.

    """
    random_state = random_state or self._random_state
    ids_for_training, ids_for_testing = train_test_split(
      # Note: `id` starts from 1 not 0!
      list(range(1, len(self) + 1)),
      test_size=test_size,
      random_state=random_state
    )
    self._db.update(ids_for_training, for_training=True)
    self._db.update(ids_for_testing, for_training=False)
    self._random_state = random_state
    self._splitted = True
    self._ids_of_training_examples = ids_for_training
    self._ids_of_testing_examples = ids_for_testing

  def examples(self, for_training=True):
    """
    A set-like object providing a view on `ase.Atoms` of this database.

    Args:
      for_training: a `bool` indicating whether should we view on training
        examples or not.

    Yields:
      atoms: an `ase.Atoms` object.

    """
    if not self._splitted:
      self.split()
    for row in self._db.select(for_training=for_training):
      yield self._get_atoms(row)

  @classmethod
  def from_xyz(cls, xyzfile, num_examples, xyz_format='xyz', verbose=True,
               unit_to_ev=None, restart=False):
    """
    Initialize a `Database` from a xyz file.

    Args:
      xyzfile: a `str` as the file to parse.
      num_examples: a `int` as the maximum number of examples to parse.
      xyz_format: a `str` representing the format of the given xyz file.
      verbose: a `bool` indicating whether we should log the parsing progress.
      unit_to_ev: a `float` as the unit for converting energies to eV. Defaults
        to None so that default units will be used.
      restart: a `bool`. If True, the database will be re-built even if already
        existed.

    Returns:
      db: a `Database`.

    """
    return cls(xyz_to_database(xyzfile,
                               num_examples=num_examples,
                               xyz_format=xyz_format,
                               verbose=verbose,
                               unit_to_ev=unit_to_ev,
                               restart=restart))

  @classmethod
  def from_db(cls, filename):
    """
    Initialize a `Database` from a db.

    Args:
      filename: a `str` as the file to load.

    Returns:
      db: a `Database`.

    """
    with connect(filename) as db:
      return cls(db)
