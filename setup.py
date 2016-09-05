from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()
    
setup(
    name='geomeppy',
    packages=['geomeppy',
              'tests',
              ],
    version='0.2.4',
    description='Geometry editing for E+ idf files',
    long_description=read_md('README.md'),
    author='Jamie Bull',
    author_email='jamie.bull@oco-carbon.com',
    url='https://github.com/jamiebull1/geomeppy',
    download_url='https://github.com/jamiebull1/geomeppy/tarball/v0.2.4',
    license='MIT License',
    keywords=['EnergyPlus', 
              'geometry',
              'building performance simulation',
              ],
    platforms='any',
    install_requires = [
        "eppy==0.5.31",
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
