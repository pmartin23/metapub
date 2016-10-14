import glob, os

from setuptools import setup, find_packages

setup(
    name = 'metapub',
    version = '0.4.3.5',
    description = 'Pubmed / NCBI / eutils interaction library, handling the metadata of pubmed papers.',
    url = 'https://bitbucket.org/metapub/metapub',
    author = 'Naomi Most',
    maintainer = 'Naomi Most',
    author_email = 'naomi@nthmost.com',
    maintainer_email = 'naomi@nthmost.com',
    license = 'Apache 2.0',
    packages = find_packages(),
    install_requires = [
        'setuptools',
        'lxml',
        'requests',
        'eutils',
        'tabulate',
        'cssselect',
        'unidecode',
        'six',
        'tox',
        ],
    )
