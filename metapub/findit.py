from __future__ import absolute_import

import requests
from lxml.html import HTMLParser
from lxml import etree

from .pubmedfetcher import PubMedFetcher
from .convert import PubMedArticle2doi, doi2pmid
from .exceptions import MetaPubError
from .text_mining import re_numbers

fetch = PubMedFetcher()

DX_DOI_URL = 'http://dx.doi.org/%s'
def the_doi_2step(doi):
    response = requests.get(DX_DOI_URL % doi)
    if response.status_code == 200:
        return response.url
    else:
        raise MetaPubError('dx.doi.org lookup failed for doi %s' % doi)

sciencedirect_format = 'http://www.sciencedirect.com/science/article/pii/{piit}'
sciencedirect_journals = [
                           'Arch Pediatr',
                           'Blood Cells Mol Dis',
                           'Biochem Biophys Res Commun' ,
                           'Biochem Pharmacol',
                           'Clin Immunol',
                           'FEBS Lett',
                           'Eur J Cancer',
                           'Gene',
                           'Genomics',
                           'Hepatol Res',
                           'Hum Genet',
                           'J Am Coll Cardiol',
                           'J Mol Biol',
                           'J Neurol Sci',
                           'Neuromuscul Disord',
                           'Mol Cell Endocrinol',
                           'Mol Genet Metab',
                           'Mol Immunol',
                           'Mutat Res',
                            ]

def get_sciencedirect_pdf_url(pma):
    '''we're looking for a url that looks like this:
    http://www.sciencedirect.com/science/article/pii/S0022283601953379/pdfft?md5=07db9e1b612f64ea74872842e34316a5&pid=1-s2.0-S0022283601953379-main.pdf'''
    starturl = sciencedirect_format.format(piit = pma.pii.translate(None,'-()'))
    r = requests.get(starturl)
    tree = etree.fromstring(r.text, HTMLParser())
    div = tree.cssselect('div.icon_pdf')[0]
    url = div.cssselect('a')[0].get('href')
    if url.find('.pdf') > -1:
        return url
    else:
        # give up, it's probably a "shopping cart" link.
        return None


jama_journals = ['Arch Neurol',
                 'Arch Ophthalmol',
                 'JAMA',
                 'JAMA Dermatol',
                 'JAMA Facial Plast Surg',
                 'JAMA Intern Med',
                 'JAMA Neurol',
                 'JAMA Oncol',
                 'JAMA Ophthalmol',
                 'JAMA Otolaryngol Head Neck Surg',
                 'JAMA Pediatr',
                 'JAMA Psychiatry',
                 'JAMA Surg', 
                ]

def the_jama_dance(doi):
    url = the_doi_2step(doi)
    r = requests.get(url)
    if r.status_code != 200:
        return 'error'

    parser = HTMLParser()
    tree = etree.fromstring(r.text, parser)
    
    # we're looking for a meta tag like this:
    # <meta name="citation_pdf_url" content="http://archneur.jamanetwork.com/data/Journals/NEUR/13776/NOC40008.pdf" />
    for item in tree.findall('head/meta'):
        if item.get('name')=='citation_pdf_url':
            return item.get('content')

# TODO
# doiserbia (Library of Serbia) articles can be grabbed by doing the_doi_2step,
# then ...?
doiserbia_journals = ['Genetika']


unlinkable = ['Ann Surg Oncol',
              'Brain Pathol',
              'Cancer',
              'Cytogenet Genome Res',       # Karger
              'Eur J Cancer',
              'Genet Test Mol Biomarkers',
            ]

todo_journals = { 'Med Sci Monit': { 'example': 'http://www.medscimonit.com/download/index/idArt/869530' },
                  'Asian Pac J Cancer Prev': { 'example': 'http://www.apocpcontrol.org/paper_file/issue_abs/Volume12_No7/1771-1776%20c%206.9%20Lei%20Zhong.pdf' },
                  'Rev Esp Cardiol': { 'example': 'http://www.revespcardiol.org/en/linkresolver/articulo-resolver/13131646/' },
                  'Ann Dermatol Venereol': { 'example': 'http://www.em-consulte.com/article/152959/alertePM' },
                  'J Biochem': { 'example': 'https://www.jstage.jst.go.jp/article/biochemistry1922/125/4/125_4_803/_pdf'},
                  'Mol Cells': { 'example': 'http://www.molcells.org/journal/view.html?year=2004&volume=18&number=2&spage=141 --> http://pdf.medrang.co.kr/KSMCB/2004/018/mac-18-2-141.pdf'},
                  'Mol Vis': { 'example': 'http://www.molvis.org/molvis/v10/a45/ --> http://www.molvis.org/bin/pdf.cgi?Zheng,10,45'}, 
                }

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
    'informa': 'http://informahealthcare.com/doi/pdf/{a.doi}', 
    'ats': 'http://www.atsjournals.org/doi/pdf/{a.doi}', 
    'acs': 'http://pubs.acs.org/doi/pdf/{a.doi}',
    'liebert': 'http://online.liebertpub.com/doi/pdf/{a.doi}',
    'akademii': 'http://www.akademiai.com/content/{a.pii}/fulltext.pdf'
    }

