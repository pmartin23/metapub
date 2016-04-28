from __future__ import absolute_import, unicode_literals, print_function

import re
import six

import requests

#py3k / py2k compatibility
if six.PY2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse

from ..text_mining import (find_doi_in_string, get_nature_doi_from_link, scrape_doi_from_article_page,
                           get_biomedcentral_doi_from_link)
from ..pubmedfetcher import PubMedFetcher
from ..crossref import CrossRef
from ..convert import doi2pmid, pmid2doi, interpret_pmids_for_citation_results
from ..pubmedcentral import get_pmid_for_otherid

from .hostname2jrnl import HOSTNAME_TO_JOURNAL_MAP
from .hostname2doiprefix import HOSTNAME_TO_DOI_PREFIX_MAP

# VIP (volume-issue-page)
re_vip = re.compile('(?P<hostname>.*?)\/content(\/\w+)?\/(?P<volume>\d+)\/(?P<issue>\d+)\/(?P<first_page>\d+)', re.I)

# PMID in url
re_pmidlookup = re.compile('.*?(\?|&)pmid=(?P<pmid>\d+)', re.I)
re_pubmed_pmid = re.compile('.*?ncbi.nlm.nih.gov\/pubmed\/(?P<pmid>\d+)')

# PMCID in url
re_pmcid = re.compile('.*?(?P<hostname>ncbi.nlm.nih.gov|europepmc.org)\/.*?(?P<pmcid>PMC\d+)', re.I)

# PII
pii_official = '(?P<pii>S\d{4}-\d{4}\(\d{2}\)\d{5}-\d{1})'
re_sciencedirect_pii_simple = re.compile('.*?(?P<hostname>sciencedirect\.com)\/science\/article\/pii\/(?P<pii>S\d+)', re.I)
re_sciencedirect_pii_official = re.compile('.*?(?P<hostname>sciencedirect\.com)\/science\/article\/pii\/' + pii_official, re.I)
re_cell_pii_simple = re.compile('.*?(?P<hostname>cell\.com)\/(?P<journal_abbrev>.*?)\/(pdf|abstract|fulltext)\/(?P<pii>S\d+)', re.I)
re_cell_pii_official = re.compile('.*?cell.com\/((?P<journal_abbrev>.*?)\/)?(pdf|abstract|fulltext)\/' + pii_official, re.I)
re_cell_old_style = re.compile('.*?(?P<hostname>cell\.com)\/(pdf|abstract|fulltext)\/(?P<pii>\d+)', re.I)

# Unique
re_jstage = re.compile('.*?(?P<hostname>jstage\.jst\.go\.jp)\/article\/(?P<journal_abbrev>.*?)\/(?P<volume>\d+)\/(?P<issue>.*?)\/(?P<info>).*?\/', re.I)
re_jci = re.compile('.*?(?P<hostname>jci\.org)\/articles\/view\/(?P<jci_id>\d+)', re.I)
re_karger = re.compile('.*?(?P<hostname>karger\.com)\/Article\/(Abstract|Pdf)\/(?P<kid>\d+)', re.I)

# Early release formats
re_early_release = re.compile('((http|https)(:\/\/))(?P<hostname>.*?)\/content\/early\/(?P<year>\d+)\/(?P<month>\d+)\/(?P<day>\d+)\/(?P<doi_suffix>.*?)(\.full|\.pdf)')

OFFICIAL_PII_FORMAT = '{pt1}-{pt2}({pt3}){pt4}-{pt5}'

FETCH = PubMedFetcher()
CRX = CrossRef()


def get_karger_doi_from_link(url):
    """ Karger IDs can be found in the URL after the "PDF" or "Abstract" piece, and used to 
    compose a DOI by prepending enough zeroes to make a 9-digit number. The Karger publisher
    ID is 10.1159

    e.g.
       https://www.karger.com/Article/Abstract/329047 --> 10.1159/000329047
       https://www.karger.com/Article/Abstract/83388 --> 10.1159/000083388

    :param url: (str)
    :return: doi or None
    """
    out = '10.1159/'
    match = re_karger.match(url)
    if match:
        kid = match.groupdict()['kid']
        num_zeroes_needed = 9 - len(kid)
        return out + '0'*num_zeroes_needed + kid
    else:
        return None


