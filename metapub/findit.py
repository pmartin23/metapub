from __future__ import absolute_import

import requests

from .pubmedfetcher import PubMedFetcher
from .convert import PubMedArticle2doi, doi2pmid
from .exceptions import MetaPubError
from .text_mining import re_numbers

fetch = PubMedFetcher()

oa_journals = (
    # open access journals (always free, everywhere, the way it should be)

    # ISOAbbreviations:
    'PLoS Biol.',
    'PLoS Comput. Biol.',
    'PLoS Genet.',
    'PLoS Med.',
    'PLoS ONE',
    'PLoS Pathog.',

    # non ISOAbbreviations:
    'BMC cancer',
    'BMC bioinformatics',
    'BMC genetics',
    )

format_templates = {
    'wiley': 'http://onlinelibrary.wiley.com/doi/{a.doi}/pdf',
    'plos': 'http://www.plosbiology.org/article/fetchObjectAttachment.action?url=info:doi/{a.doi}&representation=PDF',
    'informa': 'http://informahealthcare.com/doi/abs/{a.doi}', 
    'ats': 'http://www.atsjournals.org/doi/pdf/{a.doi}', 
    }

# simple formats are used for URLs that can be deduced from data
# in the pubmed record
simple_formats_doi = {
    'Am. J. Med. Genet. A': format_templates['wiley'],
    'Am. J. Med. Genet.': format_templates['wiley'],
    'Ann. Neurol.': format_templates['wiley'],
    'Clin. Genet.': format_templates['wiley'],
    'Genes Chromosomes Cancer': format_templates['wiley'],
    'Genet. Epidemiol.': format_templates['wiley'],
    'Hum. Mutat.': format_templates['wiley'],
    'Int. J. Cancer': format_templates['wiley'],
    'Proteins': format_templates['wiley'],
    'J. Thromb. Haemost.': format_templates['wiley'],
    'Am J Med Genet B Neuropsychiatr Genet.': format_templates['wiley'],

    'Hemoglobin': format_templates['informa'],

    'Am. J. Respir. Cell Mol. Biol.': format_templates['ats'],

    'PLoS Biol.': format_templates['plos'],
    'PLoS Comput. Biol.': format_templates['plos'],
    'PLoS Genet.': format_templates['plos'],
    'PLoS Med.': format_templates['plos'],
    'PLoS ONE.': format_templates['plos'],
    'PLoS Pathog.': format_templates['plos'],
    'N. Engl. J. Med.':  'http://www.nejm.org/doi/pdf/{a.doi}',
    }

simple_formats_pii = {
    'JAMA': 'http://jama.ama-assn.org/content/{a.pii}.full.pdf',
    'Gastroenterology': 'http://www.gastrojournal.org/article/{a.pii}/pdf',
    } 

# vip = Volume-Issue-Page format -- URLs that have the same format
# except for the host name

# http://www.bloodjournal.org/content/117/5/1622.full.pdf

vip_format = 'http://{host}/content/{a.volume}/{a.issue}/{a.first_page}.full.pdf'

vip_journals = {
        'Ann Oncol' : {'host' : 'annonc.oxfordjournals.org'},
        'Arterioscler Thromb Vasc Biol' : {'host' : 'atvb.ahajournals.org'},
        'Blood': { 'host': 'bloodjournal.org' }, #'bloodjournal.hematologylibrary.org' },
        'Brain': { 'host': 'brain.oxfordjournals.org' },
        'Breast Cancer Res' : { 'host': 'breast-cancer-research.com' },
        'Cancer Discov' : {'host': 'cancerdiscovery.aacrjournals.org'},
        'Cancer Res': { 'host': 'cancerres.aacrjournals.org' },
        'Cardiovasc Res' : {'host' : 'cardiovascres.oxfordjournals.org'},
        'Circulation': { 'host': 'circ.ahajournals.org' },
        'Circ Cardiovasc Genet' : {'host' : 'circgenetics.ahajournals.org'},
        'Circ Res' : {'host' : 'circres.ahajournals.org'},
        'Clin Cancer Res' : {'host' : 'clincancerres.aacrjournals.org'},
        'Clin Chem' : {'host' : 'clinchem.org'},
        'Eur Heart J' : {'host' : 'eurheartj.oxfordjournals.org'},
        'Eur J Endocrinol' : {'host' : 'eje-online.org'},
        'FASEB J' : {'host' : 'fasebj.org'},
        'Genome Biol' : { 'host' : 'genomebiology.com'},
        'Genes Dev' : {'host': 'genesdev.cshlp.org'},
        'Gut' : {'host' : 'gut.bmj.com'},
        'Haematologica' : {'host' : 'haematologica.org'},
        'Hum Mol Genet': { 'host': 'hmg.oxfordjournals.org' },
        'Int J Oncol' : {'host' : 'spandidos-publications.com/ijo/'},
        'IOVS' : {'host' : 'iovs.org'},
        'J Am Soc Nephrol' : {'host' : 'jasn.asnjournals.org'},
        'J Biol Chem': { 'host': 'www.jbc.org' },
        'J Cell Biol' : {'host' : 'jcb.rupress.org'},
        'J Cell Sci' : {'host' : 'jcs.biologists.org'},
        'J Clin Endocrinol Metab': { 'host': 'jcem.endojournals.org' },
        'J Clin Oncol': { 'host': 'jco.ascopubs.org' },
        'J Immunol' : {'host' : 'jimmunol.org'},
        'J Neurosci' : {'host' : 'jneurosci.org'},
        'J Med Genet': { 'host': 'jmg.bmj.com' },
        'Mol Biol Cell' : {'host' : 'molbiolcell.org'},
        'Mol Cell Biol' : {'host': 'mcb.asm.org'},
        'Mol Canc Therapeut' : {'host' : 'mct.aacrjournals.org'},
        'Mol Pharmacol': {'host' : 'molpharm.aspetjournals.org'},
        'Neurology' : {'host' : 'neurology.org'},
        'Nucleic Acids Res' : {'host' : 'nar.oxfordjournals.org'},
        'Oncol Lett' : {'host' : 'spandidos-publications.com/ol/'},
        'Oncol Rep' : {'host' : 'spandidos-publications.com/or/'},
        'Orphanet J Rare Dis' : {'host' : 'ojrd.com'},
        'Proc Natl Acad Sci USA': { 'host': 'pnas.org'},
        'Science': { 'host': 'sciencemag.org' }
        }




