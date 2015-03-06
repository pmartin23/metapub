from __future__ import absolute_import

import requests

from .pubmedfetcher import PubMedFetcher
from .convert import PubMedArticle2doi, doi2pmid
from .exceptions import MetaPubError

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
    }


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
            volparts = pma.volume.replace('(', ' ').replace(')', ' ').split()
            if volparts > 1:
                pma.volume = volparts[0]
            for item in volparts[1:]:
                try:
                    int(item)
                    pma.issue = item
                except:
                    pass
        
        if pma.issue and pma.volume:
            url = vip_format.format(host=vip_journals[pma.journal]['host'], a=pma)
        else:
            reason = 'volume and/or issue data missing from PubMedArticle XML'


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


