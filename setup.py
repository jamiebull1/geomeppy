import os

from setuptools import setup

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(THIS_DIR, "requirements.in")) as f:
    install_requires = [line for line in f if line and line[0] not in "#-"]

with open(os.path.join(THIS_DIR, "test-requirements.in")) as f:
    test_requires = [line for line in f if line and line[0] not in "#-"]

with open(os.path.join(THIS_DIR, "README.md")) as f:
    long_description = f.read()

setup(
    name="geomeppy",
    packages=["geomeppy", "geomeppy.geom", "geomeppy.io", "tests"],
    version="0.12.1",
    description="Geometry editing for E+ idf files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jamie Bull",
    author_email="jamie.bull@gmail.com",
    url="https://github.com/jamiebull1/geomeppy",
    download_url="https://github.com/jamiebull1/geomeppy/tarball/v0.12.1",
    license="MIT License",
    keywords=["EnergyPlus", "geometry", "building performance simulation"],
    platforms="any",
    install_requires=install_requires,
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    extras_require={
        "lint": ["mypy", "black"],
        "testing": test_requires,
    },
    include_package_data=True,
)
