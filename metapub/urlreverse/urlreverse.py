from __future__ import absolute_import, unicode_literals

import re

import requests

from ..text_mining import (find_doi_in_string, get_nature_doi_from_link, 
                            get_biomedcentral_doi_from_link, findall_dois_in_text)

from .hostname2jrnl import HOSTNAME_TO_JOURNAL_MAP

pii_official = '(?P<pii>S\d+-\d+\(\d+\)\d+-\d)'

re_vip = re.compile('.*?\/(?P<volume>\d+)\/(?P<issue>\d+)\/(?P<first_page>\d+)')
re_pmid = re.compile('.*?\?pmid=(?P<pmid>\d+)')
re_jstage = re.compile('.*?jstage.jst.go.jp\/article\/(?P<journal_abbrev>.*?)\/(?P<volume>\d+)\/(?P<issue>.*?)\/(?P<info>).*?\/')
re_sciencedirect_pii_simple = re.compile('.*?(sciencedirect|cell).com\/science\/article\/pii\/(?P<pii>S\d+)')
re_sciencedirect_pii_official = re.compile('.*?(sciencedirect|cell).com\/science\/article\/pii\/' + pii_official)
re_jci = re.compile('.*?jci.org\/articles\/view\/(?P<jci_id>\d+)')
re_karger = re.compile('.*?karger.com\/Article\/(Abstract|Pdf|PDF)\/(?P<kid>\d+)')

re_cell_pii_simple = re.compile('.*?cell.com\/(\w+\/)?(pdf|abstract)\/(?P<pii>S\d+)')
re_cell_pii_official = re.compile('.*?cell.com\/(\w+\/)?(pdf|abstract)\/' + pii_official)

OFFICIAL_PII_FORMAT = '{pt1}-{pt2}({pt3}){pt4}-{pt5}'



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

        response = requests.get(url)
        dois = findall_dois_in_text(response.text)
        if dois:
            return dois[0]
        else:
            return None


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

    :param url: (str)
    :return: doi or None
    """
    out = '10.1016/'
    match = re_cell_pii_simple.match(url)
    if match:
        pii = OFFICIAL_PII_FORMAT.format(pt1=pii[:5], pt2=pii[5:9], pt3=pii[9:11], pt4=pii[11:16], pt5=pii[16])

    else:
        match = re_cell_pii_official.match(url)
        if match:
            pii = match.groupdict()['pii']
        else:
            return None
    return out + pii


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
        return match.groupdict().update({'format': 'vip', 'jtitle': jrnl})
    return None
    

DOI_METHODS = [get_biomedcentral_doi_from_link, 
               get_nature_doi_from_link,
               get_sciencedirect_doi_from_link,
               get_karger_doi_from_link,
               get_jstage_doi_from_link,
               get_cell_doi_from_link,
              ]


def try_doi_methods(url):
    """ Tries every "get_*_doi_from_link" method registered in DOI_METHODS and returns a doi
    when/if it finds one. As a last resort, uses find_doi_in_string(url), which may work in cases
    where the DOI can be parsed directly out of the URL.

    :param url: (str)
    :return: doi or None
    """

    doi = find_doi_in_string(url)
    if doi:
        # remove common addenda that may have come from the regular expression.
        for addendum in ['/full', '/asset']:
            place = doi.find(addendum)
            if place > -1:
                doi = doi[:place]

        doi = doi.replace('/full', '')

    else:
        for method in DOI_METHODS:
            doi = method(url)
    return doi


def get_article_info_from_url(url):
    """ Using regular expressions, attempt to determine the "format" of the submitted URL, and if 
    possible, extract useful information from the URL for article lookup by ID or citation.

    Possible results:
        'vip': volume-issue-page --> {'format': 'vip', 'volume': <V>, 'issue': <I>, 'first_page': <P>, 'jtitle': <jrnl>}
        'doi': has doi in the url --> {'format': 'doi', 'doi': <DOI>}
        'pmid': has pmid in the url --> {'format': 'pmid', 'pmid': <PMID>}

    If none of the available methods work to parse the URL, the result dictionary will be:
        {'format': 'unknown'}

    :param url:
    :return: result dictionary (see above)
    """
    doi = try_doi_methods(url)
    if doi:
        return {'format': 'doi', 'doi': doi}

    match = re_pmid.match(url)
    if match:
        return match.groupdict().update({'format': 'pmid'})

    vipdict = try_vip_methods(url)
    if vipdict:
        return vipdict.update({'format': 'vip'})

    return {'format': 'unknown'}


def get_journal_name_from_url(url):
    hostname = urlparse(url).hostname
    if hostname.startswith('www'):
        hostname = hostname.replace('www.', '')

    if hostname in HOSTNAME_TO_JOURNAL_MAP.keys():
        return HOSTNAME_TO_JOURNAL_MAP[hostname]
    else:
        return None


class UrlReverse(object):

    def __init__(self, url):
        self.url = url

        self.pmid = None
        self.doi = find_doi_in_string(self.url)

        self.url_format = None

        self.citation = {'jtitle': None, 'volume': None, 'aulast': None,
                         'year': None, 'first_page': None,
                        }

        if self.doi:
            self.pmid = doi2pmid(self.doi)
        else:
            parts = get_article_info_from_url(url)
            if parts['format'] == 'pmid':
                self.pmid = parts['pmid']
            elif parts['format'] == 'vip':
                self.citation['jtitle'] = jrnl
                self.citation.update(parts)

    def to_dict():
        return self.__dict__


