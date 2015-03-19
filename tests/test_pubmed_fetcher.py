import unittest

from metapub import PubMedFetcher
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