# cell journals
#cell_format = 'http://download.cell.com{ja}/pdf/PII{pii}.pdf'
cell_format = 'http://www.cell.com{ja}/pdf/{pii}.pdf'
cell_journals = {
    'Am. J. Hum. Genet.': { 'ja': '/AJHG' },
    'Cell': { 'ja': '' },
    }

# nature journals
nature_format = 'http://www.nature.com/{ja}/journal/v{a.volume}/n{a.issue}/pdf/{a.pii}.pdf'
nature_journals = {
    'Nature': { 'ja': 'nature' },
    'Nat. Genet.': { 'ja': 'ng' },
    'Nat. Neurosci.': { 'ja': 'neuro' },
    'Nat. Methods': { 'ja': 'nmeth' },
    'Nat. Rev. Genet.': { 'ja': 'nrg' },
    'Nature reviews. Immunology': { 'ja': 'nri' },
    'Eur. J. Hum. Genet.': { 'ja': 'ejhg' },
    'J. Hum. Genet.': { 'ja': 'jhg' },
    }

# TODO
#
# 15611820: no URL because No URL format for Journal Arq Bras Endocrinol Metabol
# 15611833: no URL because No URL format for Journal Arq Bras Endocrinol Metabol
# 15611902: no URL because No URL format for Journal Laryngorhinootologie
# 15613099: no URL because No URL format for Journal Eur. J. Haematol.
# 17486372: no URL because No URL format for Journal Pediatr. Nephrol.
# 17486493: no URL because No URL format for Journal Hemoglobin
# 17516458: no URL because No URL format for Journal Mov. Disord.
# 17516465: no URL because No URL format for Journal Mov. Disord.

"""
17319787: no URL because No URL format for Journal Neoplasma
17319828: no URL because No URL format for Journal Transfusion
17319831: no URL because No URL format for Journal Transfusion
17320181: no URL because No URL format for Journal Ophthalmology
17321228: no URL because No URL format for Journal Bone
17099210: no URL because No URL format for Journal Hum. Reprod.
17100396: no URL because No URL format for Journal J Med Assoc Thai
17413420: no URL because No URL format for Journal Genet. Med.
17413421: no URL because No URL format for Journal Genet. Med.
17413422: no URL because No URL format for Journal Genet. Med.
17413424: no URL because No URL format for Journal Genet. Med.
17413447: no URL because No URL format for Journal Psychiatr. Genet.
17414143: no URL because No URL format for Journal J. Pediatr. Gastroenterol. Nutr.
17415510: no URL because No URL format for Journal J. Neurol.
17415538: no URL because No URL format for Journal HNO
17415575: no URL because No URL format for Journal Arch. Dermatol. Res.
17415800: no URL because No URL format for Journal Mov. Disord.
17416296: no URL because No URL format for Journal Arch. Med. Res.
"""

# Journals with really annoying paywalls guarding their precious secrets.
schattauer_journals = [
    'Thromb Haemost.',
    ]

springer_journals = [
    'Physiol Genomics.',
    ]


PMC_PDF_URL = 'http://www.ncbi.nlm.nih.gov/pmc/articles/pmid/{a.pmid}/pdf'

def find_article_from_doi(doi):
    #1) lookup on CrossRef
    #2) pull a PubMedArticle based on CrossRef results
    #3) run it through find_article_from_pma
    pma = fetch.article_by_pmid(doi2pmid(doi))
    return find_article_from_pma(pma)
    


