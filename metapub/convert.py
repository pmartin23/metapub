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
    '''starting with a PubMedArticle object, use CrossRef to find a DOI for given article.

        :param: pma (PubMedArticle object)
        :param: use_best_guess (bool) [default: False]
        :param: min_score (float) [default: 2.0]
    '''

    _start_engines()
    results = crossref.query_from_PubMedArticle(pma)
    top_result = crossref.get_top_result(results, crossref.last_params, use_best_guess, min_score=min_score)
    if top_result:
        return top_result['doi']
    else:
        return None

def PubMedArticle2doi_with_score(pma, use_best_guess=False, min_score=2.0):
    '''Starting with a PubMedArticle object, use CrossRef to find a DOI for given article.

        Returns a tuple containing the DOI and the score CrossRef returned for the
        lookup.  If there was no good result above the min_score threshold, the tuple 
        will contain (None, 0.0).

        :param: pma (PubMedArticle object)
        :param: use_best_guess (bool) [default: False]
        :param: min_score (float) [default: 2.0]
        :return: (doi, score) (string, float) or (None, 0.0)
    '''

    _start_engines()
    results = crossref.query_from_PubMedArticle(pma)
    top_result = crossref.get_top_result(results, crossref.last_params, use_best_guess, min_score=min_score)
    if top_result:
        return (top_result['doi'], top_result['score'])
    else:
        return (None, 0.0)

def pmid2doi(pmid, use_best_guess=False, min_score=2.0):
    '''starting with a pubmed ID, lookup article in pubmed. If DOI found in PubMedArticle object,
        return it.  Otherwise, use CrossRef to find the DOI for given article.

        :param: pmid (string or int)
        :param: use_best_guess (bool) [default: False]
        :param: min_score (float) [default: 2.0]
    '''
    # let MetaPubError pass back to the caller if pmid is not for realz..
    _start_engines()
    pma = pm_fetch.article_by_pmid(pmid)
    if pma.doi:
        return pma.doi
    return PubMedArticle2doi(pma, use_best_guess, min_score=2.0)

def pmid2doi_with_score(pmid, use_best_guess=False, min_score=2.0):
    '''Starting with a pubmed ID, lookup article in pubmed. 
        
        If DOI found in PubMedArticle object, that doi and 10.0 for the doi_score, 
        i.e. the tuple (doi, 10.0).
    
        Otherwise, use CrossRef to find the DOI for given article and return (doi, crossref_doi_score).

        :param: pmid (string or int)
        :param: use_best_guess (bool) [default: False]
        :param: min_score (float) [default: 2.0]
        :return: tuple (doi, doi_score)
    '''
    _start_engines()
    pma = pm_fetch.article_by_pmid(pmid)
    if pma.doi:
        return (pma.doi, 10.0)
    return PubMedArticle2doi_with_score(pma, use_best_guess, min_score=2.0)

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
        pma = pm_fetch.article_by_doi(doi)
        return pma.pmid
    except:
        pass

    results = crossref.query(doi)
    if results:
        top_result = crossref.get_top_result(results, crossref.last_params, use_best_guess, min_score=min_score)
        pmids = pm_fetch.pmids_for_citation(**top_result['slugs'])
        if len(pmids) == 1:
            if pmids[0] == 'NOT_FOUND':
                return None
            return str(pmids[0])
        elif len(pmids) == 0:
            return None
        else:
            return 'AMBIGUOUS'
    else:
        return None

