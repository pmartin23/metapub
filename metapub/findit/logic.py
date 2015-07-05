from __future__ import absolute_import, print_function

'''findit/logic.py

        The get_pdf_from_pma function selects possible PDF links for the
        given article represented in a PubMedArticle object.

        These links are built (not crawled) by selecting a likely-to-work URL
        pattern based on the NLM journal name abbreviation taken from the
        PubMedArticle object.

        It's recommended to use the FindIt object as the primary interface
        to this code.

        See the find_article_from_pma docstring for more info.

        *** IMPORTANT NOTE ***

        In many cases, this code performs intermediary HTTP requests in order to
        scrape a PDF url out of a page, and sometimes tests the url to make sure
        that what's being sent back is in fact a PDF.

        NO PDF DOWNLOAD IS PERFORMED; however some websites will block your IP
        address when you are performing several information lookups within a
        relatively short span of time (e.g. informa blocks if 25 HTTP connections
        are made within 5 minutes).

        If you would like these requests to go through a proxy (e.g. if you would
        like to prevent making multiple requests of the same servers, which may have
        effects like getting your IP shut off from PubMedCentral), set the
        HTTP_PROXY environment variable in your code or on the command line before
        using any FindIt functionality.
'''

__author__ = 'nthmost'

import requests, os

from ..pubmedfetcher import PubMedFetcher
from ..pubmedarticle import square_voliss_data_for_pma
from ..convert import doi2pmid
from ..utils import asciify
from ..exceptions import MetaPubError

from .journal_formats import *
from .dances import *
from .journal_cantdo_list import JOURNAL_CANTDO_LIST

