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

    @property
    def pmid(self):
        return self._get('MedlineCitation/PMID')

    @property
    def abstract(self):
        return self._get('MedlineCitation/Article/Abstract/AbstractText')

    @property
    # N.B. Citations may have 0 authors. e.g., pmid:7550356
    def authors(self):
        authors = [ _au_to_last_fm(au) for au in self.content.findall('MedlineCitation/Article/AuthorList/Author') ]
        return authors

    @property
    def authors_str(self):
        return '; '.join(self.authors) 

    @property
    def author1_last_fm(self):
        """return first author's name, in format Last INITS (space between surname and inits)"""
        return _au_to_last_fm(self.content.find('MedlineCitation/Article/AuthorList/Author'))

    @property
    def author1_lastfm(self):
        """return first author's name, in format LastINITS"""
        if self.author1_last_fm is not None:
            return self.author1_last_fm.replace(' ','')
        return None

    @property
    def journal(self):
        j = self._get('MedlineCitation/Article/Journal/ISOAbbreviation')
        if j is None:
            # e.g., http://www.ncbi.nlm.nih.gov/pubmed?term=21242195
            j = self._get('MedlineCitation/Article/Journal/Title')
        assert j is not None
        return j

    @property
    def pages(self):
        return self._get('MedlineCitation/Article/Pagination/MedlinePgn') 

    @property
    def first_page(self):
        try:
            return self.pages.partition('-')[0]
        except AttributeError:
            return None

    @property
    def title(self):
        return self._get('MedlineCitation/Article/ArticleTitle') 

    @property
    def volume(self):
        try:
            return self.content.find('MedlineCitation/Article/Journal/JournalIssue/Volume').text
        except AttributeError:
            return None

    @property
    def issue(self):
        try:
            return self.content.find('MedlineCitation/Article/Journal/JournalIssue/Issue').text
        except AttributeError:
            return None

    @property
    def volume_issue(self):
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

    @property
    def year(self):
        y = self._get('MedlineCitation/Article/Journal/JournalIssue/PubDate/Year')
        if y is None:
            # case applicable for pmid:9887384 (at least)
            y = self._get('MedlineCitation/Article/Journal/JournalIssue/PubDate/MedlineDate')[0:4]
        assert y is not None
        return y

    @property
    def doi(self):
        return self._get('PubmedData/ArticleIdList/ArticleId[@IdType="doi"]')

    @property
    def pii(self):
        return self._get('PubmedData/ArticleIdList/ArticleId[@IdType="pii"]')

    @property
    def pmc(self):
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