# simple formats are used for URLs that can be deduced from data
# in the pubmed record
simple_formats_doi = {
    'Acta Neurol Scand': format_templates['wiley'],
    'Ann Hum Genet': format_templates['wiley'],
    'Ann Neurol': format_templates['wiley'],
    'Am J Hematol': format_templates['wiley'],
    'Am J Med Genet': format_templates['wiley'],
    'Am J Med Genet A': format_templates['wiley'],
    'Am J Med Genet B Neuropsychiatr Genet': format_templates['wiley'],
    'Arthritis Rheum': format_templates['wiley'],
    'Australas J Dermatol': format_templates['wiley'],
    'BJU Int': format_templates['wiley'],
    'Breast J': format_templates['wiley'],
    'Br J Dermatol': format_templates['wiley'],
    'Br J Haematol': format_templates['wiley'],
    'Clin Endocrinol (Oxf)': format_templates['wiley'],
    'Clin Genet': format_templates['wiley'],
    'Clin Pharmacol Ther': format_templates['wiley'],
    'Dev Med Child Neurol': format_templates['wiley'],
    'Eur J Clin Invest': format_templates['wiley'],
    'Eur J Haematol': format_templates['wiley'],
    'Exp Dermatol': format_templates['wiley'],
    'Genes Chromosomes Cancer': format_templates['wiley'],
    'Genet Epidemiol': format_templates['wiley'],
    'Hum Mutat': format_templates['wiley'],
    'Immunol Rev': format_templates['wiley'],
    'Int J Cancer': format_templates['wiley'],
    'J Bone Miner Res': format_templates['wiley'],
    'J Dermatol': format_templates['wiley'],
    'J Gastroenterol Hepatol': format_templates['wiley'],
    'J Orthop Res': format_templates['wiley'],
    'J Thromb Haemost': format_templates['wiley'],
    'Mov Disord': format_templates['wiley'],
    'Muscle Nerve': format_templates['wiley'],
    'Pediatr Blood Cancer': format_templates['wiley'],
    'Pediatr Int': format_templates['wiley'],
    'Prenat Diagn': format_templates['wiley'],
    'Proteins': format_templates['wiley'],
    'Tissue Antigens': format_templates['wiley'],  #this one's not working...?
    'Transfus Med': format_templates['wiley'],
    'Transfusion': format_templates['wiley'],
    'Vox Sang': format_templates['wiley'],

    'Acta Oncol': format_templates['informa'],
    'Hemoglobin': format_templates['informa'],

    'Am J Respir Cell Mol Biol': format_templates['ats'],
    'Am J Respir Crit Care Med': format_templates['ats'],

    'Anal Chem': format_templates['acs'],

    'Genet Test': format_templates['liebert'],
    'Thyroid': format_templates['liebert'],

    'Mol Endocrinol': 'http://press.endocrine.org/doi/pdf/{a.doi}',

    'PLoS Biol': format_templates['plos'],
    'PLoS Comput Biol': format_templates['plos'],
    'PLoS Genet': format_templates['plos'],
    'PLoS Med': format_templates['plos'],
    'PLoS ONE': format_templates['plos'],
    'PLoS Pathog': format_templates['plos'],
    'N Engl J Med':  'http://www.nejm.org/doi/pdf/{a.doi}',
    }

# http://www.ajconline.org/article/S0002-9149(07)00515-2/pdf

