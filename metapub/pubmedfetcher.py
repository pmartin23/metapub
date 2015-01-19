from __future__ import absolute_import

"""metapub.PubMedFetcher -- tools to deal with NCBI's E-utilities interface to PubMed"""

import xml.etree.ElementTree as ET
from eutils.exceptions import EutilsBadRequestError
import requests

from .pubmedarticle import PubMedArticle
from .utils import Borg, get_pmid_for_otherid
from .exceptions import MetaPubError

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

    def __init__(self, method='eutils'):
        Borg.__init__(self)
        self.method = method

        if method=='eutils':
            import eutils.client as ec
            self.qs = ec.QueryService()
            self.article_by_pmid = self._eutils_article_by_pmid
            self.article_by_pmcid = self._eutils_article_by_pmcid
            self.article_by_doi = self._eutils_article_by_doi
        else:
            raise NotImplementedError('coming soon: fetch from local pubmed via medgen-mysql.')

    def _eutils_article_by_pmid(self, pmid):
        try:
            result = self.qs.efetch(args={'db': 'pubmed', 'id': pmid})
        except EutilsBadRequestError:
            raise MetaPubError('Invalid ID "%s" (rejected by Eutils); please check the number and try again.' % pmid)
        if result.find('ERROR') > -1:
            raise MetaPubError('PMID %s returned ERROR; cannot construct PubMedArticle (no such PMID)' % pmid)
        return PubMedArticle(result)

    def _eutils_article_by_pmcid(self, pmcid):
        pmid = get_pmid_for_otherid(pmcid)
        if pmid is None:
            raise MetaPubError('No PMID available for PubMedCentral id %s' % pmcid)
        return self._eutils_article_by_pmid(pmid)
    
    def _eutils_article_by_doi(self, doi):
        pmid = get_pmid_for_otherid(doi)
        if pmid is None:
            raise MetaPubError('No PMID available for doi %s' % doi)
        return self._eutils_article_by_pmid(pmid)

    def pmids_for_citation(self, **kwargs):
        '''returns list of pmids for given citation. requires at least 3/5 of these keyword arguments:
            journal_title
            year
            volume
            first_page
            author_name (works best with only Author1's last name supplied)
        '''

        # output format in return:
        # journal_title|year|volume|first_page|author_name|your_key|
        base_uri = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/ecitmatch.cgi?db=pubmed&retmode=xml&bdata={journal_title}|{year}|{volume}|{first_page}|{author_name}|metapub|'
        inp_dict = { 'journal_title': kwargs.get('journal_title', '').replace(' ', '+'),
                     'year': str(kwargs.get('year', '')), 
                     'volume': str(kwargs.get('volume', '')),
                     'first_page': str(kwargs.get('first_page', '')),
                     'author_name': _reduce_author_string(kwargs.get('author_name', '')).replace(' ', '+'),
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