def find_article_from_pma(pma, use_nih=False):
    '''The real workhorse of FindIt.

        Based on the contents of the supplied PubMedArticle object, this function
        returns the best possible download link for a Pubmed PDF.

        Be aware that this function no longer performs doi lookups; if you want
        this handled for you, use the FindIt object (which will also record the
        doi score from the lookup for you).

        Returns (url, reason) -- url being self-explanatory, and "reason" containing
        any qualifying message about why the url came back the way it did.

        Reasons may include (but are not limited to):

            "DOI missing from PubMedArticle and CrossRef lookup failed."
            "pii missing from PubMedArticle XML"
            "No URL format for Journal %s"
            "TODO format"

        Optional params:
            use_nih      -- source PubmedCentral articles from nih.gov (NOT recommended)

        :param: (pma PubMedArticle object)
        :param: use_nih (bool) default: False
        :return: (url, reason)
    '''
    reason = ''
    url = None

    # protect against unicode character mishaps in journal names.
    # (did you know that unicode.translate takes ONE argument whilst
    #   str.translate takes TWO?! true story)
    jrnl = asciify(pma.journal).translate(None, '.')

    ##### Pubmed Central: ideally we get the article from PMC if it has a PMC id.
    #
    #   Note: we're using europepmc.org rather than nih.gov (see the_pmc_twist function).
    #
    #   If we can't get the article from a PMC site, it may be that the paper is
    #   temporarily embargoed.  In that case, we may be able to fall back on retrieval
    #   from a publisher link.

    if pma.pmc:
        try:
            url = the_pmc_twist(pma, use_nih)
            return (url, None)
        except MetaPubError as error:
            reason = str(error)

    if jrnl in simple_formats_pii.keys():
        #TODO: move to dances
        if pma.pii:
            url = simple_formats_pii[jrnl].format(a=pma)
            reason = ''
        else:
            url = None
            reason = 'MISSING: pii missing from PubMedArticle XML (pii format)'

        if url:
            res = requests.get(url)
            if res.text.find('Access Denial') > -1:
                url = None
                reason = 'DENIED: Access Denied by ScienceDirect'
            #TODO: handle other types of broken conditions here.

    elif jrnl in simple_formats_pmid.keys():
        url = simple_formats_pmid[jrnl].format(pmid=pma.pmid)
        return (url, None)

    elif jrnl in simple_formats_doi.keys():
        if pma.doi:
            url = simple_formats_doi[jrnl].format(a=pma)
            reason = ''

    elif jrnl in vip_journals.keys():
        pma = square_voliss_data_for_pma(pma)
        if pma.volume and pma.issue:
            url = vip_format.format(host=vip_journals[jrnl]['host'], a=pma)
        else:
            # TODO: try the_doi_2step
            reason = 'MISSING: vip (volume and maybe also issue data missing from PubMedArticle)'

    elif jrnl in vip_journals_nonstandard.keys():
        pma = square_voliss_data_for_pma(pma)
        url = vip_journals_nonstandard[jrnl].format(a=pma)
        if url.find('None') > -1:
            # TODO: try the_doi_2step
            reason = 'MISSING: vip (volume or issue or page data missing from PubMedArticle)'
            url = None

    if url:
        return (url, reason)

    ##### PUBLISHER BASED LISTS #####

    if jrnl in jstage_journals:
        if pma.doi:
            try:
                url = the_jstage_dive(pma)
            except MetaPubError as error:
                reason = str(error)

    elif jrnl.find('BMC') == 0 or jrnl in BMC_journals:
        # Many Biomed Central journals start with "BMC", but many more don't.
        try:
            url = the_biomed_calypso(pma)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in springer_journals:
        if pma.doi:
            try:
                url = the_springer_shag(pma)
            except MetaPubError as error:
                reason = str(error)

    elif jrnl in wiley_journals:
        if pma.doi:
            try:
                url = the_wiley_shuffle(pma)
            except MetaPubError as error:
                reason = str(error)

    elif jrnl in jama_journals:
        try:
            url = the_jama_dance(pma)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in aaas_journals.keys():
        pma = square_voliss_data_for_pma(pma)
        try:
            url = the_aaas_tango(pma)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in spandidos_journals.keys():
        pma = square_voliss_data_for_pma(pma)
        if pma.volume and pma.issue:
            url = spandidos_format.format(ja=spandidos_journals[jrnl]['ja'], a=pma)
        else:
            # TODO: try the_doi_2step
            reason = 'MISSING: vip - volume and maybe also issue data missing from PubMedArticle'

    elif jrnl in jci_journals:
        try:
            url = the_jci_polka(pma)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in biochemsoc_journals.keys():
        pma = square_voliss_data_for_pma(pma)
        if pma.volume and pma.issue:
            host = biochemsoc_journals[jrnl]['host']
            url = biochemsoc_format.format(a=pma, host=host, ja=biochemsoc_journals[jrnl]['ja'])
        else:
            reason = 'MISSING: vip - volume and maybe also issue data missing from PubMedArticle'

    elif jrnl in nature_journals.keys():
        try:
            url = the_nature_ballet(pma)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in cell_journals.keys():
        if pma.pii:
            # the front door
            url = cell_format.format(a=pma, ja=cell_journals[jrnl]['ja'],
                                     pii=pma.pii.translate(None, '-()'))
        else:
            reason = 'MISSING: pii missing from PubMedArticle XML (%s in Cell format)' % jrnl

    elif jrnl.find('Lancet') > -1:
        try:
            url = the_lancet_tango(pma)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in sciencedirect_journals:
        try:
            url = the_sciencedirect_disco(pma)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in karger_journals:
        try:
            url = the_karger_conga(pma)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in paywall_journals:
        reason = 'PAYWALL: this journal has been marked in a list as "never free"'

    elif jrnl in todo_journals:
        reason = 'TODO: format example: %s' % todo_journals[jrnl]['example']

    elif jrnl in JOURNAL_CANTDO_LIST:
        reason = 'CANTDO: this journal has been marked as being abandonware / unsourceable'

    # aka if url is STILL None...
    if not url and not reason:
        reason = 'NOFORMAT: No URL format for Journal %s' % jrnl

    return (url, reason)


def find_article_from_doi(doi, use_nih=False):
    '''pull a PubMedArticle based on CrossRef lookup (using doi2pmid),
    then run it through find_article_from_pma.

        :param: doi (string)
        :return: (url, reason)
    '''
    fetch = PubMedFetcher()
    pma = fetch.article_by_pmid(doi2pmid(doi))
    return find_article_from_pma(pma, use_nih=use_nih)

