import unittest

from metapub import MedGenFetcher
fetch = MedGenFetcher()

hugos = ['ACVRL1']

class TestPubmedSearch(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_fetch_concepts_for_known_gene(self):
        hugo = 'ACVRL1'
        result = fetch.uids_by_term(hugo+'[gene]')
        assert result is not None
        assert result[0]=='324960'
    
    def test_fetch_concepts_for_incorrect_term(self):
        term = 'AVCRL'
        result = fetch.uids_by_term(term+'[gene]')
        assert result==[]

