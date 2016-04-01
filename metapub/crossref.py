# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, unicode_literals

import os, sys, shutil
import re
import hashlib
import logging
import json

#py3k / py2k compatibility
from six.moves import urllib

import requests

from .eutils_common import SQLiteCache, get_cache_path
from .exceptions import *
from .config import DEFAULT_CACHE_DIR

from .utils import asciify, parameterize, remove_html_markup, deparameterize, remove_chars
from .base import Borg

CACHE_FILENAME = 'crossref-cache.db'

#TODO implement usage of crossref V2 returns which are much nicer.

# crossref V1 API return looks like:
""" {
        doi: "http://dx.doi.org/10.2307/40250596",
        score: 2.0651011,
        normalizedScore: 74,
        title: "Research and Relevant Knowledge: American Research Universities since World War II",
        fullCitation: "Winton U. Solberg, Roger L. Geiger, 1994, 'Research and Relevant Knowledge: American Research Universities since World War II', <i>Academe</i>, vol. 80, no. 1, p. 56",
        coins: "ctx_ver=Z39.88-2004&amp;rft_id=info%3Adoi%2Fhttp%3A%2F%2Fdx.doi.org%2F10.2307%2F40250596&amp;rfr_id=info%3Asid%2Fcrossref.org%3Asearch&amp;rft.atitle=Research+and+Relevant+Knowledge%3A+American+Research+Universities+since+World+War+II&amp;rft.jtitle=Academe&amp;rft.date=1994&amp;rft.volume=80&amp;rft.issue=1&amp;rft.spage=56&amp;rft.aufirst=Winton+U.&amp;rft.aulast=Solberg&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal&amp;rft.genre=article&amp;rft.au=Winton+U.+Solberg&amp;rft.au=+Roger+L.+Geiger",
        year: "1994"
    },
"""


