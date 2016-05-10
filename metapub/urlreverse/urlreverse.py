from __future__ import absolute_import, unicode_literals, print_function

import time
import logging

from ..pubmedcentral import get_pmid_for_otherid
from ..pubmedfetcher import PubMedFetcher
from ..crossref import CrossRef
from ..eutils_common import SQLiteCache, get_cache_path
from ..dx_doi import DxDOI
from ..convert import doi2pmid, pmid2doi, interpret_pmids_for_citation_results
from ..exceptions import MetaPubError, DxDOIError, BadDOI
from ..utils import hostname_of, remove_chars, asciify      #, kpick
from ..cache_utils import datetime_to_timestamp
from ..text_mining import find_doi_in_string
from ..config import DEFAULT_CACHE_DIR

from .hostname2jrnl import HOSTNAME_TO_JOURNAL_MAP
from .methods import re_pmcid, try_pmid_methods, try_doi_methods, try_vip_methods


FETCH = PubMedFetcher()
CRX = CrossRef()
DXDOI = DxDOI()

# UrlReverse cacheing engine globals
URLREVERSE_CACHE = None
CACHE_FILENAME = 'urlreverse-cache.db'


def get_article_info_from_url(url):
    """ Using regular expressions, attempt to determine the "format" of the submitted URL, and if 
    possible, extract useful information from the URL for article lookup by ID or citation.

    Possible results:
        'vip': volume-issue-page --> {'format': 'vip', 'volume': <V>, 'issue': <I>, 'first_page': <P>, 'jtitle': <jrnl>}
        'doi': has doi in the url --> {'format': 'doi', 'doi': <DOI>, 'method': <get_doi_function>}
        'pmid': has pmid in the url --> {'format': 'pmid', 'pmid': <PMID>}
        'pmcid': has PMC id in the url --> {'format': 'pmcid': 'pmcid': <PMCID>}

    If none of the available methods work to parse the URL, the result dictionary will be:
        {'format': 'unknown'}

    :param url:
    :return: result dictionary (see above)
    """
    # maybe the DOI is deducible from the URL:
    doidict = try_doi_methods(url)
    if doidict:
        doidict['format'] = 'doi'
        return doidict

    # maybe the pubmed ID is in the URL:
    pmid = try_pmid_methods(url)
    if pmid:
        outd = {'pmid': pmid, 'format': 'pmid'}
        return outd

    # maybe the PubmedCentral ID is in the URL:
    #if 'nih.gov' in url or 'europepmc.org' in url:
    match = re_pmcid.match(url)
    if match:
        outd = match.groupdict()
        outd['format'] = 'pmcid'
        return outd

    # maybe this is a volume-issue-page formatted link and we can look it up by citation or CrossRef:
    vipdict = try_vip_methods(url)
    if vipdict:
        vipdict['format'] = 'vip'
        return vipdict

    return {'format': 'unknown'}


def get_journal_name_from_url(url):
    if not url.lower().startswith('http'):
        url = 'http://' + url

    hostname = hostname_of(url)

    if hostname in HOSTNAME_TO_JOURNAL_MAP.keys():
        return HOSTNAME_TO_JOURNAL_MAP[hostname]
    else:
        return None


def _get_urlreverse_cache(cachedir=DEFAULT_CACHE_DIR):
    global URLREVERSE_CACHE
    if not URLREVERSE_CACHE:
        _cache_path = get_cache_path(cachedir, CACHE_FILENAME)
        URLREVERSE_CACHE = SQLiteCache(_cache_path)
    return URLREVERSE_CACHE


