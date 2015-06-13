import unittest
import logging
from metapub import FindIt

log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
log.addHandler(ch)

class TestFindItDances(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_aaas_tango(self):
        pmid_needs_form = '18385036'    # Sci Signal requiring form negotiation
        pmid_needs_form_url = 'http://stke.sciencemag.org/content/1/13/eg3.full.pdf'
        pmid_no_form = '25678633'       # Science 
        pmid_no_form_url = 'http://sciencemag.org/content/347/6223/695.full.pdf'

        source = FindIt(pmid=pmid_no_form)
        assert source.url == pmid_no_form_url

        source = FindIt(pmid=pmid_needs_form)
        #TODO: update this when the_aaas_tango knows how to navigate forms.
        assert source.url is None

    def test_jci_polka(self):
        pmid = 26030226
        source = FindIt(pmid=pmid)
        if source.pma.pmc:
            assert source.url.find('europepmc.org') > -1
        else:
            assert source.url == 'http://www.jci.org/articles/view/82041/version/1/pdf/render'

