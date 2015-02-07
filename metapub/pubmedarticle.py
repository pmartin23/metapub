from __future__ import absolute_import, print_function

"""metapub.pubmedarticle -- PubMedArticle class instantiated by supplying ncbi XML string."""

import logging
from datetime import datetime

from .base import MetaPubObject
from .exceptions import MetaPubError

class PubMedArticle(MetaPubObject):
    '''This PubMedArticle class receives an XML string as its required argument
    and parses it into its constituent parts, exposing them as attributes. 

    Usage:
        paper = PubMedArticle(xml_string)

    To query services to return an article by pmid, use PubMedFetcher, which
    returns PubMedArticle objects.

    When xmlstr is parsed, the `pubmed_type` attribute will be set to one of 'article' or 'book',
    depending on whether PubmedBookArticle or PubmedArticle headings are found in the supplied
    xmlstr at instantiation.

    Since this class needs to work seamlessly in production whether it's a book 
    or an article, the PubmedArticle attributes will always be available (set to None in many
    cases for PubmedBookArticle, e.g. volume, issue, journal), but PubmedBookArticle
    attributes will only be set when pubmed_type='book'.

    PubMedBook special handling of certain attributes:
        * abstract: a joined string from self.book_abstracts
        * title: comes from ArticleTitle

    Special attributes for PubmedBookArticle (pubmed_type='book'):
        * book_id (default: None) - string from IdType="bookaccession", e.g. "NBK1403"
        * book_title (default: None) - string with name of book (as differentiated from ArticleTitle)
        * book_publisher (default: None) - dict containing {'name': string, 'location': string}
        * book_sections (default: []) - dict with key->value pairs as section_name->SectionTitle 
        * book_contribution_date (default: None) - python datetime date
        * book_date_revised (default: None) - python datetime date
        * book_history (default: [])  - dictionary with key->value pairs as PubStatus -> python datetime
        * book_language (default: None) - string (e.g. "eng")
        * book_editors (default: []) - list containing names from 'editors' AuthorList
        * book_abstracts (default: []) - dict with key->value pairs as Label->AbstractText.text)
        * book_medium (default: None) - string (e.g. "Internet")
        * book_synonyms (default: None) - list of disease synonyms (applicable to "gene" book)
        * book_publication_status (default: None) - string (e.g. "ppublish")
    '''

    def __init__(self, xmlstr, *args, **kwargs):
        if xmlstr.find('<PubmedBookArticle>') > -1:
            super(PubMedArticle, self).__init__(xmlstr, 'PubmedBookArticle', args, kwargs)
            self.pubmed_type = 'book'
            self._root = 'BookDocument'
        else:
            super(PubMedArticle, self).__init__(xmlstr, 'PubmedArticle', args, kwargs)
            self.pubmed_type = 'article'
            self._root = 'MedlineCitation'

        pmt = self.pubmed_type
        
        # shared between book and article types:
        self.pmid = self._get_pmid()
        self.authors = self._get_authors() if pmt=='article' else self._get_book_authors()
        self.title = self._get_title() if pmt=='article' else self._get_book_articletitle()
        self.authors_str = self._get_authors_str()
        self.author1_last_fm = self._get_author1_last_fm()        
        self.author1_lastfm = self._get_author1_lastfm()
    
        # 'article' only (not shared):
        self.pages = None if pmt=='book' else self._get_pages()
        self.first_page = None if pmt=='book' else self._get_first_page()
        self.last_page = None if pmt=='book' else self._get_last_page()
        self.volume = None if pmt=='book' else self._get_volume()
        self.issue = None if pmt=='book' else self._get_issue()
        self.volume_issue = None if pmt=='book' else self._get_volume_issue()
        self.doi = None if pmt=='book' else self._get_doi()
        self.pii = None if pmt=='book' else self._get_pii()
        self.pmc = None if pmt=='book' else self._get_pmc()
        self.issn = None if pmt=='book' else self._get_issn()

        # 'book' only:
        self.book_accession_id = None if pmt=='article' else self._get_bookaccession_id()
        self.book_title = None if pmt=='article' else self._get_book_title()
        self.book_publisher = None if pmt=='article' else self._get_book_publisher()
        self.book_language = None if pmt=='article' else self._get_book_language()
        self.book_editors = None if pmt=='article' else self._get_book_editors()
        self.book_abstracts = None if pmt=='article' else self._get_book_abstracts()
        self.book_sections = None if pmt=='article' else self._get_book_sections()
        self.book_copyright = None if pmt=='article' else self._get_book_copyright()
        self.book_medium = None if pmt=='article' else self._get_book_medium()
        self.book_synonyms = None if pmt=='article' else self._get_book_synonyms()
        self.book_publication_status = None if pmt=='article' else self._get_book_publication_status()
        self.book_history = None if pmt=='article' else self._get_book_history()
        self.book_contribution_date = None if pmt=='article' else self._get_book_contribution_date()
        self.book_date_revised = None if pmt=='article' else self._get_book_contribution_date()

        # the shared oddballs, must be done last.
        self.abstract = self._get_abstract() if pmt=='article' else self._get_book_abstract()
        self.journal = self.book_title if pmt=='book' else self._get_journal()
        self.year = self._get_book_year() if pmt=='book' else self._get_year()


    def to_dict(self):
        outd = self.__dict__
        outd.pop('content')
        outd.pop('xmlstr')
        outd.pop('_root')
        return self.__dict__

    def _construct_datetime(self, d):
        names = ['Year', 'Month', 'Day']
        parts = {}
        for name in names:
            if d.find(name) is not None:
                parts[name.lower()] = d.find(name).text
        if 'day' in parts.keys() and 'month' in parts.keys():
            return datetime.strptime('{year}/{month}/{day}'.format(**parts), '%Y/%m/%d').date()
        elif 'month' in parts.keys() and 'year' in parts.keys():
            return datetime.strptime('{year}/{month}'.format(**parts), '%Y/%m').date()
        else:
            return datetime.strptime('{year}'.format(**parts), '%Y').date()

    def _get_bookaccession_id(self):
        for item in self.content.findall('BookDocument/ArticleIdList/ArticleId'):
            if item.get('IdType')=='bookaccession':
                return item.text

    def _get_book_title(self):
        return self._get('BookDocument/Book/BookTitle')

    def _get_book_articletitle(self):
        return self._get('BookDocument/ArticleTitle')

    def _get_book_authors(self):
        authors = [ _au_to_last_fm(au) for au in self.content.findall('BookDocument/AuthorList/Author') ]
        return authors

    def _get_book_publisher(self):
        return self._get('BookDocument/Book/Publisher/PublisherName')

    def _get_book_publisher_location(self):
        return self._get('BookDocument/Book/Publisher/PublisherLocation')

    def _get_book_language(self):
        return self._get('BookDocument/Language')

    def _get_book_editors(self):
        return [ _au_to_last_fm(au) for au in self.content.findall('BookDocument/Book/AuthorList/Author') ]

    def _get_book_abstracts(self):
        abd = {}
        for item in self.content.findall('BookDocument/Abstract/AbstractText'):
            abd[item.get('Label')] = item.text
        return abd

    def _get_book_sections(self):
        sections = {}
        for item in self.content.findall('BookDocument/Sections/Section'):
            sec_title = item.find('SectionTitle')
            sections[sec_title.get('sec')] = sec_title.text
        return sections

    def _get_book_abstract(self):
        abstract_strs = ['%s: %s' % (k,v) for k,v in self.book_abstracts.items()]
        return '\n'.join(abstract_strs)

    def _get_book_copyright(self):
        return self._get('BookDocument/Abstract/CopyrightInformation')

    def _get_book_medium(self):
        return self._get('BookDocument/Book/Medium')

    def _get_book_contribution_date(self):
        return self._construct_datetime(self.content.find('BookDocument/ContributionDate'))

    def _get_book_date_revised(self):
        return self._construct_datetime(self.content.find('BookDocument/DateRevised'))

    def _get_book_synonyms(self):
        syn_list = self.content.find('BookDocument/ItemList')
        if syn_list.get('ListType')=='Synonyms':
            return [item.text for item in self.content.findall('BookDocument/ItemList/Item')]
        else:
            return []

    def _get_book_history(self):
        history = {}
        items = self.content.findall('PubmedBookData/History/PubMedPubDate')
        for item in items:
            history[item.get('PubStatus')] = self._construct_datetime(item)
        return history

    def _get_book_publication_status(self):
        return self._get('PubmedBookData/PublicationStatus')

    def _get_book_year(self):
        return self.book_contribution_date.year

    def _get_pmid(self):
        return self._get(self._root+'/PMID')

    def _get_abstract(self):
        return self._get(self._root+'/Article/Abstract/AbstractText')

    def _get_authors(self):
        # N.B. Citations may have 0 authors. e.g., pmid:7550356
        authors = [ _au_to_last_fm(au) for au in self.content.findall(self._root+'/Article/AuthorList/Author') ]
        return authors

    def _get_authors_str(self):
        return '; '.join(self.authors) 

    def _get_author1_last_fm(self):
        '''return first author's name, in format Last INITS (space between surname and inits)'''
        #return _au_to_last_fm(self.content.find(self._root+'/Article/AuthorList/Author'))
        if self.authors:
            return self.authors[0]
        else:
            return None

    def _get_author1_lastfm(self):
        '''return first author's name, in format LastINITS'''
        if self.author1_last_fm is not None:
            return self.author1_last_fm.replace(' ','')
        return None

    def _get_journal(self):
        j = self._get(self._root+'/Article/Journal/ISOAbbreviation')
        if j is None:
            # e.g., http://www.ncbi.nlm.nih.gov/pubmed?term=21242195
            j = self._get(self._root+'/Article/Journal/Title')
        assert j is not None
        return j

    def _get_pages(self):
        return self._get(self._root+'/Article/Pagination/MedlinePgn') 

    def _get_first_page(self):
        try:
            return self.pages.split('-')[0]
        except AttributeError:
            return self.pages

    def _get_last_page(self):
        #TODO: return true last page in situations like self.pages = "148-52"
        #           i.e. we want last_page = "152", not "52"
        #if lastnum < self.first_page:
        #    len(lastnum)....
        try:
            lastnum = self.pages.split('-')[1]
            return lastnum
        except (IndexError, AttributeError):
            return None

    def _get_title(self):
        return self._get(self._root+'/Article/ArticleTitle') 

    def _get_volume(self):
        try:
            return self.content.find(self._root+'/Article/Journal/JournalIssue/Volume').text
        except AttributeError:
            return None

    def _get_issue(self):
        try:
            return self.content.find(self._root+'/Article/Journal/JournalIssue/Issue').text
        except AttributeError:
            return None

    def _get_volume_issue(self):
        ji = self.content.find(self._root+'/Article/Journal/JournalIssue')
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
        return None

    def _get_pubdate(self):
        return self._compose_datetime(self.content.find(self._root+'/Article/Journal/JournalIssue/PubDate'))

    def _get_year(self):
        y = self._get(self._root+'/Article/Journal/JournalIssue/PubDate/Year')
        if y is None:
            # case applicable for pmid:9887384 (at least)
            y = self._get(self._root+'/Article/Journal/JournalIssue/PubDate/MedlineDate')[0:4]
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

    def _get_issn(self):
        return self._get(self._root+'/Article/Journal/ISSN')
    
    def __str__(self):
        if self.pubmed_type == 'article':
            return( '%s (%s. %s, %s:%s)' % (
                 self.title, self.authors_str, self.journal, self.volume_issue, self.pages) )
        else:
            return( '%s (%s. %s, %s)' % (self.title, self.authors_str, self.book_title, self.year))


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


