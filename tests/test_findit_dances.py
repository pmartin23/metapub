from __future__ import print_function

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

    def test_jama_dance(self):
        doi_but_unfree = '26575068'
        source = FindIt(doi_but_unfree)
        assert source.url is None

    def test_pmc_twist(self):
        embargoed = '25554792'      # Science / pmc-release = Jan 2, 2016 / PMC4380271
        embargoed_url = 'http://sciencemag.org/content/347/6217/1258522.full.pdf'

        nonembargoed = '26106273'   # Saudi Pharm / pmc-release = None / PMC4475813

        source = FindIt(pmid=embargoed)
        assert source.pma.pmc == '4380271'
        assert source.pma.history['pmc-release'] is not None
        assert source.url == embargoed_url

        source = FindIt(pmid=nonembargoed)
        assert source.pma.pmc == '4475813'
        assert source.pma.history.get('pmc-release', None) is None
        print(source.url)

    def test_aaas_tango(self):
        pmid_needs_form = '18385036'    # Sci Signal requiring form negotiation
        # pmid_needs_form_url = 'http://stke.sciencemag.org/content/1/13/eg3.full.pdf'
        pmid_no_form = '25678633'       # Science 
        pmid_no_form_url = 'http://sciencemag.org/content/347/6223/695.full.pdf'

        source = FindIt(pmid=pmid_no_form)
        assert source.url == pmid_no_form_url

        source = FindIt(pmid=pmid_needs_form)
        # TODO: update this when the_aaas_tango knows how to navigate forms.
        assert source.url is None

    # Looks like JCI complained about EuropePMC hosting its stuff?
    def test_jci_polka(self):
        pmid = 26030226
        source = FindIt(pmid=pmid)
    #    if source.pma.pmc:
    #        assert source.url.find('europepmc.org') > -1
    #    else:
        assert source.reason.find('DENIED') > -1
        assert source.reason.find('jci.org') > -1

    def test_jstage_dive(self):
        pmid = 21297370
        source = FindIt(pmid=pmid)
        assert source.url == 'https://www.jstage.jst.go.jp/article/yakushi/131/2/131_2_247/_pdf'
