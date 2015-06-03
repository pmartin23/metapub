import unittest
from metapub import FindIt

class TestFindItDances(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_aaas_tango(self):
        '''
        Test on the xml returned by eutils
        '''
        pmid_needs_form = '18385036'    # Sci Signal requiring form negotiation
        pmid_no_form = '25678633'       # Science 
        pmid_no_form_url = 'http://www.sciencemag.org/content/347/6223/695.full.pdf'

        source = FindIt(pmid=pmid_no_form)
        assert source.url == pmid_no_form_url
