from __future__ import absolute_import

"""metapub.pubmedarticle -- PubMedArticle class instantiated by supplying ncbi XML string."""

import logging
import xml.etree.ElementTree as ET

from .base import MetaPubObject
from .exceptions import MetaPubError

logger = logging.getLogger()

class PubMedArticle(MetaPubObject):
    '''This PubMedArticle class receives an XML string as its required argument
    and parses it into its constituent parts, exposing them as attributes. 

    Usage:
        paper = PubMedArticle(xml_string)

    To query services to return an article by pmid, use PubMedFetcher, which
    returns PubMedArticle objects.
    '''

    def __init__(self, xmlstr, *args, **kwargs):
        super(PubMedArticle, self).__init__(xmlstr, 'PubmedArticle', args, kwargs)
        self.pmid = self._get_pmid()
        self.abstract = self._get_abstract()
        self.authors = self._get_authors()
        self.authors_str = self._get_authors_str()
        self.author1_last_fm = self._get_author1_last_fm()        
        self.author1_lastfm = self._get_author1_lastfm()
        self.title = self._get_title()
        self.journal = self._get_journal()
        self.pages = self._get_pages()
        self.first_page = self._get_first_page()
        self.last_page = self._get_last_page()
        self.volume = self._get_volume()
        self.issue = self._get_issue()
        self.volume_issue = self._get_volume_issue()
        self.year = self._get_year()
        self.doi = self._get_doi()
        self.pii = self._get_pii()
        self.pmc = self._get_pmc()

    def to_dict(self):
        outd = self.__dict__
        outd.pop('content')
        outd.pop('xmlstr')
        return self.__dict__

    def _get_pmid(self):
        return self._get('MedlineCitation/PMID')

    def _get_abstract(self):
        return self._get('MedlineCitation/Article/Abstract/AbstractText')

    def _get_authors(self):
        # N.B. Citations may have 0 authors. e.g., pmid:7550356
        authors = [ _au_to_last_fm(au) for au in self.content.findall('MedlineCitation/Article/AuthorList/Author') ]
        return authors

    def _get_authors_str(self):
        return '; '.join(self.authors) 

    def _get_author1_last_fm(self):
        '''return first author's name, in format Last INITS (space between surname and inits)'''
        return _au_to_last_fm(self.content.find('MedlineCitation/Article/AuthorList/Author'))

    def _get_author1_lastfm(self):
        '''return first author's name, in format LastINITS'''
        if self.author1_last_fm is not None:
            return self.author1_last_fm.replace(' ','')
        return None

    def _get_journal(self):
        j = self._get('MedlineCitation/Article/Journal/ISOAbbreviation')
        if j is None:
            # e.g., http://www.ncbi.nlm.nih.gov/pubmed?term=21242195
            j = self._get('MedlineCitation/Article/Journal/Title')
        assert j is not None
        return j

    def _get_pages(self):
        return self._get('MedlineCitation/Article/Pagination/MedlinePgn') 

    def _get_first_page(self):
        try:
            return self.pages.split('-')[0]
        except AttributeError:
            return self.pages

    def _get_last_page(self):
        try:
            lastnum = self.pages.split('-')[1]
            return lastnum
            
            #TODO: return true last page in situations like self.pages = "148-52"
            #           i.e. we want last_page = "152", not "52"
            #if lastnum < self.first_page:
            #    len(lastnum)....

        except IndexError, AttributeError:
            return None

    def _get_title(self):
        return self._get('MedlineCitation/Article/ArticleTitle') 

    def _get_volume(self):
        try:
            return self.content.find('MedlineCitation/Article/Journal/JournalIssue/Volume').text
        except AttributeError:
            return None

    def _get_issue(self):
        try:
            return self.content.find('MedlineCitation/Article/Journal/JournalIssue/Issue').text
        except AttributeError:
            return None

    def _get_volume_issue(self):
        ji = self.content.find('MedlineCitation/Article/Journal/JournalIssue')
        try:
            return '%s(%s)' % (ji.find('Volume').text, ji.find('Issue').text)
                               
        except AttributeError:
            pass
        try:
            return ji.find('Volume').text
        except AttributeError:
            pass
        # electronic pubs may not have volume or issue
        # e.g., http://www.ncbi.nlm.nih.gov/pubmed?term=20860988
        logger.info("No volume for "+self.pmid)
        return None

    def _get_year(self):
        y = self._get('MedlineCitation/Article/Journal/JournalIssue/PubDate/Year')
        if y is None:
            # case applicable for pmid:9887384 (at least)
            y = self._get('MedlineCitation/Article/Journal/JournalIssue/PubDate/MedlineDate')[0:4]
        assert y is not None
        return y

    def _get_doi(self):
        return self._get('PubmedData/ArticleIdList/ArticleId[@IdType="doi"]')

    def _get_pii(self):
        return self._get('PubmedData/ArticleIdList/ArticleId[@IdType="pii"]')

    def _get_pmc(self):
        try:
            return self._get('PubmedData/ArticleIdList/ArticleId[@IdType="pmc"]')[3:]
        except TypeError:
            return None
    
    def __str__(self):
        return( '%s (%s. %s, %s:%s)' % (
            self.title, self.authors_str, self.journal, self.volume_issue, self.pages) )

############################################################################
## Utilities

def _au_to_last_fm(au):
    if au is None:
        return
    try:
        return au.find('LastName').text + u' ' + au.find('Initials').text
                
    except AttributeError:
        pass
    try:
        return au.find('CollectiveName').text 
    except AttributeError:
        pass
    try:
        return au.find('LastName').text
    except AttributeError:
        pass
    raise MetaPubError("Author structure not recognized")

