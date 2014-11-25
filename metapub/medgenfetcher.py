from __future__ import absolute_import

"""metapub.MedGenFetcher -- tools to deal with NCBI's E-utilities interface to the MedGen db"""

from lxml import etree

from .exceptions import MetaPubError
from .medgenconcept import MedGenConcept
from .utils import Borg

class MedGenFetcher(Borg):
    '''PubMedFetcher (a Borg singleton object)

    An interaction layer for querying via specified method to return PubMedArticle objects.
    
    Currently available methods: eutils

    Basic Usage:

        fetch = PubMedFetcher()
    
    To specify a service method (more coming soon):

        fetch = PubMedFetcher('eutils')

    To return an article by querying the service with a known PMID:

        paper = fetch.article_by_pmid('123456')

    Similar methods exist for returning papers by DOI and PM Central id:

        paper = fetch.article_by_doi('10.1038/ng.379')
        paper = fetch.article_by_pmcid('PMC3458974')
    '''

    def __init__(self, method='eutils'):
        Borg.__init__(self)
        self.method = method

        if method=='eutils':
            import eutils.client as ec
            self.qs = ec.QueryService()
            self.ids_by_term = self._eutils_ids_by_term
            self.concept_by_id = self._eutils_concept_by_id
            self.id_for_cuid = self._eutils_id_for_cuid
        else:
            raise NotImplementedError('coming soon: fetch from local medgen via medgen-mysql.')

    def _eutils_ids_by_term(self, term):
        '''wraps results of an medgen efetch term lookup, returning IDs of related MedGenConcepts.
        
        :return: list of medgen ids (strings)
        '''
        # http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=medgen&term=OCRL
        result = self.qs.esearch( { 'db': 'medgen', 'term': term } )
        dom = etree.fromstring(result)
        ids = []
        idlist = dom.find('IdList')
        for item in idlist.findall('Id'):
            ids.append(item.text.strip())
        return ids
    
    def _eutils_concept_by_id(self, id):
        '''wraps results of an esummary fcgi call to medgen when ID is known.
        
        :return: MedGenConcept object
        '''
        # http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=medgen&id=336867
        id = str(id)
        result = self.qs.esummary( { 'db': 'medgen', 'id': id } )
        return MedGenConcept(result)

    def _eutils_id_for_cuid(self, cuid):
        '''given a ConceptID (cuid), return a medgen ID.'''
        #http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=medgen&term=C0000039
        if not cuid.startswith('C'):
            raise MetaPubError('Invalid CUID: must start with C (e.g. C0000039)')

        result = self.qs.esearch( { 'db': 'medgen', 'term': cuid } )
        dom = etree.fromstring(result)
        try:
            cuid = dom.find('IdList').find('Id').strip()
        except AttributeError:
            raise MetaPubError('Invalid CUID: did not return MedGen id.')
        return cuid

