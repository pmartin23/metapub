import unittest

from metapub import PubMedFetcher 
from metapub.pubmedfetcher import parse_related_pmids_result
from metapub.pubmedcentral import *

class TestPubmedFetcher(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_article_by_pmid(self):
        pmid = '4'
        fetch = PubMedFetcher()
        article = fetch.article_by_pmid(pmid)
        assert str(article.pmid) == pmid

        pmid = '25763451'
        fetch = PubMedFetcher()
        article = fetch.article_by_pmid(pmid)
        assert str(article.pmid) == pmid

    def test_related_pmids(self):
        ''' * pubmed    (all related links)
            * citedin   (papers that cited this paper)
            * five      (the "five" that pubmed displays as the top related results)
            * reviews   (review papers that cite this paper)
            * combined  (?)
        '''

        expected_keys = ['pubmed', 'citedin', 'five', 'reviews', 'combined']
        xmlstr = open('tests/data/sample_related_pmids_result.xml').read()
        resd = parse_related_pmids_result(xmlstr)
        for key in resd.keys():
            assert key in expected_keys
        assert len(resd['citedin']) == 6
        

