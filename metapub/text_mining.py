import re

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

