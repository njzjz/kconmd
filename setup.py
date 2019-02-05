"""Use 'pip install .' to install."""


from os import path

from setuptools import find_packages, setup

if __name__ == '__main__':
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'docs', 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

    tests_require = ['pytest-sugar', 'pytest-cov'],
    setup(name='kconmd',
          description='Molecular dynamics (MD) simulations supported by k-Bags Convolutional Neural Network (kcon).',
          keywords="molecular dynamics kcon",
          url='https://github.com/njzjz/kconmd',
          author='Jinzhe Zeng',
          author_email='jzzeng@stu.ecnu.edu.cn',
          packages=find_packages(),
          python_requires='~=3.6.0',
          install_requires=['numpy', 'scipy',
                            'matplotlib', 'scikit-learn', 'ase>=3.12',
                            'coloredlogs',
                            ],
          extras_require={
              "tf": ["tensorflow>=1.3"],
              "tf_gpu": ["tensorflow-gpu>=1.3"],
              'test': tests_require,
          },
          test_suite='kconmd.test',
          tests_require=tests_require,
          use_scm_version=True,
          setup_requires=['setuptools_scm', 'pytest-runner'],
          package_data={
              'kconmd': ['test/test.xyz', 'test/test.pb'],
          },
          long_description=long_description,
          long_description_content_type='text/markdown',
          classifiers=[
              "Natural Language :: English",
              "Operating System :: POSIX :: Linux",
              "Operating System :: Microsoft :: Windows",
              "Programming Language :: Python :: 3.6",
              "Topic :: Scientific/Engineering :: Chemistry",
              "Topic :: Software Development :: Libraries :: Python Modules",
              "Topic :: Software Development :: Version Control :: Git",
          ],
          zip_safe=True,
          )
