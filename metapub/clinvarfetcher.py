from __future__ import absolute_import

"""metapub.clinvarfetcher: tools for interacting with ClinVar data"""

from lxml import etree

from .eutils_common import get_eutils_client, get_cache_path
from .exceptions import *
from .base import Borg, parse_elink_response
from .config import DEFAULT_EMAIL

class ClinVarFetcher(Borg):
    '''ClinVarFetcher (a Borg singleton object)

    Toolkit for retrieval of ClinVar information. 

    Set optional 'cachedir' parameter to absolute path of preferred directory 
    if desired; cachedir defaults to <current user directory> + /.cache

        clinvar = ClinVarFetcher()

        clinvar = ClinVarFetcher(cachedir='/path/to/cachedir')

    Usage
    -----

    Get ClinVar accession IDs for gene name (switch single_gene to True to filter out 
    results containing more genes than the specified gene being searched, default False).

        cv_ids = clinvar.ids_by_gene('FGFR3', single_gene=True)

    Get ClinVar accession in python dictionary format for given ID:

        cv_subm = clinvar.accession(65533)  # can also submit ID as string 

    Get list of pubmed IDs (pmids) for given ClinVar accession ID:

        pmids = clinvar.pmids_for_id(65533)  # can also submit ID as string

    Get list of pubmed IDs (pmids) for hgvs_c string:

        pmids = clinvar.variant2pubmed('NM_017547.3:c.1289A>G')

    For more info, see the ClinVar eutils page:
    http://www.ncbi.nlm.nih.gov/clinvar/docs/maintenance_use/
    '''

    _cache_filename = 'clinvar-cache.db'

    def __init__(self, method='eutils', email=DEFAULT_EMAIL, cachedir='default'):
        Borg.__init__(self)
        self.method = method
        self._cache_path = None

        if method=='eutils':
            self._cache_path = get_cache_path(cachedir, self._cache_filename)
            self.qs = get_eutils_client(self._cache_path, email=email) 
            self.ids_by_gene = self._eutils_ids_by_gene
            self.get_accession = self._eutils_get_accession
            self.pmids_for_id = self._eutils_pmids_for_id
            self.ids_for_variant = self._eutils_ids_for_variant
            self.variant2pubmed = self._eutils_variant2pubmed
            self.get_variant_summary = self._eutils_get_variant_summary
        else:
            raise NotImplementedError('coming soon: fetch from local clinvar via medgen-mysql.')

    def _eutils_get_accession(self, accession_id):
        '''returns python dict of info for given ClinVar accession ID.

        :param: accession_id (integer or string)
        :return: dictionary
        '''
        result = self.qs.esummary({'db': 'clinvar', 'id': accession_id, 'retmode': 'json'})
        return result

    def _eutils_get_variant_summary(self, accession_id):
        '''returns variant summary XML (<ClinVarResult-Set>) for given ClinVar accession ID.
        (This corresponds to the entry in the clinvar.variant_summary table.)
        '''
        result = self.qs.efetch({'db': 'clinvar', 'id': accession_id, 'rettype': 'variation'})
        return result

    def _eutils_ids_by_gene(self, gene, single_gene=False):
        '''searches ClinVar for specified gene (HUGO); returns up to 500 matching results.

        :param: gene (string) - gene name in HUGO naming convention.
        :param: single_gene (bool) [default: False] - restrict results to single-gene accessions.
        :return: list of clinvar ids (strings)
        '''
        # equivalent esearch:
        # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=FGFR3[gene]&retmax=500

        result = self.qs.esearch({'db': 'clinvar', 'term': gene + '[gene]', 'single_gene': single_gene})
        dom = etree.fromstring(result)
        ids = []
        idlist = dom.find('IdList')
        for item in idlist.findall('Id'):
            ids.append(item.text.strip())
        return ids
    
    def _eutils_pmids_for_id(self, clinvar_id):
        '''returns pubmed IDs associated with this ClinVar accession ID.

        example:
        https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=clinvar&db=pubmed&id=9

        :param: clinvar_id (integer or string)
        :return: list of pubmed IDs (strings)
        '''
        xmlstr = self.qs.elink({'dbfrom': 'clinvar', 'id': clinvar_id, 'db': 'pubmed'})
        return parse_elink_response(xmlstr)

    def _eutils_ids_for_variant(self, hgvs_c):
        '''returns ClinVar IDs for given HGVS c. string

        :param: hgvs_c (string)
        :return: list of pubmed IDs (strings)
        '''
        result = self.qs.esearch({'db': 'clinvar', 'term': '"%s"' % hgvs_c})
        dom = etree.fromstring(result)
        ids = []
        idlist = dom.find('IdList')
        for item in idlist.findall('Id'):
            ids.append(item.text.strip())
        return ids

    def _eutils_variant2pubmed(self, hgvs_c):
        '''returns pubmed IDs for given HGVS c. string

        :param: hgvs_c (string)
        :return: list of pubmed IDs (strings)
        '''
        ids = self._eutils_ids_for_variant(hgvs_c)
        if len(ids) > 1:
            print('Warning: more than one ClinVar id returned for term %s' % hgvs_c)
        pmids = []
        for clinvar_id in ids:
            pmids = pmids + self._eutils_pmids_for_id(clinvar_id)
        return pmids
