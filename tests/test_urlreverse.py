from metapub.urlreverse.urlreverse import *

import unittest

# SAMPLE URLs (as yet unused in tests)
#
#https://www.researchgate.net/figure/279965765_fig3_Figure-2-Genotyping-the-CPVT1-RyR2-R420Q-mutation-and-CPVT2-CASQ2-D307H-mutation-A


# "fixtures"
pmid_samples = {
    'http://www.ncbi.nlm.nih.gov/pubmed/22253870': '22253870',
    'http://aac.asm.org/cgi/pmidlookup?view=long&pmid=7689822': '7689822',
    }

vip_samples = {
    'http://www.jbc.org/content/266/17/10880.full.pdf': '2040605',
    'http://cardiovascres.oxfordjournals.org/content/75/1/69': '17449018',
    'http://www.jbc.org/content/285/5/3076.full': '19920148',
    'http://www.bloodjournal.org/content/127/16/1967.full.pdf': '26932803', 
    }

jstage_samples = { 
    'https://www.jstage.jst.go.jp/article/jat/16/3/16_E125/_pdf': '10.5551/jat.E125',
    'https://www.jstage.jst.go.jp/article/yoken/66/4/66_306/_pdf': '10.7883/yoken.66.306',
    'https://www.jstage.jst.go.jp/article/jvms1939/40/5/40_5_575/_pdf/': '10.1292/jvms1939.40.575',
    'https://www.jstage.jst.go.jp/article/analsci/21/12/21_12_1479/_article': '10.2116/analsci.21.1479',
    }
            
wiley_samples = {
    'http://onlinelibrary.wiley.com/doi/10.1111/j.1582-4934.2011.01476.x/full': '10.1111/j.1582-4934.2011.01476.x',
    'http://onlinelibrary.wiley.com/store/10.1002/(SICI)1097-0061(19980130)14:2<161::AID-YEA208>3.0.CO;2-Y/asset/208_ftp.pdf?v=1&t=ibqsvd4r&s=d74396a1e55e0a7b1bb08f297ce23c220d713d6f': '10.1002/(SICI)1097-0061(19980130)14:2<161::AID-YEA208>3.0.CO;2-Y',
    'http://onlinelibrary.wiley.com/doi/10.1002/humu.20182/pdf': '10.1002/humu.20182',
    }

karger_samples = {
    'http://www.karger.com/Article/PDF/322318': '10.1159/000322318',
    'https://www.karger.com/Article/Abstract/329047': '10.1159/000329047',
    'https://www.karger.com/Article/Abstract/83388': '10.1159/000083388',
    }

sciencedirect_samples = {
    
    }

cell_samples = {
    'http://www.cell.com/pdf/0092867480906212.pdf': '10.1016/0092-8674(80)90621-2',
    'http://www.cell.com/cancer-cell/pdf/S1535610806002844.pdf': '10.1016/j.ccr.2006.09.010',
    'http://www.cell.com/molecular-cell/abstract/S1097-2765(00)80321-4': '10.1016/S1097-2765(00)80321-4',
    'http://www.cell.com/biophysj/abstract/S0006-3495(15)01407-1': '10.1016/S0006-3495(15)01407-1',
    'http://www.cell.com/current-biology/fulltext/S0960-9822(16)30170-1': '10.1016/j.cub.2016.03.002',
    }

pmc_samples = {
    'http://europepmc.org/articles/pmc4103182': '24070655',
    'http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC3296117&blobtype=pdf': '21801150',
    'europepmc.org/articles/PMC360379/pdf/molcellb00133-0293.pdf': '1406642',
    'http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4382744/': '25833843',
    'http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3256213/': '22253870',
    'http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3256213/pdf/pone.0030042.pdf': '22253870',
    }

jci_samples = {
    'https://www.jci.org/articles/view/32496': '10.1172/JCI32496',
    'http://www.jci.org/articles/view/37506/version/1/pdf/render': '10.1172/JCI37506',
    'http://www.jci.org/articles/view/18784': '10.1172/JCI18784',
    'https://www.jci.org/articles/view/31080/figure/1': '10.1172/JCI31080',
    }

springer_samples = {
    'link.springer.com/article/10.1186/1471-2164-7-243': '10.1186/1471-2164-7-243',
    'http://link.springer.com/content/pdf/10.1007/s004390000422.pdf': '10.1007/s004390000422',
    }

class TestUrlReverse(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_pmids_for_pmc_links(self):
        for url, pmid in pmc_samples.items():
            urlrev = UrlReverse(url)
            assert urlrev.pmid == pmid

    def test_get_pmids_for_pmid_links(self):
        for url, pmid in pmid_samples.items():
            urlrev = UrlReverse(url)
            assert urlrev.pmid == pmid

    #def test_get_jstage_doi_from_link(self):
    #    for url, doi in jstage_samples.items():
    #        assert doi == get_jstage_doi_from_link(doi)

    def test_try_doi_methods_for_wiley_samples(self):
        for url, doi in wiley_samples.items():
            assert doi == try_doi_methods(url)['doi']

    def test_try_doi_methods_for_springer_samples(self):
        for url, doi in springer_samples.items():
            assert doi == try_doi_methods(url)['doi']

    def test_get_karger_doi_from_link(self):
        for url, doi in karger_samples.items():
            assert doi == get_karger_doi_from_link(url)

    def test_get_sciencedirect_doi_from_link(self):
        for url, doi in sciencedirect_samples.items():
            assert doi == get_sciencedirect_doi_from_link(url)

    def test_get_cell_doi_from_link(self):
        for url, doi in cell_samples.items():
            assert doi == get_cell_doi_from_link(url)

    def test_get_vip_url_with_supplied_title(self):
        url = 'http://www.clinsci.org/content/ppclinsci/130/11/871'
        expected_doi = '10.1042/CS20150777',
        urlrev = UrlReverse(url, title='High-fat diet increases O-GlcNAc levels in cerebral arteries')

