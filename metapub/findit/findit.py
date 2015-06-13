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

import requests

from ..pubmedfetcher import PubMedFetcher
from ..pubmedarticle import square_voliss_data_for_pma
from ..convert import PubMedArticle2doi_with_score, doi2pmid
from ..exceptions import MetaPubError, AccessDenied, NoPDFLink
from ..text_mining import re_numbers
from ..utils import asciify

from .journal_formats import *
from .dances import *
from .journal_cantdo_list import JOURNAL_CANTDO_LIST

fetch = PubMedFetcher()

paywall_reason_template = '%s behind %s paywall'  # % (journal, publisher)

def find_article_from_pma(pma, use_crossref=True, use_paywalls=False):
    '''The real workhorse of FindIt.

        Based on the contents of the supplied PubMedArticle object, this function
        returns the best possible download link for a Pubmed PDF.

        Returns (url, reason) -- url being self-explanatory, and "reason" containing
        any qualifying message about why the url came back the way it did.

        Reasons may include (but are not limited to):

            "DOI missing from PubMedArticle and CrossRef lookup failed."
            "pii missing from PubMedArticle XML"
            "No URL format for Journal %s"
            "TODO format"

        :param: (pma PubMedArticle object) 
        :param: use_crossref (bool) default: True
        :param: use_paywalls (bool) default: False [not yet implemented]
        :return: (url, reason)
    '''
    reason = None
    url = None

    # protect against unicode character mishaps in journal names.
    # (did you know that unicode.translate takes ONE argument whilst str.translate takes TWO?! true story)
    jrnl = asciify(pma.journal).translate(None, '.')

    if pma.pmc:
        try:
            url = the_pmc_twist(pma)
            return (url, None)
        except Exception, e:
            reason = str(e)

    if jrnl in simple_formats_pii.keys():
        # TODO: find a smarter way to process these (maybe just break them out into publishers)
        if pma.pii:
            url = simple_formats_pii[jrnl].format(a=pma)
            reason = ''
        elif pma.doi:
            try:
                url = the_doi_2step(pma.doi)
            except MetaPubError, e:
                reason = '%s' % e
        else:
            url = None
            reason = 'pii missing from PubMedArticle XML and DOI lookup failed. Harsh!'

        if url:
            r = requests.get(url)
            if r.text.find('Access Denial') > -1:
                url = None
                reason = 'Access Denied by ScienceDirect'

    elif jrnl in simple_formats_doi.keys():
        if pma.doi:
            url = simple_formats_doi[jrnl].format(a=pma)
            reason = ''

    #elif jrnl in doi2step_journals:
    #    if pma.doi:
    #        try:
    #            baseurl = the_doi_2step(pma.doi)
    #            url = baseurl.replace('full', 'pdf').replace('html', 'pdf')
    #            reason = ''
    #        except Exception, e:
    #            reason = '%s' % e

    elif jrnl in jstage_journals:
        if pma.doi:
            try:
                url = the_jstage_dive(pma)
            except Exception, e:
                reason = str(e)

    elif jrnl.find('BMC')==0 or jrnl in BMC_journals:
        # Many Biomed Central journals start with "BMC", but many more don't.
        try:
            url = the_biomed_calypso(pma)
        except Exception, e:
            reason = str(e)
            
    elif jrnl in wiley_journals:
        if pma.doi:
            try:
                url = the_wiley_shuffle(pma)
            except Exception, e:
                reason = str(e)

    elif jrnl in jama_journals:
        try:
            url = the_jama_dance(pma)
        except Exception, e:
            reason = str(e)

    elif jrnl in vip_journals.keys(): 
        pma = square_voliss_data_for_pma(pma)
        if pma.volume and pma.issue:
            url = vip_format.format(host=vip_journals[jrnl]['host'], a=pma)
        else:
            # TODO: try the_doi_2step
            reason = 'volume and maybe also issue data missing from PubMedArticle'

    elif jrnl in aaas_journals.keys():
        pma = square_voliss_data_for_pma(pma)
        try:
            url = the_aaas_tango(pma)
        except Exception, e:
            reason = str(e)

    elif jrnl in spandidos_journals.keys():
        pma = square_voliss_data_for_pma(pma)
        if pma.volume and pma.issue:
            url = spandidos_format.format(ja=spandidos_journals[jrnl]['ja'], a=pma)
        else:
            # TODO: try the_doi_2step
            reason = 'volume and maybe also issue data missing from PubMedArticle'

    elif jrnl in jci_journals:
        try:
            url = the_jci_polka(pma)
        except Exception, e:
            reason = str(e)

    elif jrnl in nature_journals.keys():
        try:
            url = the_nature_ballet(pma)
        except Exception, e:
            reason = str(e)

    elif jrnl in cell_journals.keys():
        if pma.pii:
            # the front door
            url = cell_format.format( a=pma, ja=cell_journals[jrnl]['ja'],
                    pii=pma.pii.translate(None,'-()') )
        #elif pma.doi:
            # the side door
        #    try:
        #        baseurl = the_doi_2step(pma.doi)
        #        url = baseurl.replace('full', 'pdf').replace('html', 'pdf')
        #        reason = ''
        #    except Exception, e:
        #        reason = '%s' % e
        else:
            #reason = 'pii missing from PubMedArticle XML (%s in Cell format) and no DOI either (harsh!)' % jrnl
            reason = 'pii missing from PubMedArticle XML (%s in Cell format)' % jrnl

    elif jrnl.find('Lancet') > -1:
        try:
            url = the_lancet_tango(pma)
        except Exception, e:
            reason = str(e)

    elif jrnl in sciencedirect_journals:
        try:
            url = the_sciencedirect_disco(pma)
        except Exception, e:
            reason = str(e)

    elif jrnl in paywall_journals:
        if use_paywalls:
            reason = '%s behind paywall; not yet smart enough to navigate paywalls, sorry!' % jrnl
        else:
            reason = '%s behind paywall' % jrnl

    elif jrnl in todo_journals:
        reason = 'TODO format -- example: %s' % todo_journals[jrnl]['example']

    elif jrnl in JOURNAL_CANTDO_LIST:
        reason = 'CANTDO: this journal is in the "can\'t do" list (see metapub/findit/journal_cantdo_list.py)'

    else:
        reason = 'No URL format for Journal %s' % jrnl

    return (url, reason)


