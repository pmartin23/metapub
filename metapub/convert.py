from __future__ import print_function, absolute_import

__doc__='mildly-experimental mashups of various services to get needed IDs.'

from urllib import urlretrieve

from .config import PMC_ID_CONVERSION_URI
from .pubmedfetcher import PubMedFetcher
from .crossref import CrossRef
from .text_mining import re_doi

crossref = None   #CrossRef()
pm_fetch = None   #PubMedFetcher()

def _start_engines():
    global crossref
    global pm_fetch
    if crossref and pm_fetch:
        return
    else:
        crossref = CrossRef()
        pm_fetch = PubMedFetcher()

def PubMedArticle2doi(pma, use_best_guess=False):
    _start_engines()
    results = crossref.query_from_PubMedArticle(pma)
    top_result = crossref.get_top_result(results, CR.last_params, use_best_guess)
    if top_result:
        return top_result['doi']
    else:
        return None

def pmid2doi(pmid, use_best_guess=False):
    # let MetaPubError pass back to the caller if pmid is not for realz..
    _start_engines()
    pma = fetch.article_by_pmid(pmid)
    return PubMedArticle2doi(pma, use_best_guess)

def doi2pmid(doi, use_best_guess=False):
    '''uses CrossRef and PubMed eutils to lookup a PMID given a known doi.
        Warning: does NO validation (use in combo with metapub.text_mining).

        If a PMID can be found, return it. Otherwise return None.
    '''
    # for PMA, skip the validation; some pubmed XML has weird partial strings for DOI.
    # We should allow people to search using these oddball strings.
    _start_engines()
    doi = doi.strip()
    try:
        pma = fetch.article_by_doi(doi):
        return pma.pmid
    except:
        pass

    results = crossref.query(doi)
    if results:
        top_result = crossref.get_top_result(results, CR.last_params, use_best_guess)
        return top_result[0]
    else:
        return None

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

