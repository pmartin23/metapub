from metapub.text_mining import re_doi, findall_dois_in_text, find_doi_in_string

import unittest

# "fixtures"

dois = ['10.1002/(SICI)1098-1004(1999)14:1<91::AID-HUMU21>3.0.CO;2-B',
        '10.1007/s12020-014-0368-x',
        '10.1101/gad.14.3.278',
        '10.1016/S0898-1221(00)00204-2',]

fake_dois = ['10.10.1.0/26', 'abcdefg', 'ab.efgh/1234567890' ]

text_with_many_dois = open('tests/data/text_with_many_dois.txt', 'r').read()
text_with_one_doi = open('tests/data/text_with_one_doi.txt', 'r').read()
text_with_no_dois = open('tests/data/text_with_no_dois.txt', 'r').read()


class TestRunStatus(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_findall_dois_in_text(self):
        pass

    def test_find_doi_returns_None_for_fake_DOIs(self):
        for fake_doi in fake_dois:
            assert (find_doi_in_string(fake_doi) is None)

    def test_find_doi_in_string(self):
        # 
        pass        

