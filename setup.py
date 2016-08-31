#from distutils.core import setup

import geomeppy
from setuptools import setup


setup(
    name='geomeppy',
    packages=['geomeppy',
              'devtools',
              'tests',
              ],
    version=geomeppy.__version__,
    description='Geometry editing for E+ idf files',
    author='Jamie Bull',
    author_email='jamie.bull@oco-carbon.com',
    url='https://github.com/jamiebull1/geomeppy',
    download_url='https://github.com/jamiebull1/geomeppy/tarball/v0.0.1',
    license='MIT License',
    keywords=['EnergyPlus', 
              'geometry',
              'building performance simulation',
              ],
    platforms='any',
    install_requires = [
        "eppy>=0.5.2",
        "numpy>=1.11.1",
        "six>=1.10.0",  # python2/3 compatibility
        "pyclipper>=1.0.2",  # geometry intersection
        "transforms3d>=0.3",  # geometry transformations
        "matplotlib>=1.5.1",  # simple geometry viewer
        ],
    classifiers = [
        'Programming Language :: Python :: 2',
#        'Programming Language :: Python :: 3',  # on hold until Eppy updates
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        ],
)