# TODO: support this madness (http://www.ncbi.nlm.nih.gov/books/NBK3828/):

"""
How do I submit tags for Volume and Issue Supplements?

Use the following guidelines for Supplements:

Supplement 1 for Volume 6:

 <Volume>6 Suppl 1</Volume>
<Issue></Issue> 
Issue 4, Supplement 2 for Volume 7:

<Volume>7</Volume>
<Issue>4 Suppl 2</Issue> 
Issue 4 Pt 1 for Volume 7:

<Volume>7</Volume>
<Issue>4 Pt 1</Issue> 
Issue Part 3 for Volume 7 (it has Volume 7 Part 3 on the cover):

<Volume>7</Volume>
<Issue>Pt 3</Issue>
"""



def find_article_from_pma(pma, crossref_doi=True):
    reason = None
    url = None

    if pma.pmc:
        url = PMC_PDF_URL.format(a=pma)
        
    elif pma.journal in simple_formats_doi.keys():
        if pma.doi == None:
            if crossref_doi:
                pma.doi = PubMedArticle2doi(pma)
                if pma.doi is None:
                    reason = 'No DOI: missing from PubMedArticle and CrossRef lookup failed.' 
            else:
                reason = 'No DOI: missing from PubMedArticle and CrossRef lookup failed.' 
        
        if pma.doi != None:
            url = simple_formats_doi[pma.journal].format(a=pma)

    elif pma.journal in simple_formats_pii.keys():
        if pma.pii:
            url = simple_formats_pii[pma.journal].format(a=pma)
        else:
            reason = 'pii missing from PubMedArticle XML'

    elif pma.journal in vip_journals.keys():
        # TODO: catch weird stuff like these results from PMID 10071047:
        #   http://brain.oxfordjournals.org/content/122 ( Pt 2)/None/183.full.pdf
        # (working URL = http://brain.oxfordjournals.org/content/brain/122/2/183.full.pdf )
        if pma.volume != None and pma.issue is None:
            # try to get a number out of the parts that came after the first number.
            volparts = re_numbers.findall(pma.volume)
            if volparts > 1:
                pma.volume = volparts[0]
                # take a guess. best we can do. this often works (e.g. Brain journal)
                pma.issue = volparts[1]
            else:
                reason = 'issue data missing (volume: %s, issue: %s)' % (pma.volume, pma.issue)

        
        if pma.issue and pma.volume:
            if pma.issue.find('Pt') > -1:
                pma.issue = re_numbers.findall(pma.issue)[0]
            url = vip_format.format(host=vip_journals[pma.journal]['host'], a=pma)
        else:
            reason = 'volume and maybe also issue data missing'


    elif pma.journal in nature_journals.keys():
        if pma.pii:
            url = nature_format.format(a=pma, ja=nature_journals[pma.journal]['ja'])
        else:
            reason = 'pii missing from PubMedArticle XML'

    elif pma.journal in cell_journals.keys():
        if pma.pii:
            url = cell_format.format( a=pma, ja=cell_journals[pma.journal]['ja'],
                    pii=pma.pii.translate(None,'-()') )
        else:
            reason = 'pii missing from PubMedArticle XML'
    
    elif pma.journal in 'Lancet' and pma.pii is not None:
        url = 'http://download.thelancet.com/pdfs/journals/lancet/PII{piit}.pdf'.format(piit = pma.pii.translate(None,'-()'))

    else:
        reason = 'No URL format for Journal %s' % pma.journal

    return (url, reason)


class FindIt(object):

    @classmethod
    def by_pmid(cls, pmid, *args, **kwargs):
        kwargs['pmid'] = pmid
        return cls(args, kwargs)

    @classmethod
    def by_doi(cls, doi, *args, **kwargs):
        kwargs['doi'] = doi
        return cls(args, kwargs)
    
    def __init__(self, *args, **kwargs):    
        self.pmid = kwargs.get('pmid', None)
        self.doi = kwargs.get('doi', None)
        self.url = kwargs.get('url', None)
        self.reason = None

        self.pma = None
        #self.cr_top_result = None

        if self.pmid:
            self.pma = fetch.article_by_pmid(self.pmid)
            self.url, self.reason = find_article_from_pma(self.pma)

        elif self.doi:
            self.url, self.reason = find_article_from_doi(self.doi)


    def download(self, filename):
        # verify=False means it ignores bad SSL certs
        response = requests.get(url, stream=True, timeout=CURL_TIMEOUT, verify=False)

        if not response.ok:
            return 'error'

        if response.status_code == 200:
            if response.headers.get('content-type')=='application/pdf':
                with open(filename, 'wb') as handle:
                    for block in response.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)
            return response.headers.get('content-type')
        else:
            return response.status_code


    def verify(self, pdf2txt=False):
        '''verify that download was indeed a PDF. If pdf2txt is True, convert PDF to text for further validation.

            returns confidence score from 1 to 10 (10 being highest confidence that PDF is in fact the 
            desired article.)'''


