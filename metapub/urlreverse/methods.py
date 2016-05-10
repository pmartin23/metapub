from __future__ import absolute_import, print_function, unicode_literals

import re

from ..exceptions import DxDOIError
from ..text_mining import (find_doi_in_string, get_nature_doi_from_link, scrape_doi_from_article_page,
                           get_biomedcentral_doi_from_link)
from ..utils import hostname_of, rootdomain_of

from .hostname2doiprefix import HOSTNAME_TO_DOI_PREFIX_MAP


# string templates
OFFICIAL_PII_FORMAT = '{pt1}-{pt2}({pt3}){pt4}-{pt5}'


# VIP (volume-issue-page)
re_vip = re.compile('(?P<hostname>.*?)\/content(\/\w+)?\/(?P<volume>\d+)\/(?P<issue>\w+)\/(?P<first_page>\w+)', re.I)

# PMID in url
re_pmidlookup = re.compile('.*?(\?|&)pmid=(?P<pmid>\d+)', re.I)
re_pubmed_pmid = re.compile('.*?ncbi.nlm.nih.gov\/pubmed\/(?P<pmid>\d+)')

# PMCID in url
re_pmcid = re.compile('.*?(?P<hostname>ncbi.nlm.nih.gov|europepmc.org)\/.*?(?P<pmcid>PMC\d+)', re.I)

# PII -- see https://en.wikipedia.org/wiki/Publisher_Item_Identifier
pii_official = '(?P<pii>S\d{4}-\d{4}\(\d{2}\)\d{5}-\w{1})'
re_sciencedirect_pii_simple = re.compile('.*?(?P<hostname>sciencedirect\.com)\/science\/article\/pii\/(?P<pii>S\d+\w?)', re.I)
re_sciencedirect_pii_official = re.compile('.*?(?P<hostname>sciencedirect\.com)\/science\/article\/pii\/' + pii_official, re.I)
re_cell_pii_simple = re.compile('.*?(?P<hostname>cell\.com)\/(?P<journal_abbrev>.*?)\/(pdf|abstract|fulltext|pdfExtended)\/(?P<pii>S\d+)', re.I)
re_cell_pii_official = re.compile('.*?cell.com\/((?P<journal_abbrev>.*?)\/)?(pdf|abstract|fulltext|pdfExtended)\/' + pii_official, re.I)
re_cell_old_style = re.compile('.*?(?P<hostname>cell\.com)\/(pdf|abstract|fulltext)\/(?P<pii>\d+)', re.I)

# Unique
re_jstage = re.compile('.*?(?P<hostname>jstage\.jst\.go\.jp)\/article\/(?P<journal_abbrev>.*?)\/(?P<volume>\d+)\/(?P<issue>.*?)\/(?P<info>).*?\/', re.I)
re_jci = re.compile('.*?(?P<hostname>jci\.org)\/articles\/view\/(?P<jci_id>\d+)', re.I)
re_karger = re.compile('.*?(?P<hostname>karger\.com)\/Article\/(Abstract|Pdf)\/(?P<kid>\d+)', re.I)
#re_ahajournals = re.compile('\/(?P<doi_suffix>\w+\.\d+\.\d+\.\w+)', re.I)
re_ahajournals = re.compile('\/(?P<doi_suffix>[a-z0-9]+\.\d+\.\d+\.[a-z0-9]+)', re.I)

re_bmj = re.compile('(^|https?:\/\/)(?P<subdomain>\w+)\.bmj.com\/content\/(?P<volume>\d+)\/(?P<doi_suffix>bmj.\w+)', re.I)
re_bmj_vip_to_doi = re.compile('(^|https?:\/\/)(?P<subdomain>\w+).bmj.com\/content\/(?P<volume>\d+)\/(?P<issue>\d+)\/(?P<first_page>\w+)', re.I)

# Early release formats
re_early_release = re.compile('(^|(https?):\/\/)(?P<hostname>.*?)\/content(\/\w+)?\/early\/(?P<year>\d+)\/(?P<month>\d+)\/(?P<day>\d+)\/(?P<doi_suffix>.*?)(\.full|\.pdf|\.abstract|$)')


