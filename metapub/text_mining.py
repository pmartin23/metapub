import re

# examples of real DOIs: 
#         10.1002/(SICI)1098-1004(1999)14:1<91::AID-HUMU21>3.0.CO;2-B

re_doi = re.compile(r'(10[.][0-9]{2,}(?:[.][0-9]+)*/(?:(?!["&\'])\S)+)')

def findall_dois_in_text(body):
    return re_doi.findall(body)

def find_doi_in_string(body):
    try:
        return re_doi.findall(body)[0]
    except IndexError:
        return None

