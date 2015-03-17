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

        stuff = fetch.pmids_for_query(**params)
        print stuff

        params = { 'TA':'Journal of Neural Transmission', 
                    'pdat':2014, 
                    'vol':121, 
                    'aulast': 'Freitag'
         } 

        stuff = fetch.pmids_for_query(**params)
        print stuff

        params = { 'mesh': 'breast neoplasm' }
        stuff = fetch.pmids_for_query(since='2015/1/1', until='2015/3/1', pmc_only=True, **params)

        print params
        print stuff