simple_formats_pii = {
    'Am J Cardiol': 'http://www.ajconline.org/article/{a.pii}/pdf',
    'Am J Ophthalmol': 'http://www.ajo.com/article/{a.pii}/pdf', #ScienceDirect
    'Atherosclerosis': 'http://www.atherosclerosis-journal.com/article/{a.pii}/pdf', #ScienceDirect
    'Biol Psychiatry': 'http://www.biologicalpsychiatryjournal.com/article/{a.pii}/pdf', #ScienceDirect
    'Brain Dev': 'http://www.brainanddevelopment.com/article/{a.pii}/pdf', #ScienceDirect
    'Cancer Lett': 'http://www.cancerletters.info/article/{a.pii}/pdf', #ScienceDirect
    'Clin Neurol Neurosurg': 'http://www.clineu-journal.com/article/{a.pii}/pdf', #ScienceDirect
    'Diabetes Res Clin Pract': 'http://www.diabetesresearchclinicalpractice.com/article/{a.pii}/pdf', #ScienceDirect
    'Epilepsy Res': 'http://www.epires-journal.com/article/{a.pii}/pdf', #ScienceDirect
    'Eur J Paediatr Neurol': 'http://www.ejpn-journal.com/article/{a.pii}/pdf', #ScienceDirect
    'Fertil Steril': 'http://www.fertstert.org/article/{a.pii}/pdf',    #ScienceDirect
    'Gastroenterology': 'http://www.gastrojournal.org/article/{a.pii}/pdf',
    'Int J Pediatr Otorhinolaryngol': 'http://www.ijporlonline.com/article/{a.pii}/pdf', #ScienceDirect
    'J Mol Cell Cardiol': 'http://www.jmmc-online.com/article/{a.pii}/pdf', #ScienceDirect
    'J Mol Diagn': 'http://jmd.amjpathol.org/article/{a.pii}/pdf',
    'J Neurol Sci': 'http://www.jns-journal.com/article/{a.pii}/pdf',   
    'J Pediatr': 'http://www.jpeds.com/article/{a.pii}/pdf',  #ScienceDirect
    'J Pediatr Urol': 'http://www.jpurol.com/article/{a.pii}/pdf',  #ScienceDirect
    'Ophthalmology': 'http://www.aaojournal.org/article/{a.pii}/pdf', #ScienceDirect
    'Orv Hetil': format_templates['akademii'],
    'Metabolism': 'http://www.metabolismjournal.com/article/{a.pii}/pdf', #ScienceDirect
    'Metab Clin Exp': 'http://www.metabolismjournal.com/article/{a.pii}/pdf', #ScienceDirect
    'Mol Genet Metab': 'http://www.mgmjournal.com/article/{a.pii}/pdf', #ScienceDirect
    'Parkinsonism Relat Disord': 'http://www.prd-journal.com/article/{a.pii}/pdf', #ScienceDirect
    'Pediatr Neurol': 'http://www.pedneur.com/article/{a.pii}/pdf', #ScienceDirect
    'Surg Neurol': 'http://www.worldneurosurgery.org/article/{a.pii}/pdf', #ScienceDirect
    } 

# vip = Volume-Issue-Page format -- URLs that have the same format
# except for the host name

# http://www.bloodjournal.org/content/117/5/1622.full.pdf

vip_format = 'http://{host}/content/{a.volume}/{a.issue}/{a.first_page}.full.pdf'