def get_jstage_doi_from_link(url):
    """ Since the jstage urls are composed with some degree of unpredictability with respect to
    what's found in segment that ought to contain the first_page element, we have to load the _article
    page (if we can) and try to extract the DOI.

    :param url: (str)
    :return: doi or None
    """
    match = re_jstage.match(url)
    if match:
        if url.find('_pdf') > -1:
            url = url.replace('_pdf', '_article')
        return scrape_doi_from_article_page(url)


def get_sciencedirect_doi_from_link(url):
    """ We can extract the PII from most sciencedirect links. To get a DOI, we may be able to 
    simply append the PII to the publisher code "10.1016/", or we may have to inject the special
    character separaters into the PII numbers.

    Example:
        http://www.sciencedirect.com/science/article/pii/S0094576599000673

        PII = S0094576599000673
        DOI = 10.1016/S0094-5765(99)00067-3

    :param url: (str)
    :return: doi or None
    """
    out = '10.1016/'

    try:
        pii = re_sciencedirect_pii_simple.match(url).groupdict()['pii']
        pii = OFFICIAL_PII_FORMAT.format(pt1=pii[:5], pt2=pii[5:9], pt3=pii[9:11], pt4=pii[11:16], pt5=pii[16])
    except AttributeError:
        try:
            pii = re_sciencedirect_pii_official.match(url).groupdict()['pii']
        except AttributeError:
            return None    
    return out + pii


def get_cell_doi_from_link(url):
    """ Cell and ScienceDirect links have similar properties, but there are several different url
    types for Cell abstracts and PDFs (much like biomedcentral).

    Examples:
        http://www.cell.com/pdf/0092867480906212.pdf --> 10.1016/0092-8674(80)90621-2
        http://www.cell.com/cancer-cell/pdf/S1535610806002844.pdf --> 10.1016/j.ccr.2006.09.010
        http://www.cell.com/molecular-cell/abstract/S1097-2765(00)80321-4 --> 10.1016/S1097-2765(00)80321-4
        http://www.cell.com/current-biology/fulltext/S0960-9822%2816%2930170-1 --> 10.1016/j.cub.2016.03.002

    :param url: (str)
    :return: doi or None
    """
    out = '10.1016/'
    pii = ''

    # Try "official" pii format first
    match = re_cell_pii_official.match(url)
    if match:
        pii = match.groupdict()['pii']

    else:
        # Try "simple" (no punctuation) pii formats.
        match = re_cell_pii_simple.match(url)
        if match:
            pii = match.groupdict()['pii']
            pii = OFFICIAL_PII_FORMAT.format(pt1=pii[:5], pt2=pii[5:9], pt3=pii[9:11], pt4=pii[11:16], pt5=pii[16])

        else:
            # Try "old style" (has no "S" in front).
            match = re_cell_old_style.match(url)
            if match:
                pii = match.groupdict()['pii']
                pii = OFFICIAL_PII_FORMAT.format(pt1=pii[:4], pt2=pii[4:8], pt3=pii[8:10], pt4=pii[10:15], pt5=pii[15])

    if match:
        journal_abbrev = match.groupdict().get('journal_abbrev', None)
        if journal_abbrev and journal_abbrev in ['cancer-cell', 'current-biology']:
            return scrape_doi_from_article_page(url)

        return out + pii

    return None


def get_jci_doi_from_link(url):
    """ Journal of Clinical Investigation (JCI) links have a numerical ID that can be used to 
    reconstruct the article's DOI.

    Example:
        https://www.jci.org/articles/view/32496 --> 10.1172/JCI32496
       
    :param url: (str)
    :return: doi or None 
    """
    out = '10.1172/JCI'
    match = re_jci.match(url)
    if match:
        return out + match.groupdict()['jci_id']
    else:
        return None


