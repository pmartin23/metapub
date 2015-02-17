import re

# examples of real DOIs: 
#         10.1002/(SICI)1098-1004(1999)14:1<91::AID-HUMU21>3.0.CO;2-B
#         10.1007/s12020-014-0368-x
#         10.1101/gad.14.3.278
#         10.1016/S0898-1221(00)00204-2

re_doi = re.compile(r'(10[.][0-9]{2,}(?:[.][0-9]+)*/(?:(?!["&\'])\S)+)')

def findall_dois_in_text(inp):
    '''returns all seen DOIs in input string.'''
    return re_doi.findall(inp)

def find_doi_in_string(inp):
    '''returns the first seen DOI in the input string.'''
    try:
        return re_doi.findall(inp)[0]
    except IndexError:
        return None

#### NOT TESTED and probably not working #####
def get_pmc_fulltext_filename_for_PubMedArticle(pma):
    fmt = '{journal}/{journal}_{year}_{month}_{day}_{voliss}_{pages}'
    return fmt.format(**pma.to_dict())

