import re
from urlparse import urlparse

# examples of real DOIs: 
#         10.1002/(SICI)1098-1004(1999)14:1<91::AID-HUMU21>3.0.CO;2-B
#         10.1007/s12020-014-0368-x
#         10.1101/gad.14.3.278
#         10.1016/S0898-1221(00)00204-2

# example of DOI returned by the regular expression that is incorrect:
#         10.1002/ajmg.b.30585).

re_doi = re.compile(r'(10[.][0-9]{2,}(?:[.][0-9]+)*/(?:(?!["&\'])\S)+)')
re_doi_ws = re.compile(r'(10[.][0-9]{2,}(?:[.][0-9]+)*\s+/\s+(?:(?!["&\'])\S)+)')

re_pmid = re.compile('\d+')
re_numbers = re_pmid    # for now, until there's a better idea about parsing PMIDs...

def pick_pmid(text):
    '''return longest numerical string from text (string) as the pmid.
        if text is empty or there are no pmids, return None.'''
    pmids = re_pmid.findall(text)
    if pmids:
        longest = ''
        for num in pmids:
            if len(num) > len(longest):
                longest = num
        return longest
    else:
        return None

def _doi_pass_2(doi):
    if doi.endswith('.') or doi.endswith(','):
        return _doi_pass_2(doi[:-1])
    elif doi.endswith(')'):
        if doi.count('(') == doi.count(')'):
            return doi
        else:
            return _doi_pass_2(doi[:-1])
    else:
        return doi.replace(' ', '')

def findall_dois_in_text(inp, whitespace=False):
    '''returns all seen DOIs in input string.

       if `whitespace` arg set to True, look for DOIs like the following:
             10.1002 / pd.354   
        ...but return with whitespace stripped:
             10.1002/pd.354
    '''
    if whitespace:
        dois = re_doi_ws.findall(inp)
    else:
        dois = re_doi.findall(inp)
    return [_doi_pass_2(doi) for doi in dois]

def find_doi_in_string(inp, whitespace=False):
    '''returns the first seen DOI in the input string.'''
    try:
        doi = findall_dois_in_text(inp, whitespace)[0]
    except IndexError:
        return None
    return _doi_pass_2(doi)

#### NOT TESTED and probably not working #####
def get_pmc_fulltext_filename_for_PubMedArticle(pma):
    fmt = '{journal}/{journal}_{year}_{month}_{day}_{voliss}_{pages}'
    return fmt.format(**pma.to_dict())

def get_nature_doi_from_link(link):
    '''custom method to get a DOI from a nature.com URL
    For example, http://www.nature.com/modpathol/journal/vaop/ncurrent/extref/modpathol2014160x3.xlsx
    :param link: the URL
    :return: a string containing a DOI, if one was resolved, or None
    '''
    if 'nature.com' not in link:
        return None

    # this is a non-comprehensive list of nature journals
    style1journals = ['gimo', 'nature', 'nbt', 'ncb', 'nchembio', 'ncomms', 'ng', 'nm', 'nn', 'nrc', 'nrm', 'nsmb', 'srep']

    # example: link:http://www.nature.com/modpathol/journal/vaop/ncurrent/extref/modpathol2014160x3.xlsx
    #          doi:10.1038/modpathol.2014.160
    style2journals = ['aps', 'bjc', 'cddis', 'cr', 'ejhg', 'gim', 'jcbfm', 'jhg', 'jid', 'labinvest', 'leu',
                      'modpathol', 'mp', 'onc', 'oncsis', 'pr']

    match = re.search(r'nature.com/[a-zA-z]+/', link)

    journal_abbrev = None
    if match:
        try:
            journal_abbrev = match.group(0).split('/')[1]
        except:
            log.debug("Unable to extract journal abbrev from link {}".format(link))
            journal_abbrev = None

    # Example: http://www.nature.com/neuro/journal/v13/n11/abs/nn.2662.html
    if journal_abbrev == 'neuro':
        journal_abbrev = 'nn'

    match = re.search(r'%s\.{0,1}\d+' % journal_abbrev, link)
    if match:
        doi_suffix = match.group(0)
        if doi_suffix.endswith('.'):  # strip off a trailing period
            doi_suffix = doi_suffix[:-1]

        # the DOI suffix can be taken directly for these journals
        if journal_abbrev in style1journals:
            return  '10.1038/{}'.format(doi_suffix)

        # style2journals are the default
        else:
            year = doi_suffix[len(journal_abbrev):len(journal_abbrev)+4]
            num = doi_suffix[len(journal_abbrev)+4:]
            return '10.1038/{}.{}.{}'.format(journal_abbrev, year, num)

    # http://www.nature.com/articles/cr2009141 :
    # http://www.nature.com/articles/cddis201475
    # http://www.nature.com/articles/nature03404
    # http://www.nature.com/articles/ng.2223
    # http://www.nature.com/articles/nsmb.2666
    match = re.search(r'articles/(([a-z]+)\.{0,1}(\d+))', link)
    if match:
        full_match = match.group(0)
        suffix = match.group(1)
        journal_abbrev = match.group(2)
        num = match.group(3)
        if journal_abbrev in style1journals:
            return '10.1038/{}'.format(suffix)
        else:
            return '10.1038/{}.{}.{}'.format(journal_abbrev, num[:4], num[4:])

    # http://www.nature.com/leu/journal/v19/n11/abs/2403943a.html : 10.1038/sj.leu.2403943
    # http://www.nature.com/onc/journal/v26/n57/full/1210594a.html :  doi:10.1038/sj.onc.1210594
    match = re.search(r'full/\d+|abs/\d+', link)
    if match:
        num = match.group(0).split('/')[1]
        return '10.1038/sj.{}.{}'.format(journal_abbrev, num)

