import unittest

from metapub import PubMedFetcher
from metapub.pubmedcentral import *

class TestPubmedFetcher(unittest.TestCase):

    def setUp(self):
        self.fetch = PubMedFetcher()

    def tearDown(self):
        pass

    def test_pmids_for_query(self):
        params = { 'jtitle': 'American Journal of Medical Genetics', 
                    'year': 1996, 
                    'volume': 61, 
                    'author1_lastfm': 'Hegmann' }

        pmids = self.fetch.pmids_for_query(**params)
        assert len(pmids)==1

        params = { 'TA':'Journal of Neural Transmission', 
                    'pdat':2014, 
                    'vol':121, 
                    'aulast': 'Freitag'
         } 

        pmids = self.fetch.pmids_for_query(**params)
        assert len(pmids) == 1

    def test_specified_return_slice(self):
        pmids = self.fetch.pmids_for_query(since='2015/3/1', retmax=1000)
        assert len(pmids)==1000

        pmids = self.fetch.pmids_for_query(since='2015/3/1', retstart=200, retmax=500)
        assert len(pmids)==500

    def test_pmc_only(self):
        params = { 'mesh': 'breast neoplasm' }
        stuff = self.fetch.pmids_for_query(since='2015/1/1', until='2015/3/1', pmc_only=True, **params)
        print stuff

