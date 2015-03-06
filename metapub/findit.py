from __future__ import absolute_import

import requests

from .pubmedfetcher import PubMedFetcher
from .convert import PubMedArticle2doi
from .exceptions import MetaPubError

"""
When fulfilling orders for articles listed in pubmed, follow these heuristics:
(assuming a valid PubMedArticle object as "pma")
1) if pma.pmc, return PMC url to pdf
2) if pma.journal in oa_journals, return journal_pdf_url
3) if pma.journal in subs_journals, return journal_pdf_url
3.1) Fail: if pma.pii is missing
3.2) Fail: if journal_pdf_url send back HTML text (e.g. an order page) instead of a PDF.
last) order from reprintsdesk
"""

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
    'plos': 'http://www.plosbiology.org/article/fetchObjectAttachment.action?uri=info:doi/{a.doi}&representation=PDF',
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
    } 

# vip = Volume-Issue-Page format -- URLs that have the same format
# except for the host name

# http://www.bloodjournal.org/content/117/5/1622.full.pdf

vip_format = 'http://{host}/content/{a.volume}/{a.issue}/{a.first_page}.full.pdf'
vip_journals = {
    'Blood': { 'host': 'bloodjournal.hematologylibrary.org' },
    'Brain': { 'host': 'brain.oxfordjournals.org' },
    'Cancer Res.': { 'host': 'cancerres.aacrjournals.org' },
    'Circulation': { 'host': 'circ.ahajournals.org' },
    'Hum. Mol. Genet.': { 'host': 'hmg.oxfordjournals.org' },
    'J. Biol. Chem.': { 'host': 'www.jbc.org' },
    'J. Clin. Endocrinol. Metab.': { 'host': 'jcem.endojournals.org' },
    'J. Clin. Oncol.': { 'host': 'jco.ascopubs.org' },
    'J. Med. Genet.': { 'host': 'jmg.bmj.com' },
    'Proc. Natl. Acad. Sci. U.S.A.': { 'host': 'www.pnas.org' },
    'Science': { 'host': 'www.sciencemag.org' },
    }

# cell journals
cell_format = 'http://download.cell.com{ja}/pdf/PII{pii}.pdf'
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
    }


PMC_PDF_URL = 'http://www.ncbi.nlm.nih.gov/pmc/articles/pmid/{a.pmid}/pdf'

def find_from_pma(pma, crossref_doi=True):
    reason = None
    uri = None

    if pma.pmc:
        uri = PMC_PDF_URL.format(a=pma)
        
    elif pma.journal in simple_formats_doi.keys():
        if pma.doi == None:
            if crossref_doi:
                pma.doi = PubMedArticle2doi(pma)
                if pma.doi is None:
                    reason = 'No DOI: missing from PubMedArticle and CrossRef lookup failed.' 
            else:
                reason = 'No DOI: missing from PubMedArticle and CrossRef lookup failed.' 
        
        if pma.doi != None:
            uri = simple_formats_doi[pma.journal].format(a=pma)

    elif pma.journal in simple_formats_pii.keys() and pma.pii != None:
        uri = simple_formats_pii[pma.journal].format(a=pma)

    elif pma.journal in vip_journals.keys():
        uri = vip_format.format(host=vip_journals[pma.journal]['host'], a=pma)

    elif pma.journal in nature_journals.keys():
        uri = nature_format.format(a=pma, ja=nature_journals[pma.journal]['ja'])

    elif pma.journal in cell_journals.keys() and pma.pii:
        uri = cell_format.format( a=pma, ja=cell_journals[pma.journal]['ja'],
                pii=pma.pii.translate(None,'-()') )
    
    elif pma.journal in 'Lancet' and pma.pii:
        uri = 'http://download.thelancet.com/pdfs/journals/lancet/PII{piit}.pdf'.format(piit = pma.pii.replace(None,'-()'))

    return (uri, reason)


class FindIt(object):

    @classmethod
    def by_pmid(cls, pmid, **kwargs):
        kwargs['pmid'] = pmid
        return cls(**kwargs)

    @classmethod
    def by_doi(cls, doi, **kwargs):
        return cls(doi=doi, 
    
    def __init__(self, *args, **kwargs):    
        self.pmid = kwargs.get('pmid', None)
        self.doi = kwargs.get('doi', None)
        self.uri = kwargs.get('uri', None)
        self.reason = None

        self.pma = None
        self.cr_top_result = None

        if self.pmid:
            self.pma = fetch.article_by_pmid(pmid)
            self.uri, self.reason = find_from_pma(self.pma)

        elif self.doi:
            results = CR.query(self.doi)
            self.cr_top_result = CR.get_top_result(results)
            if self.cr_top_result is not None:


    def download(self, filename):
        # verify=False means it ignores bad SSL certs
        response = requests.get(uri, stream=True, timeout=CURL_TIMEOUT, verify=False)

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


