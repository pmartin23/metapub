from __future__ import absolute_import

"""metapub.medgenconcept -- MedGenConcept class instantiated by supplying ESummary XML string."""

import logging
from lxml import etree

from .base import MetaPubObject
from .exceptions import MetaPubError

logger = logging.getLogger()

class MedGenConcept(MetaPubObject):

    def __init__(self, xmlstr, *args, **kwargs):
        super(MedGenConcept, self).__init__(xmlstr, 'DocumentSummarySet/DocumentSummary', args, kwargs)

        if self._get('error'):
            raise MetaPubError('Supplied XML for MedGenConcept contained explicit error: %s' % self._get('error') )

        # ConceptMeta is an XML document embedded within the XML response. Boo-urns. 
        self.meta = etree.fromstring('<ConceptMeta>'+self.content.find('ConceptMeta').text+'</ConceptMeta>')

    @property
    def cui(self):
        return self._get('ConceptId')
    
    @property
    def title(self):
        return self._get('Title')
        
    @property
    def definition(self):
        return self._get('Definition')
    
    @property
    def semantic_id(self):
        return self._get('SemanticId')
    
    @property
    def semantic_type(self):
        return self._get('SemanticType')
        
    @property
    def modes_of_inheritance(self):
        '''returns a list of all known ModesOfInheritance, in format:
        [ { 'cui': 'CNxxxx', 'name': 'some name' }, { }  ]
        '''
        modes = []
        try:
            for item in self.meta.find('ModesOfInheritance').getchildren():
                modes.append({ 'cui': item.get('CUI'), 'name': item.find('Name').text })
            return modes
        except AttributeError:
            return None
    

    # TODO
    # ModesOfInheritance
    # <ModesOfInheritance><ModeOfInheritance uid="425042" CUI="CN001297" TUI="T045"><Name>X-linked recessive inheritance</Name><SemanticType>Genetic Function</SemanticType><Definition>A mode of inheritance that is observed for recessive traits related to a gene encoded on the X chromosome. In the context of medical genetics, X-linked recessive disorders manifest in males (who have one copy of the X chromosome and are thus hemizygotes), but generally not in female heterozygotes who have one mutant and one normal allele.</Definition></ModeOfInheritance></ModesOfInheritance>
    
    # TODO
    # Names
    # <Names><Name SDUI="300555" CODE="300555" SAB="OMIM" TTY="PT" type="syn">DENT DISEASE 2</Name><Name SDUI="C564487" SCUI="M0564787" CODE="C564487" SAB="MSH" TTY="NM" type="syn">Dent Disease 2</Name><Name SDUI="GTRT000001952" CODE="AN0084357" SAB="GTR" TTY="PT" type="preferred">Dent disease 2</Name><Name SDUI="GTRT000001952" CODE="AN0348120" SAB="GTR" TTY="SYN" type="syn">Dent Disease Type II</Name><Name SDUI="Orphanet_93623" CODE="AN0449423" SAB="ORDO" TTY="PT" type="syn">Dent disease type 2</Name><Name SDUI="Orphanet_93623" CODE="AN0470672" SAB="ORDO" TTY="SYN" type="syn">Nephrolithiasis type 2</Name></Names>
    
    # TODO
    # Definitions
    # <Definitions><Definition source="GeneReviews">Dent disease, an X-linked disorder of proximal renal tubular dysfunction, is characterized by low molecular-weight (LMW) proteinuria, hypercalciuria, nephrocalcinosis, nephrolithiasis, and chronic kidney disease (CKD). Males younger than age ten years may manifest only low molecular-weight (LMW) proteinuria and/or hypercalciuria, which are usually asymptomatic. Thirty to 80% of affected males develop end-stage renal disease (ESRD) between ages 30 and 50 years; in some instances ESRD does not develop until the sixth decade of life or later. Rickets or osteomalacia are occasionally observed, and mild short stature, although underappreciated, may be a common occurrence. Disease severity can vary within the same family. Males with Dent disease 2 (caused by mutation of OCRL) are at increased risk for intellectual disability. Due to random X-chromosome inactivation, some female carriers may manifest hypercalciuria and, rarely, renal calculi and moderate LMW proteinuria. Females rarely if ever develop CKD.</Definition></Definitions>
    
    # TODO
    # Chromosome
    # <Chromosome>X</Chromosome>
    
    # TODO
    # Cytogenic
    # <Cytogenetic>Xq26.1</Cytogenetic>
    
    # TODO
    # ClinicalFeatures / ClinicalFeature
    # <ClinicalFeatures><ClinicalFeature uid="9232" CUI="C0019322" TUI="T190" SDUI="HP:0001537"><Name>Umbilical hernia</Name><SemanticType>Anatomical Abnormality</SemanticType></ClinicalFeature><ClinicalFeature uid="87607" CUI="C0349588" TUI="T033" SDUI="HP:0004322"><Name>Short stature</Name><SemanticType>Finding</SemanticType></ClinicalFeature><ClinicalFeature uid="333360" CUI="C1839606" TUI="T033" SDUI="HP:0003126"><Name>Low-molecular-weight proteinuria</Name><SemanticType>Finding</SemanticType></ClinicalFeature><ClinicalFeature uid="383844" CUI="C1856145" TUI="T033" SDUI="HP:0100543"><Name>Cognitive impairment</Name><SemanticType>Finding</SemanticType></ClinicalFeature><ClinicalFeature uid="349145" CUI="C1859342" TUI="T033" SDUI="HP:0000114"><Name>Proximal tubulopathy</Name><SemanticType>Finding</SemanticType></ClinicalFeature><ClinicalFeature uid="504348" CUI="CN000117" TUI="T033" SDUI="HP:0000121"><Name>Nephrocalcinosis</Name><SemanticType>Finding</SemanticType><Definition>Nephrocalcinosis is the deposition of calcium salts in renal parenchyma.</Definition></ClinicalFeature><ClinicalFeature uid="504774" CUI="CN001157" TUI="T033" SDUI="HP:0001263"><Name>Global developmental delay</Name><SemanticType>Finding</SemanticType><Definition>A delay in the achievement of motor or mental milestones in the domains of development of a child, including motor skills, speech and language, cognitive skills, and social and emotional skills. This term should only be used to describe children younger than five years of age.</Definition></ClinicalFeature><ClinicalFeature uid="505127" CUI="CN001948" TUI="T033" SDUI="HP:0002150"><Name>Hypercalciuria</Name><SemanticType>Finding</SemanticType></ClinicalFeature><ClinicalFeature uid="505493" CUI="CN002923" TUI="T033" SDUI="HP:0003236"><Name>Elevated serum creatine phosphokinase</Name><SemanticType>Finding</SemanticType><Definition>An elevation of the level of the enzyme creatine kinase (also known as creatine phosphokinase, CPK; EC 2.7.3.2) in the blood. CPK levels can be elevated in a number of clinical disorders such as myocardial infarction, rhabdomyolysis, and muscular dystrophy.</Definition></ClinicalFeature><ClinicalFeature uid="425142" CUI="CN003029" TUI="T033" SDUI="HP:0003355"><Name>Aminoaciduria</Name><SemanticType>Finding</SemanticType><Definition>An increased concentration of an amino acid in the urine.</Definition></ClinicalFeature><ClinicalFeature uid="776439" CUI="CN183891" TUI="T033" SDUI="HP:0012622"><Name>Chronic kidney disease</Name><SemanticType>Finding</SemanticType><Definition>Functional anomaly of the kidney persisting for at least three months.</Definition></ClinicalFeature></ClinicalFeatures><PhenotypicAbnormalities><Category CUI="CN000115" name="Abnormality of the genitourinary system"><ClinicalFeature uid="504348" CUI="CN000117" TUI="T033" SDUI="HP:0000121"><SemanticType>Finding</SemanticType><Name>Nephrocalcinosis</Name><Definition>Nephrocalcinosis is the deposition of calcium salts in renal parenchyma.</Definition></ClinicalFeature><ClinicalFeature uid="425142" CUI="CN003029" TUI="T033" SDUI="HP:0003355"><SemanticType>Finding</SemanticType><Name>Aminoaciduria</Name><Definition>An increased concentration of an amino acid in the urine.</Definition></ClinicalFeature><ClinicalFeature uid="776439" CUI="CN183891" TUI="T033" SDUI="HP:0012622"><SemanticType>Finding</SemanticType><Name>Chronic kidney disease</Name><Definition>Functional anomaly of the kidney persisting for at least three months.</Definition></ClinicalFeature></Category><Category CUI="CN000664" name="Abnormality of the nervous system"><ClinicalFeature uid="504774" CUI="CN001157" TUI="T033" SDUI="HP:0001263"><SemanticType>Finding</SemanticType><Name>Global developmental delay</Name><Definition>A delay in the achievement of motor or mental milestones in the domains of development of a child, including motor skills, speech and language, cognitive skills, and social and emotional skills. This term should only be used to describe children younger than five years of age.</Definition></ClinicalFeature></Category><Category CUI="CN001754" name="Abnormality of metabolism/homeostasis"><ClinicalFeature uid="505493" CUI="CN002923" TUI="T033" SDUI="HP:0003236"><SemanticType>Finding</SemanticType><Name>Elevated serum creatine phosphokinase</Name><Definition>An elevation of the level of the enzyme creatine kinase (also known as creatine phosphokinase, CPK; EC 2.7.3.2) in the blood. CPK levels can be elevated in a number of clinical disorders such as myocardial infarction, rhabdomyolysis, and muscular dystrophy.</Definition></ClinicalFeature><ClinicalFeature uid="425142" CUI="CN003029" TUI="T033" SDUI="HP:0003355"><SemanticType>Finding</SemanticType><Name>Aminoaciduria</Name><Definition>An increased concentration of an amino acid in the urine.</Definition></ClinicalFeature>
    
    # TODO
    # PhenotypicAbnormalities 
    # <PhenotypicAbnormalities><Category CUI="CN000115" name="Abnormality of the genitourinary system"><ClinicalFeature uid="504348" CUI="CN000117" TUI="T033" SDUI="HP:0000121"><SemanticType>Finding</SemanticType><Name>Nephrocalcinosis</Name><Definition>Nephrocalcinosis is the deposition of calcium salts in renal parenchyma.</Definition></ClinicalFeature><ClinicalFeature uid="425142" CUI="CN003029" TUI="T033" SDUI="HP:0003355"><SemanticType>Finding</SemanticType><Name>Aminoaciduria</Name><Definition>An increased concentration of an amino acid in the urine.</Definition></ClinicalFeature><ClinicalFeature uid="776439" CUI="CN183891" TUI="T033" SDUI="HP:0012622"><SemanticType>Finding</SemanticType><Name>Chronic kidney disease</Name><Definition>Functional anomaly of the kidney persisting for at least three months.</Definition></ClinicalFeature></Category><Category CUI="CN000664" name="Abnormality of the nervous system"><ClinicalFeature uid="504774" CUI="CN001157" TUI="T033" SDUI="HP:0001263"><SemanticType>Finding</SemanticType><Name>Global developmental delay</Name><Definition>A delay in the achievement of motor or mental milestones in the domains of development of a child, including motor skills, speech and language, cognitive skills, and social and emotional skills. This term should only be used to describe children younger than five years of age.</Definition></ClinicalFeature></Category><Category CUI="CN001754" name="Abnormality of metabolism/homeostasis"><ClinicalFeature uid="505493" CUI="CN002923" TUI="T033" SDUI="HP:0003236"><SemanticType>Finding</SemanticType><Name>Elevated serum creatine phosphokinase</Name><Definition>An elevation of the level of the enzyme creatine kinase (also known as creatine phosphokinase, CPK; EC 2.7.3.2) in the blood. CPK levels can be elevated in a number of clinical disorders such as myocardial infarction, rhabdomyolysis, and muscular dystrophy.</Definition></ClinicalFeature><ClinicalFeature uid="425142" CUI="CN003029" TUI="T033" SDUI="HP:0003355"><SemanticType>Finding</SemanticType><Name>Aminoaciduria</Name><Definition>An increased concentration of an amino acid in the urine.</Definition></ClinicalFeature></Category></PhenotypicAbnormalities>

    # TODO
    # Associated Genes / Gene
    # <AssociatedGenes><Gene gene_id="4952" chromosome="X" cytogen_loc="Xq26.1">OCRL</Gene></AssociatedGenes>
    # 
    
    # TODO
    # <RelatedDisorders></RelatedDisorders>
    
    # TODO
    # <SNOMEDCT></SNOMEDCT>
    
    # known others not planned for inclusion:
    # <PharmacologicResponse></PharmacologicResponse>
    