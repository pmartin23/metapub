# -*- coding: utf-8 -*-

from __future__ import print_function

import os, sys, logging, shutil
from urlparse import urlparse

from metapub import PubMedFetcher 
from metapub.exceptions import MetaPubError

import requests, json
from tabulate import tabulate

####
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)
####

def asciify(inp):
    '''nuke all the unicode from orbit. it's the only way to be sure.'''
    return inp.encode('ascii', 'ignore')

fetch = PubMedFetcher()

class CrossRef(object):

    query_url = 'http://search.crossref.org/dois?q={title}&jtitle={jtitle}&aulast={author_lastname}&volume={volume}&spage={start_page}&year={year}&sort=score'

    def __init__(self, pma=None, **kwargs):
        '''takes citation details or PubMedArticle object. does a doi lookup by 
            submitting citation.  results should be analyzed since there's not 
            always an exact match. Result scores under 2.0 are usually False matches.'''

        self.params =  { 'title': asciify(self.pma.title).replace(' ', '+'), 
                         'volume': self.pma.volume,
                         'year': self.pma.year,
                         'author_lastname': asciify(self.pma.author1_last_fm.split(' ')[0]),
                         'jtitle': asciify(self.pma.journal),
                         'start_page': self.pma.first_page,
                       }

        # filled after query:
        self.title = None
        self.doi = None
        self.score = None
        self.normalizedScore = None
        self.fullCitation = None
        self.year = None
        self.coins = None
        self.results = None
        self.slugs = {}

        self.query_api()

    def query_api(self):
        q = self.query_url.format(**self.params)
        response = requests.get(q)
        if response.status_code==200:
            try:
                results = json.loads(response.text)
            except ValueError:
                raise MetaPubError('search.crossref.org returned invalid JSON for %s' % q)
        else:
            raise MetaPubError('search.crossref.org returned HTTP %s (query was %s)' % (response.status_code, q))

        self.results = results

        top_results = []
        for result in results:
            if result['score'] > 2:
                top_results.append(result)

        if top_results==[]:
            for result in results:
                if result['fullCitation'].find(self.params['author_lastname']) > -1:
                    if result['fullCitation'].find(self.params['start_page']) > -1:
                        top_results.append(result)

        if top_results:
            top_result = top_results[0]

            self.doi = top_result['doi']
            self.year = top_result['year']
            self.title = top_result['title']
            self.score = top_result['score']
            self.normalizedScore = top_result['normalizedScore']
            self.fullCitation = top_result['fullCitation']
            self.coins = top_result['coins']
            self._parse_coins(self.coins)

    def _parse_coins(self, coins):
        #         coins: "ctx_ver=Z39.88-2004&amp;rft_id=info%3Adoi%2Fhttp%3A%2F%2Fdx.doi.org%2F10.2307%2F40250596&amp;rfr_id=info%3Asid%2Fcrossref.org%3Asearch&amp;rft.atitle=Research+and+Relevant+Knowledge%3A+American+Research+Universities+since+World+War+II&amp;rft.jtitle=Academe&amp;rft.date=1994&amp;rft.volume=80&amp;rft.issue=1&amp;rft.spage=56&amp;rft.aufirst=Winton+U.&amp;rft.aulast=Solberg&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal&amp;rft.genre=article&amp;rft.au=Winton+U.+Solberg&amp;rft.au=+Roger+L.+Geiger",
        self.slugs = dict([item.split('=') for item in coins.split('&amp;')])
        return self.slugs



if __name__=='__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        print('Supply filename of pmid list as the argument to this script.')
        sys.exit()
    
    pmids = open(filename, 'r').readlines()

    results_table = { 'pmid': [], 'pma_title': [], 'cr_title': [], 'doi': [], 'score': [], 'pma_author': [], 'cr_author': []} 
    for pmid in pmids:
        pmid = pmid.strip()
        if pmid:
            results_table['pmid'].append(pmid)
            try:
                pma = fetch.article_by_pmid(pmid)
            except:
                print("%s: Could not fetch" % pmid)
            try:
                CR = CrossRef(pma)
            except MetaPubError, e:
                print(pmid, e)
                continue
                
            results_table['pma_title'].append(pma.title)
            results_table['cr_title'].append(CR.title)
            results_table['doi'].append(CR.doi)
            results_table['score'].append(CR.score)

            if CR.slugs != {}:
                results_table['cr_author'].append(CR.slugs['rft.au'])
            else:
                from IPython import embed; embed()
                results_table['cr_author'].append('')            

            results_table['pma_author'].append(pma.author1_last_fm)
            print(pmid, CR.doi, CR.score, sep='\t')

    headers = ['pmid', 'doi', 'pma_title', 'cr_title', 'pma_author', 'cr_author', 'score']
    tabulated = tabulate(results_table, headers, tablefmt="simple")
        

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

