# kconMD (k-Bags Convolutional Neural Network Molecular Dynamics)

[![python version](https://img.shields.io/pypi/pyversions/kconmd.svg?logo=python&logoColor=white)](https://pypi.org/project/kconmd)
[![PyPI](https://img.shields.io/pypi/v/kconmd.svg)](https://pypi.org/project/kconmd)
[![Build Status](https://travis-ci.com/njzjz/kconmd.svg?branch=master)](https://travis-ci.com/njzjz/kconmd)
[![Coverage Status](https://coveralls.io/repos/github/njzjz/kconmd/badge.svg?branch=master)](https://coveralls.io/github/njzjz/kconmd?branch=master)
[![codecov](https://codecov.io/gh/njzjz/kconmd/branch/master/graph/badge.svg)](https://codecov.io/gh/njzjz/kconmd)

Molecular Dynamics (MD) simulations supported by [k-Bags Convolutional Neural Network (kCON)](https://github.com/njzjz/kcon).

**Author**: Jinzhe Zeng

Email: jzzeng@stu.ecnu.edu.cn

[![Research Group](https://img.shields.io/website-up-down-green-red/http/computchem.cn.svg?label=Research%20Group)](http://computechem.cn)

## Acknowledgement

Many thanks to [Xin Chen](https://github.com/Bismarrck) for his help and development of [kCON](https://github.com/Bismarrck/kcon).

## Requirements

* [numpy](https://github.com/numpy/numpy)
* [scipy](https://github.com/scipy/scipy)
* [matplotlib](https://github.com/matplotlib/matplotlib)
* [scikit-learn](https://github.com/scikit-learn/scikit-learn)
* [ASE](https://wiki.fysik.dtu.dk/ase/)
* [TensorFlow](https://github.com/tensorflow/tensorflow)

## Installation

### With pip

```sh
pip install kconmd
```

### Build from source

```sh
$ git clone https://github.com/njzjz/kconmd
$ cd kconmd/
$ pip install .
```

## Examples

### Simple example

See [examples/example.py](examples/example.py).

### Client–server model

See [examples/server.py](examples/server.py) and [examples/client.py](examples/client.py).

### Run MD with LAMMPS

See [njzjz/Pyforce](https://github.com/njzjz/Pyforce) repository and install Pyforce module. Then rename [examples/client.py](examples/client.py) as `force.py` and put it where you run LAMMPS. Add a line in the LAMMPS input file:
```
fix 1 all pyforce C H O
```
