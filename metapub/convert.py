from __future__ import print_function, absolute_import, unicode_literals

__doc__='mildly-experimental mashups of various services to get needed IDs.'

from .pubmedfetcher import PubMedFetcher
from .crossref import CrossRef
from .exceptions import *

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


def _protected_crossref_query(**kwargs):
    pma = kwargs.get('pma', None)
    pmid = kwargs.get('pmid', None)
    use_best_guess = kwargs.get('use_best_guess', False)
    min_score = kwargs.get('min_score', 2.0)
    if pmid and not pma:
        pma = pm_fetch.article_by_pmid(pmid)
    try:
        results = crossref.query_from_PubMedArticle(pma)
    except CrossRefConnectionError:
        return None
    return crossref.get_top_result(results, crossref.last_params, use_best_guess, min_score=min_score)


def interpret_pmids_for_citation_results(pmids):
    if len(pmids) == 1:
        if pmids[0] == 'NOT_FOUND':
            return None
        elif pmids[0].startswith('AMBIGUOUS'):
            return 'AMBIGUOUS'
        return str(pmids[0])
    elif len(pmids) == 0:
        return None
    else:
        return 'AMBIGUOUS'


def PubMedArticle2doi(pma, use_best_guess=False, min_score=2.0):
    '''starting with a PubMedArticle object, use CrossRef to find a DOI for given article.

    Args:
        pma (PubMedArticle)
        use_best_guess (bool): default=False
        min_score (float): default=2.0

    Returns:
        doi (str) or None
    '''
    _start_engines()
    result = _protected_crossref_query(pma=pma, use_best_guess=use_best_guess, min_score=min_score)
    if result:
        return result['doi']
    else:
        return None


def PubMedArticle2doi_with_score(pma, use_best_guess=False, min_score=2.0):
    '''Starting with a PubMedArticle object, use CrossRef to find a DOI for given article.

    Returns a tuple containing the DOI and the score CrossRef returned for the
    lookup.  If there was no good result above the min_score threshold, the tuple 
    will contain (None, 0.0).

    Args:
        pma (PubMedArticle)
        use_best_guess (bool): default=False
        min_score (float): default=2.0
    
    Returns:
        tuple (doi string, score) or (None, 0.0)
    '''

    _start_engines()
    result = _protected_crossref_query(pma=pma, use_best_guess=use_best_guess, min_score=min_score)
    if result:
        return (result['doi'], result['score'])
    else:
        return (None, 0.0)


def pmid2doi(pmid, use_best_guess=False, min_score=2.0):
    '''starting with a pubmed ID, lookup article in pubmed. If DOI found in PubMedArticle object,
        return it.  Otherwise, use CrossRef to find the DOI for given article.

    Args:
        pmid (str or int)
        use_best_guess (bool): default=False
        min_score (float): minimum score to accept from CrossRef for given doi. default=2.0

    Returns:
        doi (str) or None

    Raises:
        InvalidPMID (if pmid is invalid)
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

    Args:
        pmid (str or int)
        use_best_guess (bool): default=False
        min_score (float): minimum score to accept from CrossRef for given doi. default=2.0

    Returns:
        tuple (doi, score) or (None, 0.0)

    Raises:
        InvalidPMID (if pmid is invalid)
    '''
    _start_engines()
    pma = pm_fetch.article_by_pmid(pmid)
    if pma.doi:
        return (pma.doi, 10.0)
    return PubMedArticle2doi_with_score(pma, use_best_guess, min_score=2.0)


def doi2pmid(doi, use_best_guess=False, min_score=2.0, debug=False):
    '''uses CrossRef and PubMed eutils to lookup a PMID given a known doi.

    Warning: NO validation of input DOI performed here. Use
             metapub.text_mining.find_doi_in_string beforehand if needed.

    If a PMID can be found, return it. Otherwise return None.

    In very rare cases, use of the CrossRef->pubmed citation method used
    here may result in more than one pubmed ID. In this case, this function
    will return instead the word 'AMBIGUOUS'.

    Args:
        pmid (str or int)
        use_best_guess (bool): default=False
        min_score (float): minimum score to accept from CrossRef for given doi. default=2.0

    Returns:
        pmid (str) if found; 'AMBIGUOUS' if citation count > 1; None if no results.
    '''
    # for PMA, skip the validation; some pubmed XML has weird partial strings for DOI.
    # We should allow people to search using these oddball strings.
    _start_engines()
    doi = doi.strip()
    try:
        pma = pm_fetch.article_by_doi(doi)
        if debug:
            print('Found PubMedArticle via eutils fetch')
        return pma.pmid
    except:
        pass

    # Try doing a DOI lookup right in an advanced query string. Sometimes works and has
    # benefit of being a cached query so it is quick to do again, should we need.
    pmids = pm_fetch.pmids_for_query(doi)
    if len(pmids) == 1:
        # we need to cross-check; pubmed sometimes screws us over by giving us an article
        # with a SIMILAR doi. *facepalm*
        pma = pm_fetch.article_by_pmid(pmids[0])
        if pma.doi == doi:
            if debug:
                print('Found PMID via PubMed advanced query for DOI')
            return pma.pmid
        if debug:
            print('PubMed advanced query gave us a wonky result:')
            print('     Search: %s' % doi)
            print('     Return: %s' % pma.doi)

    # Look up the DOI in CrossRef, then feed results to pubmed citation query tool.
    try:
        results = crossref.query(doi)
    except CrossRefConnectionError:
        return None

    if results:
        top_result = crossref.get_top_result(results, crossref.last_params, use_best_guess, min_score=min_score)
        pmids = pm_fetch.pmids_for_citation(debug=debug, **top_result['slugs'])
        if debug:
            print('Submitted slugs: %r' % top_result['slugs'])
            #print('CrossRef results: %r' % top_result)
            print('PMIDs: %r' % pmids)
        return interpret_pmids_for_citation_results(pmids)
    else:
        return None

