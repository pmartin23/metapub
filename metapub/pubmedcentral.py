from __future__ import absolute_import

from urllib import urlretrieve

from .config import PKGNAME, DEFAULT_EMAIL, TMPDIR

PMC_ID_CONVERSION_URI = 'http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool='+PKGNAME+'&email='+DEFAULT_EMAIL+'&ids=%s'

__doc__='''An assortment of functions providing access to various web APIs.

    The pubmedcentral.* functions abstract the submission of one of the following
    acceptable IDs to the Pubmed Central ID Conversion API as a lookup to
    get another ID mapping to the same pubmed article:

        * doi       Digital Object Identifier
        * pmid      Pubmed ID
        * pmcid     Pubmed Central ID (includes Versioned Identifier)

    Available functions:

        get_pmid_for_otherid(string)
    
        get_doi_for_otherid(string)

        get_pmcid_for_otherid(string)
'''

def get_tmp_xml_path(someid):
    someid = someid.replace('/', '__')
    return os.path.join(TMPDIR, '%s.xml' % someid)

def _pmc_id_conversion_api(input_id):
    xmlfile = urlretrieve(PMC_ID_CONVERSION_URI % input_id, get_tmp_xml_path(input_id))
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
    record = _pmc_id_conversion_api(otherid)
    return record.get('pmid')

def get_pmcid_for_otherid(otherid):
    record = _pmc_id_conversion_api(otherid)
    return record.get('pmcid')

def get_doi_for_otherid(otherid):
    record = _pmc_id_conversion_api(otherid)
    return record.get('doi')


# PMID: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=23193287
# PMCID: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=PMC3531190
# Manuscript ID: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=NIHMS311352
# DOI: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=10.1093/nar/gks1195
# Versioned identifier: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=PMC2808187.1