def get_biomedcentral_doi_from_link(link):
    '''custom method to get a DOI from a biomedcentral.com URL
    For example, http://www.nature.com/modpathol/journal/vaop/ncurrent/extref/modpathol2014160x3.xlsx
    :param link: the URL
    :return: a string containing a DOI, if one was resolved, or None
    '''
    # style 1:
    # http://www.biomedcentral.com/content/pdf/bcr1282.pdf : doi:10.1186/bcr1282
    # http://www.biomedcentral.com/content/pdf/1465-9921-12-49.pdf : doi:10.1186/1465-9921-12-49
    # http://www.biomedcentral.com/content/pdf/1471-2164-16-S1-S3.pdf : doi:10.1186/1471-2164-16-S1-S3
    # http://www.biomedcentral.com/content/pdf/1753-6561-4-s2-o22.pdf : doi:10.1186/1753-6561-4-S2-O22
    # http://genomebiology.com/content/pdf/gb-2013-14-10-r108.pdf : doi:10.1186/gb-2013-14-10-r108
    # for supplementary, must remove the last 'S' part
    # http://www.biomedcentral.com/content/supplementary/bcr1865-S3.doc : doi:10.1186/bcr1865
    # http://www.biomedcentral.com/content/supplementary/bcr3584-S1.pdf : doi:10.1186/bcr3584
    # http://www.biomedcentral.com/content/supplementary/1471-2105-11-300-S1.PDF : doi:10.1186/1471-2105-11-300
    # http://www.biomedcentral.com/content/supplementary/1471-2164-12-343-S3.XLS : doi:10.1186/1471-2164-12-343
    # http://www.biomedcentral.com/content/supplementary/1471-2164-14-S3-S7-S1.xlsx : doi:10.1186/1471-2164-14-S3-S7
    # http://www.biomedcentral.com/content/supplementary/gb-2013-14-10-r108-S8.xlsx : doi:10.1186/gb-2013-14-10-r108
    # style 2:
    # http://www.biomedcentral.com/1471-2148/12/114 : doi:10.1186/1471-2164-12-114
    # http://www.biomedcentral.com/1471-2164/15/707/table/T2 : doi:10.1186/1471-2164-15-707
    # http://www.biomedcentral.com/1471-2164/14/S1/S11 doi:10.1186/1471-2164-14-S1-S11
    # http://www.biomedcentral.com/1471-230X/11/31 doi:10.1186/1471-230X-11-31

    # first, try to use the filename
    if '/content/' in link:
        filename = link.split('/')[-1]
        if '.' in filename:
            base = filename.split('.')[0]
            if '/pdf/' in link:
                return '10.1186/' + base
            elif '/supplementary/' in link:
                i1 = base.rfind('S')
                i2 = base.rfind('s')
                i = max(i1, i2)
                return '10.1186/' + base[:i-1]
    else:
        parse_result = urlparse(link)
        path = parse_result.path
        keywords = ['abstract', 'figure', 'table']
        for kw in keywords:
            if kw in path:
                i = path.find(kw)
                path = path[:i-1]
                break
        if path[-1] == '/':
            path = path[:-1]
        if path[0] == '/':
            path = path[1:]
        return '10.1186/' + path.replace('/', '-')