def find_article_from_doi(doi):
    '''pull a PubMedArticle based on CrossRef lookup (using doi2pmid),
    then run it through find_article_from_pma.

        :param: doi (string)
        :return: (url, reason)
    '''
    pma = fetch.article_by_pmid(doi2pmid(doi))
    return find_article_from_pma(pma)


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
        self.use_crossref = kwargs.get('use_crossref', True)
        self.use_paywalls = kwargs.get('use_paywalls', False)
        self.doi_min_score = kwargs.get('doi_min_score', 2.3)
        self.tmpdir = kwargs.get('tmpdir', '/tmp')
        self.doi_score = None
        self.pma = None

        if self.pmid:
            self._load_pma_from_pmid()
        elif self.doi:
            self._load_pma_from_doi()
        else:
            raise MetaPubError('Supply either a pmid or a doi to instantiate. e.g. FindIt(pmid=1234567)')

        try:
            self.url, self.reason = find_article_from_pma(self.pma, use_paywalls=self.use_paywalls) 
        except requests.exceptions.ConnectionError, e:
            self.url = None
            self.reason = 'tx_error: %r' % e

    def _load_pma_from_pmid(self):
        self.pma = fetch.article_by_pmid(self.pmid)
        if self.pma.doi:
            self.doi_score==10.0
        
        if self.pma.doi==None:
            if self.use_crossref:
                self.pma.doi, self.doi_score = PubMedArticle2doi_with_score(self.pma, min_score=self.doi_min_score)
                if self.pma.doi == None:
                    self.reason = 'DOI missing from PubMedArticle and CrossRef lookup failed.'
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