vip_journals = {
        'Ann Clin Biochem': { 'host': 'acb.sagepub.com' },
        'Am J Hypertens': { 'host': 'ajh.oxfordjournals.org' },
        'Ann Oncol' : {'host' : 'annonc.oxfordjournals.org'},
        'Arterioscler Thromb Vasc Biol' : {'host' : 'atvb.ahajournals.org'},
        'Blood': { 'host': 'bloodjournal.org' }, #'bloodjournal.hematologylibrary.org' },
        'Brain': { 'host': 'brain.oxfordjournals.org' },
        'Breast Cancer Res' : { 'host': 'breast-cancer-research.com' },
        'Cancer Discov' : {'host': 'cancerdiscovery.aacrjournals.org'},
        'Cancer Epidemiol Biomarkers Prev': { 'host': 'cebp.aacrjournals.org' },
        'Cancer Res': { 'host': 'cancerres.aacrjournals.org' },
        'Carcinogenesis': { 'host': 'carcin.oxfordjournals.org' } ,
        'Cardiovasc Res' : {'host' : 'cardiovascres.oxfordjournals.org'},
        'Circulation': { 'host': 'circ.ahajournals.org' },
        'Circ Cardiovasc Genet' : {'host' : 'circgenetics.ahajournals.org'},
        'Circ Res' : {'host' : 'circres.ahajournals.org'},
        'Clin Cancer Res' : {'host' : 'clincancerres.aacrjournals.org'},
        'Clin Chem' : {'host' : 'clinchem.org'},
        'Diabetes': {'host': 'diabetes.diabetesjournals.org'},
        'Diabetes Care': { 'host': 'care.diabetesjournals.org' },
        'Eur Heart J' : {'host' : 'eurheartj.oxfordjournals.org'},
        'Eur J Endocrinol' : {'host' : 'eje-online.org'},
        'FASEB J' : {'host' : 'fasebj.org'},
        'Genome Biol' : { 'host' : 'genomebiology.com'},
        'Genes Dev' : {'host': 'genesdev.cshlp.org'},
        'Gut' : {'host' : 'gut.bmj.com'},
        'Haematologica' : {'host' : 'haematologica.org'},
        'Hum Mol Genet': { 'host': 'hmg.oxfordjournals.org' },
        'Hum Reprod': { 'host': 'humrep.oxfordjournals.org' },
        'Hypertension': { 'host': 'hyper.ahajournals.org' },
        'Int J Oncol' : {'host' : 'spandidos-publications.com/ijo/'},
        'Invest Ophthalmol Vis Sci': { 'host': 'www.iovs.org' },
        'IOVS' : {'host' : 'iovs.org'},
        'J Am Soc Nephrol' : {'host' : 'jasn.asnjournals.org'},
        'J Biol Chem': { 'host': 'www.jbc.org' },
        'J Cell Biol' : {'host' : 'jcb.rupress.org'},
        'J Cell Sci' : {'host' : 'jcs.biologists.org'},
        'J Clin Endocrinol Metab': { 'host': 'jcem.endojournals.org' },
        'J Clin Oncol': { 'host': 'jco.ascopubs.org' },
        'J Dent Res': { 'host': 'jdr.sagepub.com' },
        'J Immunol' : {'host' : 'jimmunol.org'},
        'J Infect Dis': {'host': 'jid.oxfordjournals.org'},
        'J Natl Cancer Inst': {'host': 'jnci.oxfordjournals.org'},
        'J Neurol Neurosurg Psychiatry': {'host': 'jnnp.bmj.com'}, 
        'J Neurosci' : {'host' : 'jneurosci.org'},
        'J Med Genet': { 'host': 'jmg.bmj.com' },
        'J Mol Endocrinol': { 'host': 'jme.endocrinology-journals.org' },
        'J Lipid Res': { 'host': 'www.jlr.org' },
        'Mol Biol Cell' : {'host' : 'molbiolcell.org'},
        'Mol Cell Biol' : {'host': 'mcb.asm.org'},
        'Mol Canc Therapeut' : {'host' : 'mct.aacrjournals.org'},
        'Mol Hum Reprod': {'host': 'molehr.oxfordjournals.org'},
        'Mol Pharmacol': {'host' : 'molpharm.aspetjournals.org'},
        'Neurology' : {'host' : 'neurology.org'},
        'Nephrol Dial Transplant': {'host': 'ndt.oxfordjournals.org'},
        'Nucleic Acids Res' : {'host' : 'nar.oxfordjournals.org'},
        'Oncol Lett' : {'host' : 'spandidos-publications.com/ol/'},
        'Oncol Rep' : {'host' : 'spandidos-publications.com/or/'},
        'Orphanet J Rare Dis' : {'host' : 'ojrd.com'},
        'Pediatrics': {'host': 'pediatrics.aappublications.org'},
        'Proc Natl Acad Sci USA': { 'host': 'pnas.org'},
        'Science': { 'host': 'sciencemag.org' },
        }

# cell journals
#cell_format = 'http://download.cell.com{ja}/pdf/PII{pii}.pdf'
cell_format = 'http://www.cell.com{ja}/pdf/{pii}.pdf'
cell_journals = {
    'Am J Hum Genet': { 'ja': '/AJHG' },
    'Cell': { 'ja': '' },
    'Trends Mol Med': { 'ja': 'trends' },
    'Cancer Cell': { 'ja': 'cancer-cell' },
    'Neuron': {'ja': 'neuron' }
    }