# TODO: Common supplement URL format
#re_supplement_common = re.compile()
# http://jmg.bmj.com/content/suppl/2012/05/09/jmedgenet-2012-100892.DC1/Otocephaly_Supplementary_Table_3.pdf
# http://www.pnas.org/content/suppl/2013/07/08/1305207110.DCSupplemental/sapp.pdf
# http://jmg.bmj.com/content/suppl/2015/07/17/jmedgenet-2015-103132.DC1/jmedgenet-2015-103132supp.pdf

re_pnas_supplement = re.compile('.*?pnas.org\/content\/suppl\/(?P<year>\d+)\/(?P<month>\d+)\/(?P<day>\d+)\/(?P<ident>.*?)\/', re.I)


def get_pnas_doi_from_link(url):
    """ PNAS (proceedings of the national academy of sciences of the USA)

    Examples:
        http://www.pnas.org/content/suppl/2013/07/08/1305207110.DCSupplemental/sapp.pdf --> 10.1073/pnas.1305207110

    :param url: (str)
    :return: doi (str) or None
    """
    out = '10.1073/pnas.'
    match = re_pnas_supplement.match(url)
    if match:
        doi_suffix = match.groupdict()['ident'].split('.')[0]
        return out + doi_suffix
    return None


def get_bmj_doi_from_link(url):
    """ BMJ and subsidiaries use a VIP-ish format that can *sometimes* be mapped to their real
    DOIs. In the case that this process fails, use of the VIP->citation routines should work.

    List of BMJ Journals: http://journals.bmj.com/

    Examples:
        http://jmg.bmj.com/content/39/6/e31.full --> 10.1136/jmg.39.6.e31
        http://www.bmj.com/content/353/bmj.i2195 --> 10.1136/bmj.i2195
        http://www.bmj.com/content/353/bmj.i2139 --> 10.1136/bmj.i2139

    Returns None (should be caught by find_doi_in_string):
        http://bmjopengastro.bmj.com/doi/full/10.1136/bmjgast-2015-000075 --> 10.1136/bmjgast-2015-000075

    Returns None (must use VIP->citation routines):
        http://gut.bmj.com/content/65/5/767.abstract --> 10.1136/gutjnl-2015-311246

    :param url: (str)
    :return: doi (str) or None
    """

    out = '10.1136/'

    BMJ_VIP_TO_DOI_DOMAINS = ['jmg']
    match = re_bmj_vip_to_doi.match(url)
    if match:
        parts = match.groupdict()
        if parts['subdomain'] in BMJ_VIP_TO_DOI_DOMAINS:
            return out + '{subdomain}.{volume}.{issue}.{first_page}'.format(**parts)

    match = re_bmj.match(url)
    if match:
        parts = match.groupdict()
        return out + parts['doi_suffix']

    return None


def get_spandidos_doi_from_link(url):
    """ Spandidos urls follow several different conventions and their website seems to be undergoing
    some changes recently. For now, let's just scrape the page for the first available DOI.

    Examples:
        http://www.spandidos-publications.com/or/30/2/553 --> 10.3892/or.2013.2535
        https://www.spandidos-publications.com/10.3892/or.2016.4700 --> 10.3892/or.2013.2535
        https://www.spandidos-publications.com/10.3892/or.2013.2535/abstract --> 10.3892/or.2013.2535

    :param url: (str)
    :return: doi (str) or None
    """
    if not url.find('spandidos-publications.com'):
        return None

    url = url.replace('download', 'abstract')
    return scrape_doi_from_article_page(url)