class UrlReverse(object):

    def __init__(self, url, verify=True, skip_cache=False, **kwargs):
        if not url.lower().startswith('http'):
            url = 'http://' + url

        self.url = url
        self.path = []
        self.verify = verify

        # TODO: UrlReverse.supplied_info 
        # self.supplied_info = {'title': kwargs.get('title', None),
        #                      'jtitle': kpick(kwargs, ['jtitle', 'journal', 'TA'], None),
        #                      'aulast': kpick(kwargs, ['author1_last_fm', 'aulast'], None),
        #                      'volume': kwargs.get('volume', None),
        #                      'issue': kwargs.get('issue', None),
        #                      'doi': kwargs.get('doi', None),
        #                      }

        self.pmid = None
        self.doi = None
        self.info = None

        cachedir = kwargs.get('cachedir', DEFAULT_CACHE_DIR)
        self._cache = None if cachedir is None else _get_urlreverse_cache(cachedir)

        self._log = logging.getLogger('metapub.UrlReverse')
        if kwargs.get('debug', False):
            self._log.setLevel(logging.DEBUG)
        else:
            self._log.setLevel(logging.INFO)

        if self._cache:
            self._load_from_cache()
        else:
            self._urlreverse()

    def _urlreverse(self, verify=True):
        self.info = get_article_info_from_url(self.url)
        self.format = self.info['format']

        if self.format == 'pmid':
            self.pmid = self.info['pmid']
            #self.doi = pmid2doi(self.pmid)
            if self.pmid:
                self.reason += 'FOUND result from inferred PMID in URL;'

        elif self.format == 'doi':
            self.doi = self.info['doi']
            self.pmid = doi2pmid(self.doi)
            if self.pmid:
                self.reason += 'FOUND via inferred doi + doi2pmid;'
            else:
                self.reason += 'NO result from inferred doi + doi2pmid;'

        elif self.format == 'vip':
            try:
                self._try_citation_methods()
            except MetaPubError as error:
                self.pmid = None
                self.reason += 'NO result from VIP info + citation methods;'

        elif self.format == 'pmcid':
            self.pmid = get_pmid_for_otherid(self.info['pmcid'])
            self.doi = doi2pmid(self.pmid)
            if self.pmid:
                self.reason += 'FOUND result from PMCID -> PMID lookup;'

        if self.pmid and self.pmid.startswith('NOT_FOUND'):
            self.reason += 'NO result: PMID citation lookup resulted in "%s";' % self.pmid
            self.pmid = None

        if self.doi and not self.pmid:
            self._try_backup_doi2pmid_methods()

        if verify and self.doi:
            try:
                urlres = DXDOI.resolve(self.doi)
                self.reason += 'VERIFY dx.doi.org: %s;' % urlres
            except (DxDOIError, BadDOI) as error:
                self.doi = None
                self.reason += 'VERIFY dx.doi.org: problem with DOI: %r;' % error

        # Finally: ADMIT DEFEAT
        if not self.doi and not self.pmid:
            self.reason += 'NO result -- END OF LINE.'

    def _store_cache(self):
        """ Store this object in cache by explicitly choosing variables to store as
        values, using self.url as the cache key.

        A time.time() timestamp will be added to the value dictionary when stored.

        There is no return from this function. Exceptions from the SQLiteCache 
        object may be raised.
        """
        cache_value = self.to_dict()
        cache_value['timestamp'] = time.time()
        self._cache[self._make_cache_key(self.url)] = cache_value

    def _load_from_cache(self):
        cache_result = self._query_cache(self.url)

        if cache_result:
            self.pmid = cache_result['pmid']
            self.doi = cache_result['doi']
            self.reason = cache_result['reason']
            self.info = cache_result['info']
            self.verify = cache_result['verify']
            # TODO             self.supplied_info = cache_result['supplied_info']

        else:
            self._urlreverse()
            self._store_cache()

    def _make_cache_key(self, url):
        """ Returns url normalized via str() function for hash lookup / store. """
        return str(url)

    def _query_cache(self, cache_key, expiry_date=None):
        """ Return results of a lookup from the cache, if available.
        Return None if not available.

        Cache results are stored with a time.time() timestamp.

        When expiry_date is supplied, results from the cache past their
        sell-by date will be expunged from the cache and return will be None.

        expiry_date can be either a python datetime or a timestamp. 

        :param: cache_key: (required)
        :param: expiry_date (optional, default None)
        :return: (dict) result of cache lookup
        :rtype: dict or None
        """

        if hasattr(expiry_date, 'strftime'):
            # convert to timestamp
            sellby = datetime_to_timestamp(expiry_date)
        else:
            # make sure sellby is a number, not None
            sellby = expiry_date if expiry_date else 0

        if self._cache:
            cache_key = self._make_cache_key(cache_key)
            try:
                res = self._cache[cache_key]
                timestamp = res['timestamp']
                if timestamp < sellby:
                    self._log.debug('Cache: expunging result for %s (%i)', cache_key, timestamp)
                else:
                    self._log.debug('Cache: returning result for %s (%i)', cache_key, timestamp)
                return res

            except KeyError:
                self._log.debug('Cache: no result for key %s', cache_key)
                return None
        else:
            self._log.debug('Cache disabled (self._cache is None)')
            return None

    def _try_citation_methods(self):
        # 1) try pubmed citation match.
        pmids = FETCH.pmids_for_citation(**self.info)
        pmid = interpret_pmids_for_citation_results(pmids)
        if pmid and pmid != 'AMBIGUOUS':
            self.pmid = pmid
            self.doi = pmid2doi(pmid)
            self.path('FOUND via PubmedFetcher.pmids_for_citation;')
            return

        # 2) try CrossRef -- most effective when title available, but may work without it.
        # TODO: UrlReverse.supplied_info 
        # title = self.supplied_info['title'] or ''
        results = CRX.query('', params=self.info)
        if results:
            top_result = CRX.get_top_result(results, CRX.last_params)

            # we may have disqualified all the results at this point as being irrelevant, so we have to test here.
            if top_result:
                self.doi = find_doi_in_string(top_result['doi'])
                pmids = FETCH.pmids_for_citation(**top_result['slugs'])
                pmid = interpret_pmids_for_citation_results(pmids)
                if pmid and pmid != 'AMBIGUOUS':
                    self.pmid = pmid

    def _try_backup_doi2pmid_methods(self):
        """ Uses CrossRef and Pubmed Advanced Query combinations to try to get an 
        unambiguous PMID result. Mutates self.pmid (if found unambigously) and self.path
        (appending strings documenting the process by which PMID was(n't) acquired).
        """

        # All hinges on whether CrossRef can give us a good result. If not, fail out early.
        results = CRX.query(self.doi)
        coins = None

        if results:
            top_result = CRX.get_top_result(results, CRX.last_params)
            if top_result:
                coins = top_result['slugs'].copy()

        if not coins:
            return

        # normalize start page ('spage') to None in case of "no" or "n/a"
        if coins.get('spage', 'no').lower() in ['no', 'n%2Fa']:
            coins['spage'] = None

        # bowlderize the title (remove urlencoded chars and punctuation)
        title = asciify(remove_chars(coins['atitle'], urldecode=True).strip())

        pmids = []

        # try this first. If we get one single result, that should be it.
        pmids = FETCH.pmids_for_query(title)
        if len(pmids) == 1:
            self.pmid = pmids[0]
            self.path.append('FOUND via Pubmed Advanced Query;')
            return

        elif len(pmids) == 0:
            self.pmid = None
            self.path.append('NO results for title "%s" in Pubmed, attempting coordinate match;' % title)
            title = ''

        elif len(pmids) > 1 and len(title.split(' ')) < 3:
            # title could be something like "Abstract" or "Pituitary" or "Endocrinology Yearbook" -- too vague.
            self.path.append('Title "%s" TOO VAGUE, attempting coordinate match;' % title)
            title = ''

        # we have ambiguous results -- let's try to narrow the field based on whether we have a viable
        # title or not.

        # Two paths diverged in a wood, and I...

        if title=='':
            # strict coordinates
            params = {'VI': coins.get('volume', None),
                      'IP': coins.get('issue', None),
                      'AU': coins.get('aulast', None),
                      'PG': coins.get('spage', None),
                      'DP': coins.get('year', None),
                     }
            pmids = FETCH.pmids_for_query(coins['jtitle'], **params)

        else:
            if coins.get('volume') and coins.get('issue'):
                self.path.append('AMBIGUOUS results for title "%s", trying with volume/issue;')
                pmids = FETCH.pmids_for_query(title, VI=coins['volume'], IP=coins['issue'])
            elif coins.get('volume') and coins.get('aulast'):
                self.path.append('AMBIGUOUS results for title "%s", trying with aulast;')
                pmids = FETCH.pmids_for_query(title, AU=coins['aulast'])
            elif coins.get('spage') and coins.get('aulast'):
                self.path.append('AMBIGOUS results for title "%s", trying with first_page;')
                pmids = FETCH.pmids_for_query(title, PG=coins['spage'])     #, AU=coins['aulast'])
            elif coins.get('volume'):
                self.path.append('AMBIGOUS results for title "%s", trying with volume;')
                pmids = FETCH.pmids_for_query(title, VI=coins['volume'])

        # that should have narrowed the field substantially. we should give up if it's still ambiguous.
        if len(pmids) == 1:
            self.pmid = pmids[0]
            self.path.append('FOUND via Pubmed Advanced Query;')
        elif len(pmids) == 0:
            self.pmid = None
            self.path.append('NO results from pubmed advanced query.  (Data from CrossRef was: %r);' % (coins))
        else:
            self.pmid = None
            self.path('AMBIGUOUS results from pubmed advanced query (%i possibilities).  (Data from CrossRef was: %r)' % (len(pmids), coins))

    def to_dict(self):
        """ Returns a dictionary containing all public object attributes (i.e. not starting with an underscore). """
        outd = {}
        for key in self.__dict__:
            if not key.startswith('_'):
                outd[key] = self.__dict__[key]
        return outd