# nature journals
nature_format = 'http://www.nature.com/{ja}/journal/v{a.volume}/n{a.issue}/pdf/{a.pii}.pdf'
nature_journals = {
    'Eur J Hum Genet': { 'ja': 'ejhg' },
    'Eye (Lond)': { 'ja': 'eye' },
    'J Hum Genet': { 'ja': 'jhg' },
    'Kidney Int': { 'ja': 'ki' },
    'Nature': { 'ja': 'nature' },
    'Nat Genet': { 'ja': 'ng' },
    'Nat Neurosci': { 'ja': 'neuro' },
    'Nat Med': { 'ja': 'nm' },
    'Nat Methods': { 'ja': 'nmeth' },
    'Nat Rev. Genet': { 'ja': 'nrg' },
    'Nature reviews Immunology': { 'ja': 'nri' },
    'Neuropsychopharmacology': { 'ja': 'npp' },
    }

# the doi2step_journals should work in nature_journals, but the urls are weird. 
# e.g. http://www.nature.com/gim/journal/v8/n11/pdf/gim2006115a.pdf
#      http://www.nature.com/jid/journal/v113/n2/full/5603216a.html
doi2step_journals = [ 'Genet Med', 'J Invest Dermatol' ]

# TODO
#
#15533574: no URL because No URL format for Journal Int J Pediatr Otorhinolaryngol
#15533621: no URL because No URL format for Journal Med Hypotheses
# 15611820: no URL because No URL format for Journal Arq Bras Endocrinol Metabol
# 15611833: no URL because No URL format for Journal Arq Bras Endocrinol Metabol
# 17486493: no URL because No URL format for Journal Hemoglobin
# 15231984: no URL because No URL format for Journal Pediatrics
# 15234147: no URL because No URL format for Journal Ophthalmology
# 15234312: no URL because No URL format for Journal Am J Ophthalmol
# 15234419: no URL because No URL format for Journal J Am Coll Cardiol
# 15234655: no URL because No URL format for Journal Am J Med
#17319787: no URL because No URL format for Journal Neoplasma
#17320181: no URL because No URL format for Journal Ophthalmology
#17321228: no URL because No URL format for Journal Bone
#17099210: no URL because No URL format for Journal Hum. Reprod.
#17100396: no URL because No URL format for Journal J Med Assoc Thai
#9538891: no URL because No URL format for Journal Invest. Ophthalmol. Vis. Sci.
#9700188: no URL because No URL format for Journal Hum. Mol. Genet.
#9700193: no URL because No URL format for Journal Hum. Mol. Genet.
#17413447: no URL because No URL format for Journal Psychiatr. Genet.
#17414143: no URL because No URL format for Journal J. Pediatr. Gastroenterol. Nutr.
#17415510: no URL because No URL format for Journal J. Neurol.
#17415538: no URL because No URL format for Journal HNO
#17415575: no URL because No URL format for Journal Arch. Dermatol. Res.
#17415800: no URL because No URL format for Journal Mov. Disord.
#17416296: no URL because No URL format for Journal Arch. Med. Res.
#17143180: no URL because No URL format for Journal J Hypertens
#17143182: no URL because No URL format for Journal J Hypertens
#17143317: no URL because No URL format for Journal Nat Clin Pract Endocrinol Metab
#17143551: no URL because No URL format for Journal Int J Mol Med
#17145028: no URL because No URL format for Journal Med Clin (Barc)
#17145065: no URL because No URL format for Journal Mutat Res
#10726756: no URL because No URL format for Journal Electrophoresis
#15452385: no URL because No URL format for Journal Horm Res
#15452722: no URL because No URL format for Journal Graefes Arch Clin Exp Ophthalmol
#15453866: no URL because No URL format for Journal Acta Ophthalmol Scand
#15519027: no URL because No URL format for Journal J Am Coll Cardiol
#15519272: no URL because No URL format for Journal Hepatol Res
        


# Below: Journals with really annoying paywalls guarding their precious secrets.
schattauer_journals = [
    'Thromb Haemost',
    ]

wolterskluwer_journals = [
    'J Hypertens',
    'J Glaucoma',
    'Pharmacogenetics',
    'Plast Reconstr Surg',
    ]

karger_journals = [
    'Cytogenet Genome Res'
    ]

