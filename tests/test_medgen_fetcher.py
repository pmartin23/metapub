import unittest, os

from metapub import MedGenFetcher

hugos = ['ACVRL1', 'FOXP3', 'ATM']

TEST_CACHEDIR = 'tests/testcachedir'


class TestMedGenFetcher(unittest.TestCase):

    def setUp(self):
        self.fetch = MedGenFetcher()

    def tearDown(self):
        pass

    def test_fetch_concepts_for_known_gene(self):
        hugo = 'ACVRL1'
        result = self.fetch.uids_by_term(hugo+'[gene]')
        assert result is not None
        assert result[0] == '324960'
    
    def test_fetch_concepts_for_incorrect_term(self):
        term = 'AVCRL'
        result = self.fetch.uids_by_term(term+'[gene]')
        assert result == []

    def test_configurable_cachedir(self):
        """ Test that `cachedir` keyword argument is fully supported in modes:

        cachedir == 'default'   <-- assumed working since other tests use this.
        cachedir is None
        cachedir is 'some/path'
        cachedir is '~/path'
        """

        cachedir = TEST_CACHEDIR
        # start with cachedir==None; test that no cachedir is created.
        fetch = MedGenFetcher(cachedir=None)
        assert not os.path.exists(cachedir)

        fetch = MedGenFetcher(cachedir=cachedir)
        assert os.path.exists(cachedir)

        os.unlink(fetch._cache_path)
        os.rmdir(cachedir)

        fetch = MedGenFetcher(cachedir='~/testcachedir')
        assert os.path.exists(os.path.expanduser('~/testcachedir'))

        os.unlink(fetch._cache_path)
        os.rmdir(os.path.expanduser('~/testcachedir'))
