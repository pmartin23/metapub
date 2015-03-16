from __future__ import absolute_import

"""metapub.PubMedFetcher -- tools to deal with NCBI's E-utilities interface to PubMed"""

import xml.etree.ElementTree as ET
from eutils.exceptions import EutilsBadRequestError
import requests

from .pubmedarticle import PubMedArticle
from .pubmedcentral import get_pmid_for_otherid
from .utils import kpick, parameterize
from .text_mining import re_pmid
from .exceptions import *
from .base import Borg
from .config import DEFAULT_EMAIL

class PubMedFetcher(Borg):
    '''PubMedFetcher (a Borg singleton object)

    An interaction layer for querying via specified method to return PubMedArticle objects.
    
    Currently available methods: eutils

    Basic Usage:

        fetch = PubMedFetcher()
    
    To specify a service method (more coming soon):

        fetch = PubMedFetcher('eutils')

    To return an article by querying the service with a known PMID:

        paper = fetch.article_by_pmid('123456')

    Similar methods exist for returning papers by DOI and PM Central id:

        paper = fetch.article_by_doi('10.1038/ng.379')
        paper = fetch.article_by_pmcid('PMC3458974')

    Finally, you can search for PMIDs via citation details by using the pmids_for_citation
    method, for which you only need 3 out of 5 details as a list of one or more PMIDs:

        pmids = fetch.pmids_for_citation(journal='Science', year='2008', volume='4', 
                first_page='7', author_name='Grant')
    '''

    def __init__(self, method='eutils', email=DEFAULT_EMAIL):
        Borg.__init__(self)
        self.method = method

        if method=='eutils':
            import eutils.client as ec
            self.qs = ec.QueryService(tool='metapub', email=email)
            self.article_by_pmid = self._eutils_article_by_pmid
            self.article_by_pmcid = self._eutils_article_by_pmcid
            self.article_by_doi = self._eutils_article_by_doi
            self.pmids_for_query = self._eutils_pmids_for_query
        else:
            raise NotImplementedError('coming soon: fetch from local pubmed via medgen-mysql or filesystem cache.')

    def _eutils_article_by_pmid(self, pmid):
        pmid = str(pmid)
        try:
            result = self.qs.efetch(args={'db': 'pubmed', 'id': pmid})
        except EutilsBadRequestError:
            raise MetaPubError('Invalid ID "%s" (rejected by Eutils); please check the number and try again.' % pmid)

        if result==None:
            return None
        if result.find('ERROR') > -1:
            raise MetaPubError('PMID %s returned ERROR; cannot construct PubMedArticle' % pmid)

        try:
            return PubMedArticle(result)
        except AttributeError:
            # in this case, eutils let us fetch a good-looking pmid, but it did not parse as an article.
            raise InvalidPMID('Pubmed ID "%s" not found.' % pmid)

    def _eutils_article_by_pmcid(self, pmcid):
        # if user submitted a bare number, prepend "PMC" to make sure it is submitted correctly 
        # the conversion API at pubmedcentral.
        pmcid = str(pmcid)
        if re_pmid.findall(pmcid)[0] == pmcid:
            pmcid = 'PMC'+pmcid

        pmid = get_pmid_for_otherid(pmcid)
        if pmid is None:
            raise MetaPubError('No PMID available for PubMedCentral id %s' % pmcid)
        return self._eutils_article_by_pmid(pmid)
    
    def _eutils_article_by_doi(self, doi):
        pmid = get_pmid_for_otherid(doi)
        if pmid is None:
            raise MetaPubError('No PMID available for doi %s' % doi)
        return self._eutils_article_by_pmid(pmid)

    def _eutils_pmids_for_query(self, query='', **kwargs):
        '''returns list of pmids for given freeform query string plus 
            keyword arguments.'''
        q = {}
        q['AID'] = kpick(kwargs, options=['AID', 'doi']) 
        q['PMC'] = kpick(kwargs, options=['pmc', 'pmcid'])
        q['TA'] = kpick(kwargs, options=['TA', 'jtitle', 'journal']) 
        q['DP'] = kpick(kwargs, options=['DP', 'year', 'pdat'])
        q['1AU'] = kpick(kwargs, options=['1AU', 'aulast', 'author1_lastfm', 'author1_last_fm'])
        q['OT'] = kwargs.get('OT', None)
        q['PT'] = kpick(kwargs, options=['PT', 'pubmed_type'])
        q['MH'] = kpick(kwargs, options=['MH', 'mesh', 'MeSH Terms'])
        q['FAU'] = kpick(kwargs, options=['FAU', 'first_author', 'author1'])
        q['IP'] = kpick(kwargs, options=['IP', 'issue'])
        q['TI'] = kpick(kwargs, options=['TI', 'title', 'atitle', 'article_title'])
        q['TW'] = kpick(kwargs, options=['TW', 'text'])
        q['LA'] = kpick(kwargs, options=['LA', 'language'])
        q['VI'] = kpick(kwargs, options=['VI', 'volume', 'vol'])
        q['PUBN'] = kpick(kwargs, options=['PUBN', 'publisher'])
        q['book'] = kwargs.get('book', None)
        q['ISBN'] = kwargs.get('ISBN', None)
        q['LASTAU'] = kwargs.get('LASTAU', None)

        #MeSH Date [MHDA]
        #MeSH Major Topic [MAJR]
        #MeSH Subheadings [SH]
        #MeSH Terms [MH]        
        #q['MHDA'] = kwargs.get('MHDA', None)

        q['PMID'] = kpick(kwargs, options=['pmid', 'uid', 'pubmed_id'])
        
        if query != '':
            query = query + ' '
        for feature in q.keys():
            if q[feature] != None:
                query +='%s[%s] ' % (q[feature], feature)
        
        # option to query pubmed central only:
        # pubmed pmc[sb]
        if kwargs.get('pmc_only', False):
            query += 'pubmed pmc[sb]'

        results = self.qs.esearch({'db': 'pubmed', 'term': query})
        return results


    def pmids_for_citation(self, **kwargs):
        '''returns list of pmids for given citation. requires at least 3/5 of these keyword arguments:
            jtitle or journal (journal title)
            year or date
            volume
            spage or first_page (starting page / first page)
            aulast (first author's last name) or author1_first_lastfm (as produced by PubMedArticle class)

        (Note that these arguments were made to match the tokens that arise from CrossRef's result['slugs'].)
        '''
        # output format in return:
        # journal_title|year|volume|first_page|author_name|your_key|
        base_uri = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/ecitmatch.cgi?db=pubmed&retmode=xml&bdata={journal_title}|{year}|{volume}|{first_page}|{author_name}|metapub|'

        journal_title = kpick(kwargs, options=['jtitle', 'journal', 'journal_title'], default='')
        author_name = _reduce_author_string(kpick(kwargs, 
                        options=['aulast', 'author1_last_fm', 'author', 'authors'], default=''))
        first_page = kpick(kwargs, options=['spage', 'first_page'], default='')
        year = kpick(kwargs, options=['year', 'date', 'pdat'], default='')
        volume = kpick(kwargs, options=['volume'], default='')

        inp_dict = { 'journal_title': parameterize(journal_title, '+'), 
                     'year': str(year),
                     'volume': str(volume),
                     'first_page': str(first_page),
                     'author_name': parameterize(author_name, '+'),
                   }

        req = base_uri.format(**inp_dict)
        content = requests.get(req).text
        pmids = []
        for item in content.split('\n'):
            if item.strip():
                pmid = item.split('|')[-1]
                pmids.append(pmid.strip())
        return pmids
                

