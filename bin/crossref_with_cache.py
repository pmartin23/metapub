# -*- coding: utf-8 -*-

from __future__ import print_function

import os, sys, shutil
import hashlib
import time
import logging
import json
from urlparse import urlparse

import requests

from metapub import PubMedFetcher 
from metapub.exceptions import MetaPubError

from eutils.sqlitecache import SQLiteCache

from tabulate import tabulate

####
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)
####

def asciify(inp):
    '''nuke all the unicode from orbit. it's the only way to be sure.'''
    if inp:
        return inp.encode('ascii', 'ignore')
    else:
        return ''

def parameterize(inp):
    '''make strings suitable for submission to GET-based query service'''
    return asciify(inp).replace(' ', '+')

fetch = PubMedFetcher()

DEFAULT_CACHE_PATH = os.path.join(os.path.expanduser('~'),'.cache','crossref-cache.db')

class CrossRef(object):
    _logger = logging.getLogger('metapub')         #.setLevel(logging.DEBUG)
    _cache = SQLiteCache(DEFAULT_CACHE_PATH)

    def __init__(self, **kwargs):
        '''takes citation details or PubMedArticle object. does a doi lookup by 
            submitting citation.  results should be analyzed since there's not 
            always an exact match. Result scores under 2.0 are usually False matches.

        '''
        self.query_base_url = 'http://search.crossref.org/dois?q=%s'
        self.default_args = { 'sort': 'score' }
        # contains last parameters submitted to a query.
        self.last_params = {}

    def _parse_coins(self, coins):
        self.slugs = dict([item.split('=') for item in coins.split('&amp;')])
        return self.slugs

    def query_from_PubMedArticle(self, pma):
        '''Takes a PubMedArticle object and submits as many citation details 
            as possible to get well-polarized results.
        '''
        self.last_params = { 
                         'volume': parameterize(pma.volume),
                         'issue': parameterize(pma.issue),
                         'year': parameterize(pma.year),
                         'aulast': parameterize(pma.author1_last_fm.split(' ')[0]),
                         'jtitle': parameterize(pma.journal).replace('.', '').replace('J+', ''),
                         'start_page': parameterize(pma.first_page),
                           }
        search = parameterize(pma.title)
        return self.query(search, self.last_params)

    def _query_api(self, q):
        response = requests.get(q)
        if response.status_code==200:
            return response.text
        else:
            raise Exception('search.crossref.org returned HTTP %s (query was %s)' % (response.status_code, q))

    def _get_enhanced_results(self, results):
        enhanced_results = []
        for result in results:
            result['slugs'] = self._parse_coins(result['coins'])
            enhanced_results.append(result)
                
        return enhanced_results

    def _assemble_query(self, search, params):
        defining_args = self.default_args.copy()
        if params != {}:
            for k,v in params.items():
                defining_args[k] = parameterize(v)
        q = self.query_base_url % search 
        q += '&'.join(['%s=%s' % (k,v) for (k,v) in defining_args.items()])
        return q

    def query(self, search, params, skip_cache=False):
        '''
        Takes a base search string (required) and any number of the following
        available params (optional) as a dictionary. Returns a list of 
        dictionaries of results. Usually the top result is the best result.

        NOTE: it's been observed that submitting the article title (or some part 
        thereof) as the search string works MUCH better then supplying it with 
        the atitle parameter.

        If skip_cache is set, query will always hit the CrossRef API instead
        of looking in cache for previous identical queries.

        :param: search (string)
        :param: params (dict)
        :param: skip_cache (bool) (optional) (default: False)

        Available params for submission to search.crossref.org:
        
            aulast: first author's last name
            aufirst: first author's first name and/or initials
            jtitle: name of the journal article published in
            year: year of publication
            volume: volume of publication
            issue: issue of publication
            spage: starting page of article in publication
            atitle: title of the article (NOT RECOMMENDED, see above NOTE)
        '''
        self.last_params = params
        q = self._assemble_query(search, params)

        res_text = None
        if not skip_cache:
            res_text = self._query_cache(q) 

        if res_text == None: 
            res_text = self._query_api(q) 

            if self._cache:
                cache_key = self._make_cache_key(q)
                self._cache[cache_key] = res_text
                self._logger.info('cached results for key {cache_key} ({q}) '.format(
                        cache_key=cache_key, q=q))

        if res_text:
            try:
                results = json.loads(res_text)
            except ValueError:
                raise Exception('invalid JSON response for %s (%s)' % (q, res_text))
            return self._get_enhanced_results(results)
        return []


    def get_best_result(self, results, params={}):
        '''Returns most likely match from result candidates. If all candidates fail
            very basic tests of matchiness (e.g. is this the author name?), it returns None.'''
        top_results = []
        for result in results:
            if result['score'] > 2:
                top_results.append(result)

        if top_results:
            return top_results[0]

        test_items = [val for key,val in params.items() if key != 'atitle']
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

    def _make_cache_key(self, inp):
        return hashlib.md5(inp).hexdigest() 

    def _query_cache(self, q, skip_sleep=False):
        """return results for a CrossRef query, possibly from the cache.

        :param: q: an assembled query string based on input params
        :param: skip_sleep: whether to bypass query throttling
        :rtype: json string

        The args are joined with args required by search.crossref.org.

        All args will be converted to ASCII, with spaces converted to '+'.
        """

        # sqlite cache usage lifted from eutils (thanks Reece!) --nthmost

        if self._cache:
            cache_key = self._make_cache_key(q)
            try:
                v = self._cache[cache_key]
                self._logger.debug('cache hit for key {cache_key} ({q}) '.format(
                    cache_key=cache_key, q=q))
                return v
            except KeyError:
                self._logger.debug('cache miss for key {cache_key} ({q}) '.format(
                        cache_key=cache_key, q=q))
                #from IPython import embed; embed()
                #sys.exit()
                return None
        else:
            self._logger.debug('cache disabled (self._cache is None)')
            return None


        #if not skip_sleep:
        #    req_int = self.request_interval() if callable(self.request_interval) else self.request_interval
        #    sleep_time = req_int - (time.clock()-self._last_request_clock)
        #    if sleep_time > 0:
        #        self._logger.debug('sleeping {sleep_time:.3f}'.format(sleep_time=sleep_time))
        #        time.sleep(sleep_time)


