from setuptools import setup
setup(name='kconMD',
      version='1.0.0',
      description='Molecular dynamics (MD) simulations supported by k-Bags Convolutional Neural Network (kcon).',
      keywords="molecular dynamics kcon",
      url='https://github.com/njzjz/kconMD',
      author='Jinzhe Zeng',
      author_email='njzjz@qq.com',
      packages=['kconMD','kconMD/force','kconMD/kcnn'],
      install_requires=['numpy','scipy','matplotlib','scikit-learn','ase>=3.12'],
      extras_require={
        "tf": ["tensorflow>=1.3"],
        "tf_gpu": ["tensorflow-gpu>=1.3"],
      }
    )