def _reduce_author_string(author_string):
    # try splitting by commas
    authors = author_string.split(',')
    if len(authors)<2:
        # try splitting by semicolons
        authors = author_string.split(';')

    author1 = authors[0]
    # presume last name is at the end of the string
    return author1.split(' ')[-1]


""" 
Search Field Descriptions and Tags

from http://www.ncbi.nlm.nih.gov/books/NBK3827/

Affiliation [AD]
Article Identifier [AID]
All Fields [ALL]
Author [AU]
Author Identifier [AUID]
Book [book]
Comment Corrections
Corporate Author [CN]
Create Date [CRDT]
Completion Date [DCOM]
EC/RN Number [RN]
Editor [ED]
Entrez Date [EDAT]
Filter [FILTER]
First Author Name [1AU]
Full Author Name [FAU]
Full Investigator Name [FIR]
Grant Number [GR]   Investigator [IR]
ISBN [ISBN]
Issue [IP]
Journal [TA]
Language [LA]
Last Author [LASTAU]
Location ID [LID]
MeSH Date [MHDA]
MeSH Major Topic [MAJR]
MeSH Subheadings [SH]
MeSH Terms [MH]
Modification Date [LR]
NLM Unique ID [JID]
Other Term [OT]
Owner
Pagination [PG]
Personal Name as Subject [PS]   Pharmacological Action [PA]
Place of Publication [PL]
PMID [PMID]
Publisher [PUBN]
Publication Date [DP]
Publication Type [PT]
Secondary Source ID [SI]
Subset [SB]
Supplementary Concept[NM]
Text Words [TW]
Title [TI]
Title/Abstract [TIAB]
Transliterated Title [TT]
UID [PMID]
Version
Volume [VI]
"""

