from __future__ import absolute_import

import logging

PKGNAME='metapub'

TMPDIR = '/tmp'

# email address submitted to eutils with requests (as required by their api).
DEFAULT_EMAIL=os.getenv('EUTILS_EMAIL', 'naomi.most@invitae.com')

PMC_ID_CONVERSION_URI = 'http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool='+PKGNAME+'&email='+DEFAULT_EMAIL+'&ids=%s'


#### keep eutils yammering down to a reasonable level.
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)
####

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
    datalog.addHandler(fh)
    return datalog