def get_karger_doi_from_link(url):
    """ Karger IDs can be found in the URL after the "PDF" or "Abstract" piece, and used to
    compose a DOI by prepending enough zeroes to make a 9-digit number. The Karger publisher
    ID is 10.1159

    e.g.
       https://www.karger.com/Article/Abstract/329047 --> 10.1159/000329047
       https://www.karger.com/Article/Abstract/83388 --> 10.1159/000083388

    :param url: (str)
    :return: doi (str) or None
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
    doi = out + pii
    try:
        DXDOI.resolve(doi)
        return doi
    except DxDOIError:
        #print('sciencedirect recomposed DOI %s is not a real DOI' % doi)
        pass

    # use URL scrape
    return scrape_doi_from_article_page('http://www.sciencedirect.com/science/article/pii/%s' % pii)


def get_cell_doi_from_link(url):
    """ Cell and ScienceDirect links have similar properties, but there are several different url
    types for Cell abstracts and PDFs (much like biomedcentral).

    Examples:
        http://www.cell.com/pdf/0092867480906212.pdf --> 10.1016/0092-8674(80)90621-2
        http://www.cell.com/cancer-cell/pdf/S1535610806002844.pdf --> 10.1016/j.ccr.2006.09.010
        http://www.cell.com/molecular-cell/abstract/S1097-2765(00)80321-4 --> 10.1016/S1097-2765(00)80321-4
        http://www.cell.com/current-biology/fulltext/S0960-9822%2816%2930170-1 --> 10.1016/j.cub.2016.03.002
        http://www.cell.com/cell-reports/pdfExtended/S2211-1247(15)01030-X --> 10.1016/j.celrep.2015.09.019
        http://www.cell.com/ajhg/pdfExtended/S0002-9297(16)30051-9 --> 10.1016/j.ajhg.2016.03.016
        http://www.cell.com/ajhg/pdf/S0002-9297(16)00050-1.pdf --> 10.1016/j.ajhg.2016.03.016


    Unsolved cases:
        http://www.cell.com/cms/attachment/2020150130/2039963519/mmc1.pdf

    :param url: (str)
    :return: doi or None
    """
    out = '10.1016/'
    pii = ''

    if not 'cell.com' in url:
        return None

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
        if journal_abbrev and journal_abbrev in ['cancer-cell', 'current-biology', 'cell-reports', 'ajhg']:
            url = url.replace('pdfExtended', 'abstract')
            url = url.replace('/pdf/', '/abstract/')
            url = url.replace('.pdf', '')
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
    out = '10.1161/'
    if 'ahajournals.org' in url:
        match = re_ahajournals.match(url)
        if match:
            return out + match.groupdict()['doi_suffix']
    return None


def get_early_release_doi_from_link(url):
    """
    Examples:
        http://cancerres.aacrjournals.org/content/early/2015/12/30/0008-5472.CAN-15-0295.full.pdf --> 10.1158/0008-5472.CAN-15-0295
        http://ajcn.nutrition.org/content/early/2016/04/20/ajcn.115.123752.abstract --> 10.3945/ajcn.115.123752
        http://www.mcponline.org/content/early/2016/04/25/mcp.O115.055467.full.pdf+html --> 10.1074/mcp.O115.055467
        http://nar.oxfordjournals.org/content/early/2013/11/21/nar.gkt1163.full.pdf --> 10.1093/nar/gkt1163
        http://jmg.bmj.com/content/early/2008/07/08/jmg.2008.058297 --> 10.1136/jmg.2008.058297

    :param url: (str)
    :return: doi or None
    """

    match = re_early_release.match(url)
    if match:
        resd = match.groupdict()
        hostname = hostname_of(resd['hostname'])
        root_domain = rootdomain_of(hostname)

        # special treatment for oxfordjournals.org
        if root_domain in 'oxfordjournals.org':
            doi_pt1, doi_pt2 = resd['doi_suffix'].split('.', 2)
            doi_suffix = '%s/%s' % (doi_pt1, doi_pt2)
            return HOSTNAME_TO_DOI_PREFIX_MAP['*.oxfordjournals.org'] + '/' + doi_suffix

        if hostname in HOSTNAME_TO_DOI_PREFIX_MAP.keys():
            return HOSTNAME_TO_DOI_PREFIX_MAP[hostname] + '/' + resd['doi_suffix']

        elif '*.%s' % root_domain in HOSTNAME_TO_DOI_PREFIX_MAP.keys():
            # create a "wildcard" subdomain lookup in case that's an option in the hostname-doi map.
            return HOSTNAME_TO_DOI_PREFIX_MAP['*.%s' % root_domain] + '/' + resd['doi_suffix']


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


# == DOI search method registry... order matters! don't screw around with it unless you know what you're doing. :) == #
DOI_METHODS = [get_cell_doi_from_link,
               get_early_release_doi_from_link,
               get_jstage_doi_from_link,
               get_pnas_doi_from_link,
               get_bmj_doi_from_link,
               get_ahajournals_doi_from_link,
               get_biomedcentral_doi_from_link,
               get_nature_doi_from_link,
               get_sciencedirect_doi_from_link,
               get_karger_doi_from_link,
               get_spandidos_doi_from_link,
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

