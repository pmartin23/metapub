from metapub.text_mining import re_doi, findall_dois_in_text, find_doi_in_string, \
    get_biomedcentral_doi_from_link, get_nature_doi_from_link

import unittest
from hamcrest import assert_that, is_

# "fixtures"

real_dois = ['10.1002/(SICI)1098-1004(1999)14:1<91::AID-HUMU21>3.0.CO;2-B',
        '10.1007/s12020-014-0368-x',
        '10.1101/gad.14.3.278',
        '10.1016/S0898-1221(00)00204-2',]

fake_dois = ['abcdefg', 'ab.efgh/1234567890', '1.2/blargh' ]

almost_dois = ['10.10.1.0/26', '10.1234/gad.15.4).' ]

text_with_many_dois = open('tests/data/text_with_many_dois.txt', 'r').read()
text_with_one_doi = open('tests/data/text_with_one_doi.txt', 'r').read()
text_with_no_dois = open('tests/data/text_with_no_dois.txt', 'r').read()
text_with_one_whitespace_doi = open('tests/data/text_with_one_whitespace_doi.txt', 'r').read()


class TestFindDOIs(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_find_whitespace_doi(self):
        result = find_doi_in_string(text_with_one_whitespace_doi, whitespace=True)
        if result:
            assert result == '10.1002/pd.354'
        else:
            assert False

    def test_find_no_doi_in_text(self):
        result = find_doi_in_string(text_with_no_dois)
        if result:
            assert False
        else:
            assert True

    def test_find_one_doi_in_text(self):
        results = findall_dois_in_text(text_with_one_doi)
        if len(results) == 1:
            assert True
        else:
            assert False

    def test_findall_dois_in_text(self):
        results = findall_dois_in_text(text_with_many_dois)
        if len(results) > 40:
            assert True
        else:
            assert False

    def test_find_doi_returns_None_for_fake_DOIs(self):
        for fake_doi in fake_dois:
            assert (find_doi_in_string(fake_doi) is None)

    def test_find_doi_in_string(self):
        for doi in almost_dois:
            assert (find_doi_in_string(doi) is not None)

    def test_find_doi_in_exact_strings(self):
        for doi in real_dois:
            result = find_doi_in_string(doi)
            assert len(result) == len(doi)

    def test_get_nature_doi_from_link(self):
        doi = get_nature_doi_from_link('http://www.nature.com/ejhg/journal/v22/n11/extref/ejhg201416x6.doc')
        assert_that(doi, is_('10.1038/ejhg.2014.16'))

        doi = get_nature_doi_from_link('http://www.nature.com/neuro/journal/v13/n11/abs/nn.2662.html')
        assert_that(doi, is_('10.1038/nn.2662'))

        doi = get_nature_doi_from_link('http://www.nature.com/gim/journal/vaop/ncurrent/extref/gim2014176x1.xls')
        assert_that(doi, is_('10.1038/gim.2014.176'))

        doi = get_nature_doi_from_link('http://www.nature.com/jhg/journal/v57/n3/pdf/jhg2011139a.pdf?origin=publication_detail')
        assert_that(doi, is_('10.1038/jhg.2011.139'))

        doi = get_nature_doi_from_link('http://www.nature.com/onc/journal/v26/n57/full/1210594a.html')
        assert_that(doi, is_('10.1038/sj.onc.1210594'))

        doi = get_nature_doi_from_link('http://www.nature.com/articles/cddis201475')
        assert_that(doi, is_('10.1038/cddis.2014.75'))

        doi = get_nature_doi_from_link('http://www.nature.com/articles/nature03404')
        assert_that(doi, is_('10.1038/nature03404'))

        doi = get_nature_doi_from_link('http://www.nature.com/articles/ng.2223')
        assert_that(doi, is_('10.1038/ng.2223'))

    def test_get_biomedcentral_doi_from_link(self):
        doi = get_biomedcentral_doi_from_link('http://www.biomedcentral.com/content/pdf/bcr1282.pdf')
        assert_that(doi, is_('10.1186/bcr1282'))

        doi = get_biomedcentral_doi_from_link('http://www.biomedcentral.com/1471-2148/12/114')
        assert_that(doi, is_('10.1186/1471-2148-12-114'))

        doi = get_biomedcentral_doi_from_link('http://www.biomedcentral.com/content/supplementary/gb-2013-14-10-r108-S8.xlsx')
        assert_that(doi, is_('10.1186/gb-2013-14-10-r108'))

        doi = get_biomedcentral_doi_from_link('http://www.biomedcentral.com/1471-2164/15/707/table/T2')
        assert_that(doi, is_('10.1186/1471-2164-15-707'))

 
