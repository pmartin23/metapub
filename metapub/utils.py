from __future__ import absolute_import

import os
from urllib import urlretrieve
from lxml import etree

from .config import PKGNAME
from .exceptions import MetaPubError

TMPDIR = '/tmp'
EMAIL = 'naomi@nthmost.com'
ID_CONVERSION_URI = 'http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool='+PKGNAME+'&email='+EMAIL+'&ids=%s'

def get_tmp_xml_path(someid):
    someid = someid.replace('/', '__')
    return os.path.join(TMPDIR, '%s.xml' % someid)

def _id_conversion_api(input_id):
    xmlfile = urlretrieve(ID_CONVERSION_URI % input_id, get_tmp_xml_path(input_id))
    root = etree.parse(xmlfile[0])
    root.find('record')
    record = root.find('record')
    return record

def get_pmid_for_otherid(otherid):
    # this returns "None" if there is no 'pmid' item.
    record = _id_conversion_api(otherid)
    return record.get('pmid')

# singleton class used by the fetchers.
class Borg:
  _shared_state = {}
  def __init__(self):
    self.__dict__ = self._shared_state

# PMID: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=23193287
# PMCID: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=PMC3531190
# Manuscript ID: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=NIHMS311352
# DOI: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=10.1093/nar/gks1195
# Versioned identifier: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=PMC2808187.1