def get_ahajournals_doi_from_link(url):
    """ If this is an ahajournals.org journal, we should be able to compose a DOI using the publisher base
    of 10.1161 and pieces of the URL identifying the article.

    Example:
        http://circimaging.ahajournals.org/content/suppl/2013/04/02/CIRCIMAGING.112.000333.DC1/000333_Supplemental_Material.pdf
                --> 10.1161/CIRCIMAGING.112.000333

    :param url: (str)
    :return: doi or None
    """


def get_early_release_doi_from_link(url):
    """

    Examples:
        http://cancerres.aacrjournals.org/content/early/2015/12/30/0008-5472.CAN-15-0295.full.pdf --> 10.1158/0008-5472.CAN-15-0295
        http://ajcn.nutrition.org/content/early/2016/04/20/ajcn.115.123752.abstract --> 10.3945/ajcn.115.123752
        http://www.mcponline.org/content/early/2016/04/25/mcp.O115.055467.full.pdf+html --> 10.1074/mcp.O115.055467

    :param url: (str)
    :return: doi or None
    """

    match = re_early_release.match(url)
    if match:
        if match['hostname'] in HOSTNAME_TO_DOI_PREFIX_MAP.keys():
            return HOSTNAME_TO_DOI_PREFIX_MAP['hostname'] + '/' + match['doi']




def try_vip_methods(url):
    """ Many URLs follow the "volume-issue-page" format. If this URL is one of them, this function will return
    a dictionary containing at least the volume, issue, and first_page aspects of this article. The 'jtitle'
    key may or may not be filled in depending on whether metapub is aware of this journal's domain name.

    See metapub/urlreverse/hostname2journal.py for the list of supported journals (and please consider 
    contributing to the list if you can).

    :param url: (str)
    :return: dict or None
    """
    match = re_vip.match(url)

    if match:
        jrnl = get_journal_name_from_url(url)
        vipdict = match.groupdict()
        vipdict.update({'format': 'vip', 'jtitle': jrnl})
        return vipdict

    return None


def get_generic_doi_from_link(url):
    """ Covers many publisher URLs such as wiley and springer.

    Examples:
        http://onlinelibrary.wiley.com/doi/10.1111/j.1582-4934.2011.01476.x/full --> 10.1111/j.1582-4934.2011.01476.x
        link.springer.com/article/10.1186/1471-2164-7-243 --> 10.1186/1471-2164-7-243

    :param url: (str)
    :return: doi or None
    """
    doi = find_doi_in_string(url)
    if doi:
        # remove common addenda that may have come from the regular expression.
        for addendum in ['/full', '/asset', '/pdf', '.pdf']:
            place = doi.find(addendum)
            if place > -1:
                doi = doi[:place]
    return doi


DOI_METHODS = [get_cell_doi_from_link,
               get_jstage_doi_from_link,
               get_early_release_doi_from_link,
               get_biomedcentral_doi_from_link,
               get_nature_doi_from_link,
               get_sciencedirect_doi_from_link,
               get_karger_doi_from_link,
               get_generic_doi_from_link,
               ]


def try_doi_methods(url):
    """ Tries every "get_*_doi_from_link" method registered in DOI_METHODS and returns a doi
    when/if it finds one. As a last resort, uses find_doi_in_string(url), which may work in cases
    where the DOI can be parsed directly out of the URL.

    :param url: (str)
    :return: {'doi': <doi>, 'method': <method>} or None
    """
    for method in DOI_METHODS:
        doi = method(url)
        if doi:
            return {'doi': doi, 'method': method}
    return None


def try_pmid_methods(url):
    """ Attempts to get the PMID directly out of the URL.

    Examples:
        http://www.ncbi.nlm.nih.gov/pubmed/22253870 --> 22253870
        http://aac.asm.org/cgi/pmidlookup?view=long&pmid=7689822 --> 7689822

    :param url: (str)
    :return: pmid or None
    """
    match = re_pmidlookup.match(url)
    if match:
        return match.groupdict()['pmid']

    match = re_pubmed_pmid.match(url)
    if match:
        return match.groupdict()['pmid']


