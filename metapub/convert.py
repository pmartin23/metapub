from __future__ import print_function, absolute_import

__doc__='mildly-experimental mashups of various services to get needed IDs.'

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

def PubMedArticle2doi(pma, use_best_guess=False, min_score=2.0):
    _start_engines()
    results = crossref.query_from_PubMedArticle(pma)
    top_result = crossref.get_top_result(results, crossref.last_params, use_best_guess, min_score=min_score)
    if top_result:
        return top_result['doi']
    else:
        return None

def pmid2doi(pmid, use_best_guess=False, min_score=2.0):
    # let MetaPubError pass back to the caller if pmid is not for realz..
    _start_engines()
    pma = fetch.article_by_pmid(pmid)
    return PubMedArticle2doi(pma, use_best_guess, min_score=2.0)

def doi2pmid(doi, use_best_guess=False, min_score=2.0):
    '''uses CrossRef and PubMed eutils to lookup a PMID given a known doi.
        Warning: does NO validation (use in combo with metapub.text_mining).

        If a PMID can be found, return it. Otherwise return None.
    '''
    # for PMA, skip the validation; some pubmed XML has weird partial strings for DOI.
    # We should allow people to search using these oddball strings.
    _start_engines()
    doi = doi.strip()
    try:
        pma = fetch.article_by_doi(doi)
        return pma.pmid
    except:
        pass

    results = crossref.query(doi)
    if results:
        top_result = crossref.get_top_result(results, crossref.last_params, use_best_guess, min_score=min_score)
        return pm_fetch.pmids_for_citation(**top_result['slugs'])
    else:
        return None

