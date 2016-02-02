import unittest, os

from metapub import PubMedFetcher 
from metapub.pubmedfetcher import parse_related_pmids_result
from metapub.pubmedcentral import *


TEST_CACHEDIR = 'tests/cachedir'
try:
    for item in os.listdir(TEST_CACHEDIR):
        os.unlink(os.path.join(TEST_CACHEDIR, item))
except OSError:
    pass

try:
    os.rmdir(TEST_CACHEDIR)
except OSError:
    pass


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
        """ * pubmed    (all related links)
            * citedin   (papers that cited this paper)
            * five      (the "five" that pubmed displays as the top related results)
            * reviews   (review papers that cite this paper)
            * combined  (?)
        """

        expected_keys = ['pubmed', 'citedin', 'five', 'reviews', 'combined']
        xmlstr = open('tests/data/sample_related_pmids_result.xml').read()
        resd = parse_related_pmids_result(xmlstr)
        for key in resd.keys():
            assert key in expected_keys
        assert len(resd['citedin']) == 6

    def test_configurable_cachedir(self):
        """ Test that `cachedir` keyword argument is fully supported in modes:

        cachedir == 'default'   <-- assumed working since other tests use this.
        cachedir is None
        cachedir is 'some/path'
        cachedir is '~/path'
        """

        cachedir = TEST_CACHEDIR
        # start with cachedir==None; test that no cachedir is created.
        fetch = PubMedFetcher(cachedir=None)
        assert not os.path.exists(cachedir)

        fetch = PubMedFetcher(cachedir=cachedir)
        assert os.path.exists(cachedir)

        os.unlink(fetch._cache_path)
        os.rmdir(cachedir)

        fetch = PubMedFetcher(cachedir='~/testcachedir')
        assert os.path.exists(os.path.expanduser('~/testcachedir'))

        os.unlink(fetch._cache_path)
        os.rmdir(os.path.expanduser('~/testcachedir'))
