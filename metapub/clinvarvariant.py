from __future__ import absolute_import, unicode_literals

"""metapub.clinvarvariant -- ClinVarVariant class instantiated by supplying ESummary XML string."""

import logging
from datetime import datetime

from lxml import etree

from .base import MetaPubObject
from .exceptions import MetaPubError

logger = logging.getLogger()


class ClinVarVariant(MetaPubObject):

    def __init__(self, xmlstr, *args, **kwargs):
        super(ClinVarVariant, self).__init__(xmlstr, 'VariationReport', args, kwargs)

        if self._get('error'):
            raise MetaPubError('Supplied XML for ClinVarVariant contained explicit error: %s' % self._get('error'))
    
        # VariationReport basic details
        self.id = self._get_variation_id()
        self.name = self._get_variation_name()
        self.type = self._get_variation_type()
        self.date_created = self._get_date_created()
        self.date_last_updated = self._get_date_last_updated()
        self.submitter_count = self._get_submitter_count()

        # Species Info
        self.species = self._get('Species')
        self.taxonomy_id = self.content.find('Species').get('TaxonomyId')

        # Gene List
        self.genes = self._get_gene_list()


    def to_dict(self):
        """ returns a dictionary composed of all extractable properties of this concept. """
        outd = self.__dict__.copy()
        outd.pop('content')
        return outd

    ### convenience properties

    @property
    def hgvs_c(self):
        """ Returns a list of all coding HGVS strings from the Allelle data. """
        return []

    @property
    def hgvs_g(self):
        """ Returns a list of all genomic HGVS strings from the Allelle data. """
        return []
    
    @property
    def hgvs_p(self):
        """ Returns a list of all protein effect HGVS strings from the Allelle data. """
        return []

    ### VariationReport basic info

    def _get_variation_id(self):
        return self.content.get('VariationID')

    def _get_variation_name(self):
        return self.content.get('VariationName')

    def _get_variation_type(self):
        # e.g. ('VariationType', 'Simple'),
        return self.content.get('VariationType')

    def _get_date_created(self):
        # e.g. ('DateCreated', '2014-01-16'),
        datestr = self.content.get('DateCreated')
        if datestr:
            return datetime.strptime(datestr, '%Y-%m-%d')
        else:
            return None

    def _get_date_last_updated(self):
        # e.g. ('DateLastUpdated', '2016-04-10'),
        datestr = self.content.get('DateLastUpdated')
        if datestr:
            return datetime.strptime(datestr, '%Y-%m-%d')
        else:
            return None

    def _get_submitter_count(self):
        # e.g. ('SubmitterCount', '1')]
        try:
            return int(self.content.get('SubmitterCount'))
        except TypeError:
            return None

    #### GENE LIST

    def _get_gene_list(self):
        """ Returns a list of dictionaries representing each gene associated with this variant.

        Keys in gene dictionary:  'ID', 'Symbol', 'FullName', 'HGNCID', 'strand', 'Type', 'OMIM', 'Property'
        """
        #        <Gene GeneID="6261" Symbol="RYR1" FullName="ryanodine receptor 1" HGNCID="HGNC:10483" strand="+" Type="submitted">
        #           <OMIM>180901</OMIM>
        #           <Property>gene_acmg_incidental_2013</Property>
        #        </Gene>

        genes = []

        genelist = self.content.find('GeneList')
        for gene_elem in genelist.getchildren():
            genes.append(dict(gene_elem.items()))
        return genes
            
    
    ### ALLELE INFORMATION

    def _get_allele_id(self):
        return self.content.get('AlleleID')
    
    def _get_cytogenic_location(self):
        return self.content.get('Allele/CytogeneticLocation')

    