class CrossRef(Borg):
    """
       CrossRef: a Borg singleton object backed by an SQLite cache

       Disable cacheing by supplying cachedir=None in init arguments.

       Change class logging level to DEBUG (default: INFO) by supplying
       debug=True with init arguments.
    """

    _log = logging.getLogger('metapub.CrossRef')

    re_rfts = re.compile('rft\.(.*?)&amp;')
    re_rfrs = re.compile('rfr_id=.*?&amp;')

    def __init__(self, **kwargs):
        """ Takes citation details or PubMedArticle object. does a doi lookup by
            submitting citation.  

            Results should be analyzed since there's not always an exact match.

            Result scores under 2.0 are usually False matches.
            Result scores over 3.0 are always (?) True.  
            Between 2.0 and 3.0 is a grey area: be wary and check results 
                        against any known info you may have.

            Usage examples:

                CR = CrossRef()     # starts the query cache engine
                results = CR.query('Molecular epidemiological analysis of mitochondrial', 
                                params={'jtitle': 'Acta Otolaryngol', 'year': '2011' })
                top_result = CR.get_top_result(results)

            Starting from a known pubmed ID:
                pma = PubMedFetcher().article_by_pmid(known_pmid)
                results = CR.query_from_PubMedArticle(pma)
                top_result = CR.get_top_result(results, CR.last_params, use_best_guess=True)

            NOTE: if you don't supply "CR.last_params", you can't use the "use_best_guess"
                operator. In cases where all results have scores under 2, no results will 
                be returned unless use_best_guess=True.  That's often desired behavior, 
                since results with scores under 2 are usually pretty bad.
        """
        self.query_base_url = 'http://search.crossref.org/dois?q=%s&'
        self.default_args = {'sort': 'score'}
        # contains last search and parameters submitted to a query.
        self.last_search = ''
        self.last_params = {}
        self.last_query = ''

        cachedir = kwargs.get('cachedir', DEFAULT_CACHE_DIR)

        if kwargs.get('debug', False):
            self._log.setLevel(logging.DEBUG) 
        else:
            self._log.setLevel(logging.INFO) 
        
        if cachedir:
            self._cache_path = get_cache_path(cachedir, CACHE_FILENAME)
            self._cache = SQLiteCache(self._cache_path)
        else:
            self._cache_path = None
            self._cache = None

    def _parse_coins(self, coins):
        # there are multiple 'au' items. pull them out, add them to the list of authors,
        # then tack them in as a list after all the others.
        
        authors = []
        coins = remove_html_markup(coins)
        rfts = self.re_rfts.findall(coins)
        rfr_ids = self.re_rfrs.findall(coins)
        slugs = {}
        for item in rfts + rfr_ids:
            key, val = item.split('=', 1)
            if key == 'au':
                authors.append(deparameterize(val))
            else:
                slugs[key] = deparameterize(val, '+')
        return slugs

    def query_from_PubMedArticle(self, pma):
        """ Takes a PubMedArticle object and submits as many citation details
            as possible to get well-polarized results.

        :param pma: PubMedArticle object
        :return: results of CrossRef query
        :rtype dict:
        """
        aulast = None if pma.author1_last_fm is None else pma.author1_last_fm.split(' ')[0]
        jtitle = remove_chars(pma.journal, '.[]()<>,').replace('J+', '')
        params = { 
                 'volume': parameterize('%s' % pma.volume),
                 'issue': parameterize('%s' % pma.issue),
                 'year': parameterize('%s' % pma.year),
                 'aulast': parameterize(aulast),
                 'jtitle': parameterize(jtitle),
                 'start_page': parameterize(pma.first_page),
             }
        search = parameterize(pma.title)
        return self.query(search, params)

    def _query_api(self, q):
        response = requests.get(q)
        if response.status_code == 200:
            return response.text
        else:
            raise CrossRefConnectionError('search.crossref.org returned HTTP %s (query was %s)' % (response.status_code, q))

    def _get_enhanced_results(self, results):
        enhanced_results = []
        for result in results:
            result['score'] = float(result['score'])
            result['doi'] = result['doi'].replace('http://dx.doi.org/', '')
            # result['coins'] = urllib.parse.unquote(result['coins']) - best to not use unquoting if we have unicode
            result['slugs'] = self._parse_coins(result['coins'])
            enhanced_results.append(result)
        return enhanced_results

    def _assemble_query(self, search, params):
        defining_args = self.default_args.copy()
        if params != {}:
            for key, val in list(params.items()):
                defining_args[key] = parameterize(val)

        qstring = self.query_base_url % urllib.parse.quote_plus(search)
        qstring += '&'.join(['%s=%s' % (key, urllib.parse.quote_plus(val)) for (key, val) in list(defining_args.items())])
        return qstring

    def query(self, search, params=None, skip_cache=False):
        """
        Takes a base search string (required) and any number of the following
        available params (optional) as a dictionary. Returns a list of 
        dictionaries of results. Usually the top result is the best result.

        NOTE: it's been observed that submitting the article title (or some part 
        thereof) as the search string works MUCH better then supplying it with 
        the atitle parameter.

        If skip_cache is set, query will always hit the CrossRef API instead
        of looking in cache for previous identical queries.

        :param search: (string)
        :param params: (dict) (optional) (default: empty dict)
        :param skip_cache: (bool) (optional) (default: False)

        Available params for submission to search.crossref.org:
        
            aulast: first author's last name
            aufirst: first author's first name and/or initials
            jtitle: name of the journal article published in
            year: year of publication
            volume: volume of publication
            issue: issue of publication
            spage: starting page of article in publication
            atitle: title of the article (NOT RECOMMENDED, see above NOTE)

        WARNING: This function will not check that you have submitted appropriate params.
                 If you get an error or no results, please check your params and try again.
        """
        if params is None:
            params = {}

        qstring = self._assemble_query(search, params)

        self.last_search = search
        self.last_params = params
        self.last_query = qstring

        res_text = None
        if not skip_cache:
            res_text = self._query_cache(qstring) 

        if res_text is None:
            res_text = self._query_api(qstring)

            if self._cache:
                cache_key = self._make_cache_key(qstring)
                self._cache[cache_key] = res_text
                self._log.info('cached results for key {cache_key} ({q}) '.format(
                        cache_key=cache_key, q=qstring))

        if res_text:
            try:
                results = json.loads(res_text)
            except ValueError:
                raise CrossRefConnectionError('invalid JSON response for %s (%s)' % (qstring, res_text))
            return self._get_enhanced_results(results)
        return []

    def get_top_result(self, results, params={}, use_best_guess=False, min_score=2.0):
        """ Returns most likely match from result candidates. If all candidates fail
            very basic tests of matchiness (e.g. is this the author name?), it returns None.

        :param results:
        :param params:
        :param use_best_guess:
        :param min_score:
        :return:
        """
        top_results = []
        for result in results:
            if result['score'] > min_score:
                top_results.append(result)

        if top_results:
            return top_results[0]

        test_items = [val for key,val in list(params.items()) if key != 'atitle']

        if params and use_best_guess:
            best_guess = None
            best_equiv = 0
            for result in results:
                equiv_score = 0
                for item in test_items:
                    if result['fullCitation'].find(item):
                        equiv_score += 1
                if equiv_score > best_equiv:
                    best_guess = result
                    best_equiv = equiv_score
            return best_guess
        else:
            return None

    def _make_cache_key(self, inp):
        inp = asciify(inp)
        return hashlib.md5(inp).hexdigest() 

    def _query_cache(self, q):
        """ Return results for a CrossRef query, possibly from the cache.

        The args are joined with args required by search.crossref.org.

        All args will be converted to bytes, with spaces converted to '+'.

        :param q: an assembled query string based on input params
        :return: results for a CrossRef query, possibly from the cache
        :rtype str: json
        """

        # sqlite cache usage lifted from eutils (thanks Reece!) --nthmost

        if self._cache:
            cache_key = self._make_cache_key(q)
            try:
                v = self._cache[cache_key]
                self._log.debug('cache hit for key {cache_key} ({q}) '.format(
                    cache_key=cache_key, q=q))
                return v
            except KeyError:
                self._log.debug('cache miss for key {cache_key} ({q}) '.format(
                        cache_key=cache_key, q=q))
                return None
        else:
            self._log.debug('cache disabled (self._cache is None)')
            return None