def get_article_info_from_url(url):
    """ Using regular expressions, attempt to determine the "format" of the submitted URL, and if 
    possible, extract useful information from the URL for article lookup by ID or citation.

    Possible results:
        'vip': volume-issue-page --> {'format': 'vip', 'volume': <V>, 'issue': <I>, 'first_page': <P>, 'jtitle': <jrnl>}
        'doi': has doi in the url --> {'format': 'doi', 'doi': <DOI>, 'method': <get_doi_function>}
        'pmid': has pmid in the url --> {'format': 'pmid', 'pmid': <PMID>}
        'pmcid': has PMC id in the url --> {'format': 'pmcid': 'pmcid': <PMCID>}

    If none of the available methods work to parse the URL, the result dictionary will be:
        {'format': 'unknown'}

    :param url:
    :return: result dictionary (see above)
    """
    # maybe the DOI is deducible from the URL:
    doidict = try_doi_methods(url)
    if doidict:
        doidict['format'] = 'doi'
        return doidict

    # maybe the pubmed ID is in the URL:
    pmid = try_pmid_methods(url)
    if pmid:
        outd = {'pmid': pmid, 'format': 'pmid'}
        return outd

    # maybe the PubmedCentral ID is in the URL:
    #if 'nih.gov' in url or 'europepmc.org' in url:
    match = re_pmcid.match(url)
    if match:
        outd = match.groupdict()
        outd['format'] = 'pmcid'
        return outd

    # maybe this is a volume-issue-page formatted link and we can look it up by citation or CrossRef:
    vipdict = try_vip_methods(url)
    if vipdict:
        vipdict['format'] = 'vip'
        return vipdict

    return {'format': 'unknown'}


def get_journal_name_from_url(url):

    if not url.startswith('http'):
        url = 'http://' + url

    hostname = urlparse(url).hostname
    if hostname.startswith('www'):
        hostname = hostname.replace('www.', '')

    if hostname in HOSTNAME_TO_JOURNAL_MAP.keys():
        return HOSTNAME_TO_JOURNAL_MAP[hostname]
    else:
        return None


class UrlReverse(object):

    def __init__(self, url, title=''):
        self.url = url
        self.title = title

        self.pmid = None
        self.doi = None

        self.info = get_article_info_from_url(url)
        self.format = self.info['format']

        if self.format == 'pmid':
            self.pmid = self.info['pmid']
            #self.doi = pmid2doi(self.pmid)

        elif self.format == 'doi':
            self.doi = self.info['doi']
            self.pmid = doi2pmid(self.doi)

        elif self.format == 'vip':
            self._try_citation_methods()

        elif self.format == 'pmcid':
            self.pmid = get_pmid_for_otherid(self.info['pmcid'])
            self.doi = doi2pmid(self.pmid)

    def to_dict(self):
        return self.__dict__

    def _try_citation_methods(self):
        # 1) try pubmed citation match.
        pmids = FETCH.pmids_for_citation(**self.info)
        pmid = interpret_pmids_for_citation_results(pmids)
        if pmid and pmid != 'AMBIGUOUS':
            # print('got PMID from citation')
            self.pmid = pmid
            self.doi = pmid2doi(pmid)
            return

        # 2) try CrossRef -- most effective when title available, but may work without it.
        results = CRX.query(self.title, params=self.info)
        if results:
            top_result = CRX.get_top_result(results, CRX.last_params)

        # we may have disqualified all the results at this point as being irrelevant, so we have to test here.
        if top_result:
            pmids = FETCH.pmids_for_citation(**top_result['slugs'])
            pmid = interpret_pmids_for_citation_results(pmids)
            if pmid and pmid != 'AMBIGUOUS':
                self.pmid = pmid
                self.doi = find_doi_in_string(top_result['doi'])