if __name__=='__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        print('Supply filename of pmid list as the argument to this script.')
        sys.exit()
    
    pmids = open(filename, 'r').readlines()

    results_table = { 'pmid': [], 'doi': [], 'score': [], 'pma_aulast': [], 'cr_aulast': [], 'pma_journal': [], 'cr_journal': [] } 
    #results_table = { 'pmid': [], 'pma_title': [], 'cr_title': [], 'doi': [], 'score': [], 'pma_author': [], 'cr_author': []} 

    CR = CrossRef()

    for pmid in pmids:
        pmid = pmid.strip()
        if pmid:
            results_table['pmid'].append(pmid)
            try:
                pma = fetch.article_by_pmid(pmid)
            except:
                print("%s: Could not fetch" % pmid)
            results = CR.query_from_PubMedArticle(pma)
            top_result = CR.get_best_result(results, CR.last_params)
                
            #results_table['pma_title'].append(pma.title)
            results_table['pma_journal'].append(pma.journal)
            #results_table['cr_title'].append(top_result['title'])
            results_table['doi'].append(top_result['doi'])
            results_table['score'].append(top_result['score'])

            if top_result['slugs'] != {}:
                results_table['cr_aulast'].append(top_result['slugs']['rft.aulast'])
                results_table['cr_journal'].append(top_result['slugs']['rft.jtitle'])
            else:
                results_table['cr_aulast'].append('')            
                results_table['cr_journal'].append('')

            results_table['pma_aulast'].append(pma.author1_last_fm)
            print(pmid, top_result['doi'], top_result['score'], sep='\t')

    headers = ['pmid', 'doi', 'pma_title', 'cr_title', 'pma_author', 'cr_author', 'score']
    tabulated = tabulate(results_table, results_table.keys(), tablefmt="simple")
    print(tabulated)
        

# crossref return looks like:
"""{
        doi: "http://dx.doi.org/10.2307/40250596",
        score: 2.0651011,
        normalizedScore: 74,
        title: "Research and Relevant Knowledge: American Research Universities since World War II",
        fullCitation: "Winton U. Solberg, Roger L. Geiger, 1994, 'Research and Relevant Knowledge: American Research Universities since World War II', <i>Academe</i>, vol. 80, no. 1, p. 56",
        coins: "ctx_ver=Z39.88-2004&amp;rft_id=info%3Adoi%2Fhttp%3A%2F%2Fdx.doi.org%2F10.2307%2F40250596&amp;rfr_id=info%3Asid%2Fcrossref.org%3Asearch&amp;rft.atitle=Research+and+Relevant+Knowledge%3A+American+Research+Universities+since+World+War+II&amp;rft.jtitle=Academe&amp;rft.date=1994&amp;rft.volume=80&amp;rft.issue=1&amp;rft.spage=56&amp;rft.aufirst=Winton+U.&amp;rft.aulast=Solberg&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal&amp;rft.genre=article&amp;rft.au=Winton+U.+Solberg&amp;rft.au=+Roger+L.+Geiger",
        year: "1994"
        },"""

