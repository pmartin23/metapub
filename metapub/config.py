from __future__ import absolute_import

import os
import logging

PKGNAME = 'metapub'

# where to place XML (temporarily) when downloaded.
TMPDIR = '/tmp'

# default cache directory for SQLite cache engines
DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser('~'), '.cache')
if not os.access(DEFAULT_CACHE_DIR, os.W_OK):
    # default cache dir is not writeable
    # therefore ask the os for a temp directory
    import tempfile
    DEFAULT_CACHE_DIR = tempfile.gettempdir()

# email address submitted to eutils with requests (as required by their api).
DEFAULT_EMAIL = os.getenv('EUTILS_EMAIL', 'metapub@nthmost.com')


def get_process_log(filepath, loglevel=logging.INFO, name=PKGNAME+'-process'):
    log = logging.getLogger(name)
    log.setLevel(loglevel)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(filepath)
    fh.setFormatter(formatter)
    fh.setLevel(loglevel)
    log.addHandler(fh)
    return log


def get_data_log(filepath, name=PKGNAME+'-data'):
    datalog = logging.getLogger(name)
    datalog.setLevel(logging.DEBUG)
    datalog.propagate = False
    formatter = logging.Formatter('')
    fh = logging.FileHandler(filepath)
    fh.setFormatter(formatter)
    datalog.addHandler(fh)
    return datalog
