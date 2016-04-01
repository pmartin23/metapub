import unittest

from metapub.convert import pmid2doi, pmid2doi_with_score, PubMedArticle2doi, PubMedArticle2doi_with_score

pmid_with_doi_in_PMA = 25847151
pmid_with_doi_in_PMA_expected_doi = "10.1016/j.neulet.2015.04.001"

pmid_with_doi_from_CrossRef = 11228145
pmid_with_doi_from_CrossRef_expected_doi = '10.1126/science.1057766'

pmid_with_unknown_doi = 19634325


class TestConversions(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pmid2doi(self):
        # pmid2doi references PubMedArticle2doi, so let's consider that function
        # implicitly tested here.
        doi = pmid2doi(pmid_with_doi_in_PMA)
        assert doi == pmid_with_doi_in_PMA_expected_doi

        doi = pmid2doi(pmid_with_doi_from_CrossRef)
        assert doi == pmid_with_doi_from_CrossRef_expected_doi

        doi = pmid2doi(pmid_with_unknown_doi)
        assert doi is None

    def test_pmid2doi_with_score(self):
        doi, score = pmid2doi_with_score(pmid_with_doi_in_PMA)
        assert doi == pmid_with_doi_in_PMA_expected_doi
        assert score == 10.0

        doi, score = pmid2doi_with_score(pmid_with_doi_from_CrossRef)
        assert doi == pmid_with_doi_from_CrossRef_expected_doi
        assert score > 2.0

        doi, score = pmid2doi_with_score(pmid_with_unknown_doi)
        assert doi is None
        assert score < 2.0
