# kconMD (k-Bags Convolutional Neural Network Molecular Dynamics)
[![python3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://badge.fury.io/py/kconMD)[![pypi](https://badge.fury.io/py/kconMD.svg)](https://badge.fury.io/py/kconMD)

Molecular Dynamics (MD) simulations supported by [k-Bags Convolutional Neural Network (kCON)](https://github.com/njzjz/kcon).

**Author**: Jinzhe Zeng

Email: jzzeng@stu.ecnu.edu.cn

[Research Group](http://computchem.cn)

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
pip install kconMD
```

### Build from source
```sh
$ git clone https://github.com/njzjz/kconMD.git
$ cd kconMD/
$ python3 setup.py install
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
