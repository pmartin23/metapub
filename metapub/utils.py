from __future__ import absolute_import

import os
from urllib import urlretrieve
from lxml import etree

from .config import PKGNAME
from .exceptions import MetaPubError

TMPDIR = '/tmp'
DEFAULT_EMAIL = 'naomi@nthmost.com'
ID_CONVERSION_URI = 'http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool='+PKGNAME+'&email='+DEFAULT_EMAIL+'&ids=%s'

def pick_from_kwargs(args, options, default=None):
    for opt in options:
        if args.get(opt, None):
            return args[opt]
    return default

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
    '''use the PMC ID conversion API to attempt to convert either PMCID or DOI to a PMID.
        returns PMID if successful, or None if there is no 'pmid' item in the return.

        :param: otherid (string)
        :rtype: string
    '''
    record = _id_conversion_api(otherid)
    return record.get('pmid')

def asciify(inp):
    '''nuke all the unicode from orbit. it's the only way to be sure.'''
    if inp:
        return inp.encode('ascii', 'ignore')
    else:
        return ''

def parameterize(inp, sep='+'):
    '''make strings suitable for submission to GET-based query service'''
    return asciify(inp).replace(' ', sep)

def deparameterize(inp, sep='+'):
    '''undo parameterization in string. replace separators (sep) with spaces.'''
    return inp.replace(sep, ' ')

def remove_html_markup(s):
    '''remove html and xml tags from text. preserves HTML entities like &amp;'''
    tag = False
    quote = False
    out = ""

    for c in s:
            if c == '<' and not quote:
                tag = True
            elif c == '>' and not quote:
                tag = False
            elif (c == '"' or c == "'") and tag:
                quote = not quote
            elif not tag:
                out = out + c
    return out



# PMID: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=23193287
# PMCID: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=PMC3531190
# Manuscript ID: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=NIHMS311352
# DOI: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=10.1093/nar/gks1195
# Versioned identifier: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=PMC2808187.1