springer_journals = [
    'Acta Neuropathol',
    'Breast Cancer Res Treat',
    'Diabetologia',
    'Eur J Pediatr',
    'Fam Cancer',
    'J Bone Miner Metab',
    'J Endocrinol Invest',
    'J Inherit Metab Dis',
    'J Mol Med (Berl)',
    'Neurogenetics',
    'Ophthalmologe',
    'Pediatr Nephrol',
    'Physiol Genomics',
    ]

# thieme journals so far don't seem to have any open access content.
# example of link to article page: https://www.thieme-connect.com/DOI/DOI?10.1055/s-0028-1085467
thieme_journals = ['Neuropediatrics', 'Semin Vasc Med']

paywall_journals = schattauer_journals + wolterskluwer_journals + springer_journals + thieme_journals + karger_journals


PMC_PDF_URL = 'http://www.ncbi.nlm.nih.gov/pmc/articles/pmid/{a.pmid}/pdf'

def find_article_from_doi(doi):
    #1) lookup on CrossRef
    #2) pull a PubMedArticle based on CrossRef results
    #3) run it through find_article_from_pma
    pma = fetch.article_by_pmid(doi2pmid(doi))
    return find_article_from_pma(pma)
    

def find_article_from_pma(pma, crossref_doi=True, paywalls=False):
    reason = None
    url = None

    jrnl = pma.journal.translate(None, '.')

    if pma.doi==None and crossref_doi:
        pma.doi = PubMedArticle2doi(pma)
        if pma.doi==None:
            reason = 'DOI missing from PubMedArticle and CrossRef lookup failed.'
        else:
            reason = 'DOI missing from PubMedArticle.'
 
    if pma.pmc:
        url = PMC_PDF_URL.format(a=pma)

    elif jrnl in simple_formats_doi.keys():
        if pma.doi != None:
            url = simple_formats_doi[jrnl].format(a=pma)
            reason = ''

    elif jrnl in simple_formats_pii.keys():
        if pma.pii:
            url = simple_formats_pii[jrnl].format(a=pma)
        else:
            reason = 'pii missing from PubMedArticle XML'

    elif jrnl in doi2step_journals:
        if pma.doi:
            try:
                baseurl = the_doi_2step(pma.doi)
                url = baseurl.replace('full', 'pdf').replace('html', 'pdf')
                reason = ''
            except MetaPubError, e:
                reason = '%s' % e

    elif jrnl in jama_journals:
        if pma.doi:
            try:
                url = the_jama_dance(pma.doi)
                reason = ''
            except MetaPubError, e:
                reason = '%s' % e

    elif jrnl in vip_journals.keys():
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
            url = vip_format.format(host=vip_journals[jrnl]['host'], a=pma)
        else:
            reason = 'volume and maybe also issue data missing'


    elif jrnl in nature_journals.keys():
        if pma.pii:
            url = nature_format.format(a=pma, ja=nature_journals[jrnl]['ja'])
        else:
            reason = 'pii missing from PubMedArticle XML (%s in Nature format)' % jrnl

    elif jrnl in cell_journals.keys():
        if pma.pii:
            url = cell_format.format( a=pma, ja=cell_journals[jrnl]['ja'],
                    pii=pma.pii.translate(None,'-()') )
        else:
            reason = 'pii missing from PubMedArticle XML (%s in Cell format)' % jrnl
    
    elif jrnl in 'Lancet' and pma.pii is not None:
        #url = 'http://download.thelancet.com/pdfs/journals/lancet/PII{piit}.pdf'.format(piit = pma.pii.translate(None,'-()'))
        url = 'http://www.thelancet.com/pdfs/journals/lancet/PII{a.pii}.pdf'.format(a = pma)

    elif jrnl in sciencedirect_journals:
        if pma.pii:
            url = get_sciencedirect_pdf_url(pma)
        else:
            reason = 'pii missing from PubMedArticle XML (%s in ScienceDirect format)' % jrnl

    elif jrnl in paywall_journals:
        if paywalls == False:
            reason = '%s behind obnoxious paywall' % jrnl
    else:
        reason = 'No URL format for Journal %s' % jrnl

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
        self.paywalls = kwargs.get('paywalls', False)

        self.pma = None
        #self.cr_top_result = None

        if self.pmid:
            self.pma = fetch.article_by_pmid(self.pmid)
            self.url, self.reason = find_article_from_pma(self.pma, paywalls=self.paywalls)

        elif self.doi:
            self.url, self.reason = find_article_from_doi(self.doi, paywalls=self.paywalls)


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


