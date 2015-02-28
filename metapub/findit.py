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
simple_formats = {
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

    'JAMA': 'http://jama.ama-assn.org/content/{a.pii}.full.pdf',
    'N. Engl. J. Med.':  'http://www.nejm.org/doi/pdf/{a.doi}',
    }

# vip = Volume-Issue-Page format -- URLs that have the same format
# except for the host name
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


PMC_PDF_URL = 'http://www.ncbi.nlm.nih.gov/pmc/articles/pmid/{pmid}/pdf'

def find_it(pma):
    if pma.pmc:
        return PMC_PDF_URL.format(pma)
        
    elif pma.journal in simple_formats.keys():
        return simple_formats[self.journal].format(a=pma)

    elif self.journal in vip_journals.keys():
        return vip_format.format(host=vip_journals[self.journal]['host'], a=pma)

    elif self.journal in nature_journals.keys():
        return nature_format.format(a=pma, ja=nature_journals[self.journal]['ja'])

    elif self.journal in cell_journals.keys() and pma.pii:
        return cell_format.format(a=pma, ja=cell_journals[self.journal]['ja'],
                pii=pma.pii.translate(None,'-()') ) 
    
    elif self.journal in 'Lancet':
        return 'http://download.thelancet.com/pdfs/journals/lancet/PII{piit}.pdf'.format(
            piit = self.pii.replace(None,'-()'))

    else:
        return None


