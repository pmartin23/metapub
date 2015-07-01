import unittest

from metapub import FindIt
#from metapub.pubmedcentral import *

# PMIDs carefully chosen to not result in HTTP retrievals in order to find PDF links.

wiley_pmids = []
jstage_pmids = []
pmc_pmids = []
sciencedirect_pmids = []
bmj_pmids = []
oxford_pmids = []
lancet_pmids = []


class TestFindIt(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

 
