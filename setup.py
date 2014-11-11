import glob, os

from setuptools import setup, find_packages

setup(
    name = 'metapub',
    version = '0.0.1',
    description = 'Pythonic interaction layers for eutils / Entrez / PubMed',
    url = 'https://bitbucket.org/nthmost/metapub',
    author = 'Naomi Most',
    maintainer = 'Naomi Most',
    author_email = 'naomi@nthmost.com',
    maintainer_email = 'naomi@nthmost.com',
    license = 'Apache 2.0',
    packages = find_packages(),
    install_requires = [
        'setuptools',
        'eutils',
        ],
    )