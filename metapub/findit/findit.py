from __future__ import absolute_import, print_function

__doc__='''find_it: provides FindIt object, providing a tidy object layer
            into the get_pdf_from_pma function.

        The get_pdf_from_pma function selects possible PDF links for the 
        given article represented in a PubMedArticle object.

        The FindIt class allows lookups of the PDF starting from only a 
        DOI or a PMID, using the following classmethods:

        FindIt.from_pmid(pmid, **kwargs)

        FindIt.from_doi(doi, **kwargs)

        The machinery in this code performs all necessary data lookups 
        (e.g. looking up a missing DOI, or using a DOI to get a PubMedArticle)
        to end up with a url and reason, which attaches to the FindIt object
        in the following attributes:

        source = FindIt(pmid=PMID)
        source.url
        source.reason
        source.pmid
        source.doi
        source.doi_score

        The "doi_score" is an indication of where the DOI for this PMID ended up
        coming from. If it was supplied by the user or by PubMed, doi_score will be 10.
        If CrossRef came into play during the process to find a DOI that was missing
        for the PubMedArticle object, the doi_score will come from the CrossRef "top
        result".

        *** IMPORTANT NOTE ***

        In many cases, this code performs intermediary HTTP requests in order to 
        scrape a PDF url out of a page, and sometimes tests the url to make sure
        that what's being sent back is in fact a PDF.

        If you would like these requests to go through a proxy (e.g. if you would
        like to prevent making multiple requests of the same pages, which may have
        effects like getting your IP shut off from PubMedCentral), set the 
        HTTP_PROXY environment variable in your code or on the command line before
        using any FindIt functionality.
'''

__author__='nthmost'

from urlparse import urlparse

        
import requests, os, logging

from ..pubmedfetcher import PubMedFetcher
from ..pubmedarticle import square_voliss_data_for_pma
from ..convert import PubMedArticle2doi_with_score, doi2pmid
from ..exceptions import *
from ..text_mining import re_numbers
from ..utils import asciify
from ..eutils_common import SQLiteCache, get_cache_path

from .journal_formats import *
from .dances import *
from .journal_cantdo_list import JOURNAL_CANTDO_LIST

fetch = PubMedFetcher()

DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser('~'),'.cache')
CACHE_FILENAME = 'findit-cache.db'

class FindIt(object):

    @classmethod
    def by_pmid(cls, pmid, *args, **kwargs):
        kwargs['pmid'] = pmid
        return cls(args, kwargs)

    @classmethod
    def by_doi(cls, doi, *args, **kwargs):
        kwargs['doi'] = doi
        return cls(args, kwargs)
    
    def __init__(self, *args, **kwargs):    
        self.pmid = kwargs.get('pmid', None)
        self.doi = kwargs.get('doi', None)
        self.url = kwargs.get('url', None)
        self.reason = None
        self.use_nih = kwargs.get('use_nih', False)
        self.use_crossref = kwargs.get('use_crossref', True)
        self.doi_min_score = kwargs.get('doi_min_score', 2.3)
        self.tmpdir = kwargs.get('tmpdir', '/tmp')
        self.doi_score = None
        self.pma = None
        self._backup_url = None

        cachedir = kwargs.get('cachedir', DEFAULT_CACHE_DIR)
        self._cache_path = get_cache_path(cachedir, CACHE_FILENAME)
        self._cache = None if self._cache_path is None else SQLiteCache(self._cache_path)

        self._logger = logging.getLogger('metapub.FindIt')

        if self.pmid:
            self._load_pma_from_pmid()
        elif self.doi:
            self._load_pma_from_doi()
        else:
            raise MetaPubError('Supply either a pmid or a doi to instantiate. e.g. FindIt(pmid=1234567)')

        if self._cache:
            #cache_key = self._make_cache_key()
            cache_key = self.pmid
            self._cache[self.pmid] = res_text
            self._logger.info('cached results for PMID {cache_key}'.format(cache_key=cache_key))

        try:
            self.url, self.reason = find_article_from_pma(self.pma, use_nih=self.use_nih)
        except requests.exceptions.ConnectionError, e:
            self.url = None
            self.reason = 'TXERROR: %r' % e

    @property
    def backup_url(self):
        '''A backup url to try if the first url doesn't pan out.'''
        if not self.doi:
            return None

        if self._backup_url is not None:
            return self._backup_url

        baseurl = the_doi_2step(self.doi)

        urlp = urlparse(baseurl)

        # maybe it's sciencedirect or elsevier?
        if urlp.hostname.find('sciencedirect') > -1 or urlp.hostname.find('elsevier') > -1:
            if self.pma.pii:
                try:
                    self._backup_url = the_sciencedirect_disco(self.pma)
                except Exception, e:
                    print(e)
                    pass

        # maybe it's an "early" print? if so it might look like this:
        #   
        #if urlp.path.find('early'):
        #    return None

        if self._backup_url is None and urlp.path.find('.') > -1:
            extension = urlp.path.split('.')[-1]
            if extension == 'long':
                self._backup_url = baseurl.replace('long', 'full.pdf')
            elif extension == 'html':
                self._backup_url = baseurl.replace('full', 'pdf').replace('html', 'pdf')

        if self._backup_url is None:
            # a shot in the dark...
            if urlp.path.endswith('/'):
                self._backup_url = baseurl + 'pdf'
            else:
                self._backup_url = baseurl + '.full.pdf'
                
        return self._backup_url

    def _load_pma_from_pmid(self):
        self.pma = fetch.article_by_pmid(self.pmid)
        if self.pma.doi:
            self.doi = self.pma.doi
            self.doi_score = 10.0
        
        if self.pma.doi==None:
            if self.use_crossref:
                self.pma.doi, self.doi_score = PubMedArticle2doi_with_score(self.pma, min_score=self.doi_min_score)
                if self.pma.doi == None:
                    self.reason = 'MISSING: DOI missing from PubMedArticle and CrossRef lookup failed.'
                else:
                    self.doi = self.pma.doi

    def _load_pma_from_doi(self):
        self.pmid = doi2pmid(self.doi)
        if self.pmid:
            self.pma = fetch.article_by_pmid(self.pmid)
            self.doi_score = 10.0
        else:
            raise MetaPubError('Could not get a PMID for DOI %s' % self.doi)

    def to_dict(self):
        return { 'pmid': self.pmid,
                 'doi': self.doi,
                 'reason': self.reason,
                 'url': self.url,
                 'doi_score': self.doi_score,
               }

