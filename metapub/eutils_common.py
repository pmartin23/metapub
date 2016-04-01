from __future__ import absolute_import, unicode_literals

import os, logging

# this import is used by other modules (but not in this one):
from eutils.sqlitecache import SQLiteCache

from .config import DEFAULT_EMAIL, PKGNAME
from .exceptions import MetaPubError

EUTILS_DEFAULT_CACHEDIR = os.path.expanduser('~/.cache')

# == suppress the chatter of eutils and requests == #
logging.getLogger('eutils').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.ERROR)
# ==


def get_eutils_client(cache_path, email=DEFAULT_EMAIL):
    """
    :param cache_path: valid filesystem path to SQLite cache file
    :param email: (optional) email address to submit with cache queries
    :return: eutils QueryService client object
    """
    import eutils.client as ec
    if cache_path is None:
        return ec.QueryService(tool=PKGNAME, email=email, cache_path=None)
    return ec.QueryService(tool=PKGNAME, email=email, cache_path=cache_path)


def get_cache_path(cachedir, filename='metapub-cache.db'):
    """ checks if cachedir exists; if not, tries to create it;
    raises MetaPubError if it can't be created.

        if cachedir is None, returns None.
        if cachedir is 'default', returns the eutils default of '~/.cache/<filename>'

        Supports expansion of user directory shortcut '~' to full path.

    :param cachedir: directory to store
    :param filename: name of cache file
    :return: path to SQLite DB file
    :raises MetaPubError
    """
    if cachedir is None:
        return None

    elif cachedir == 'default':
        cachedir = EUTILS_DEFAULT_CACHEDIR

    elif cachedir.find('~') > -1:
        cachedir = os.path.expanduser(cachedir)

    if _require_dir(cachedir):
        return os.path.join(cachedir, filename)
    else:
        raise MetaPubError('Could not create cache directory location %s' % cachedir)


def _require_dir(targetdir):
    if os.path.exists(targetdir):
        return True

    try:
        os.makedirs(targetdir)
        return True
    except OSError:
        return False
