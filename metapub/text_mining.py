import re

re_doi = re.compile(r'(10[.][0-9]{2,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)')

def findall_dois_in_text(body):
    return re_doi.findall(body)

def find_doi_in_string(body):
    try:
        return re_doi.findall(body)[0]
    except KeyError:
        return None

