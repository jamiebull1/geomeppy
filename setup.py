
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import geomeppy

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.txt')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='geomeppy',
    version=geomeppy.__version__,
    url='https://github.com/jamiebull1/geomeppy',
    license='MIT License',
    author='Jamie Bull',
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    author_email='jamie.bull@oco-carbon.com',
    description='Geometry editing for E+ idf files, and E+ output files',
    long_description=long_description,# TODO set this up
    packages=['geomeppy',
              'devtools',
              'tests'
              ],
    include_package_data=True,
    platforms='any',
    test_suite='geomeppy.tests',# TODO make test_eppy
    install_requires = [
        "eppy>=0.5.2",
        "numpy>=1.2.1",
        "six>=1.10.0",  # python2/3 compatibility
        "pyclipper>=1.0.2",  # used for geometry intersection
        "transforms3d",  # used for geometry tranformations
        "matplotlib",  # for a simple geometry viewer
        ],
    classifiers = [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        ],
    extras_require={
        'testing': ['pytest'],
        'develop': ['matplotlib'] 
    }
)
