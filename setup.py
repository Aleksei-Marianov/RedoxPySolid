from setuptools import setup, find_packages, Extension
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    LONG_DESCRIPTION = "\n" + fh.read()

VERSION = '0.0.4'
DESCRIPTION = 'Model of heterogeneous electrochemistry'

setup(
    name="RedoxPySolid",
    version=VERSION,
    author="Aleksei Marianov",
    author_email="marjanov.alexei@gmail.com",
    long_description_content_type="text/markdown",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=['RedoxPySolid'],
    install_requires=['numpy', 'scipy'],
    keywords=['python', 'electrochemistry', 'voltammetry', 'heterogeneous catalysis'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: C++",
        "Programming Language :: Python"
    ],
    include_package_data=True
)