import os

from setuptools import setup


THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def read_rst(f):
    try:
        with open(os.path.join(THIS_DIR, f), 'r') as f_in:
            return f_in.read()
    except:
        return "GeomEppy"

setup(
    name='geomeppy',
    packages=[
        'geomeppy',
        'tests',
    ],
    version='0.4.3',
    description='Geometry editing for E+ idf files',
    long_description=read_rst('README.rst'),
    author='Jamie Bull',
    author_email='jamie.bull@oco-carbon.com',
    url='https://github.com/jamiebull1/geomeppy',
    download_url='https://github.com/jamiebull1/geomeppy/tarball/v0.4.3',
    license='MIT License',
    keywords=[
        'EnergyPlus',
        'geometry',
        'building performance simulation',
    ],
    platforms='any',
    install_requires=[
        'eppy==0.5.46',
        'pylru==1.0.9',  # caching
        'matplotlib',  # model viewer
        'numpy==1.13',
        'pyclipper==1.1.0',  # geometry intersection
        'shapely==1.6.2',  # geometry transformations
        'six==1.11.0',  # python2/3 compatibility
        'transforms3d==0.3.1',  # geometry transformations
        'pypoly2tri==0.0.3',  # triangulate polygons
    ],
    classifiers = [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
    ],
    extras_require={
        ':python_version>="3.4"': [
            'mypy==0.550',  # static type checking
        ],
        'testing': [
            'codecov',
            'flake8',
            'pytest-cov',
            'typing',
        ],
    },
)

