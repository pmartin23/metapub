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

format_templates = {
    'acs': 'http://pubs.acs.org/doi/pdf/{a.doi}',
    'akademii': 'http://www.akademiai.com/content/{a.pii}/fulltext.pdf',
    'ats': 'http://www.atsjournals.org/doi/pdf/{a.doi}', 
    'informa': 'http://informahealthcare.com/doi/pdf/{a.doi}', 
    'liebert': 'http://online.liebertpub.com/doi/pdf/{a.doi}',
    'plos': 'http://www.plosbiology.org/article/fetchObjectAttachment.action?url=info:doi/{a.doi}&representation=PDF',
    'wiley': 'http://onlinelibrary.wiley.com/doi/{a.doi}/pdf',
    }

sciencedirect_journals = [
    'Arch Pediatr',
    'Blood Cells Mol Dis',
    'Biochem Biophys Res Commun' ,
    'Biochem Pharmacol',
    'Clin Immunol',
    'FEBS Lett',
    'Eur J Cancer',
    'Eur J Med Genet',
    'Gene',
    'Genomics',
    'Hepatol Res',
    'J Am Coll Cardiol',
    'J Mol Biol',
    'J Neurol Sci',
    'Mol Cell Endocrinol',
    'Mol Genet Metab',
    'Mol Immunol',
    'Mutat Res',
    'Neurosci Lett',
    ]

sciencedirect_url = 'http://www.sciencedirect.com/science/article/pii/{piit}'
def get_sciencedirect_pdf_url(pma):
    '''we're looking for a url that looks like this:
    http://www.sciencedirect.com/science/article/pii/S0022283601953379/pdfft?md5=07db9e1b612f64ea74872842e34316a5&pid=1-s2.0-S0022283601953379-main.pdf'''
    starturl = sciencedirect_url.format(piit = pma.pii.translate(None,'-()'))
    try:
        r = requests.get(starturl)
    except requests.exceptions.TooManyRedirects:
        return 'error: cannot reach pma.journal'
    tree = etree.fromstring(r.text, HTMLParser())
    div = tree.cssselect('div.icon_pdf')[0]
    url = div.cssselect('a')[0].get('href')
    if url.find('.pdf') > -1:
        return url
    else:
        # give up, it's probably a "shopping cart" link.
        return 'error: cannot find pdf link'


jama_journals = [
                 'Arch Gen Psychiatry',
                 'Arch Neurol',
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

todo_journals = { 
    'Med Sci Monit': { 'example': 'http://www.medscimonit.com/download/index/idArt/869530' },
    'Asian Pac J Cancer Prev': { 'example': 'http://www.apocpcontrol.org/paper_file/issue_abs/Volume12_No7/1771-1776%20c%206.9%20Lei%20Zhong.pdf' },
    'Rev Esp Cardiol': { 'example': 'http://www.revespcardiol.org/en/linkresolver/articulo-resolver/13131646/' },
    'Ann Dermatol Venereol': { 'example': 'http://www.em-consulte.com/article/152959/alertePM' },
    'Mol Cells': { 'example': 'http://www.molcells.org/journal/view.html?year=2004&volume=18&number=2&spage=141 --> http://pdf.medrang.co.kr/KSMCB/2004/018/mac-18-2-141.pdf'},
    'Mol Vis': { 'example': 'http://www.molvis.org/molvis/v10/a45/ --> http://www.molvis.org/bin/pdf.cgi?Zheng,10,45'}, 
    'Singapore Med J': { 'example': 'http://www.sma.org.sg/smj/4708/4708cr4.pdf' },
    'Rev Port Cardiol': { 'example': '16335287: http://www.spc.pt/DL/RPC/artigos/74.pdf' },
    'World J Gastroenterol': { 'example': 'http://www.wjgnet.com/1007-9327/full/v11/i48/7690.htm --> http://www.wjgnet.com/1007-9327/pdf/v11/i48/7690.pdf' },
    'Genet Mol Res': { 'example': '24668667: http://www.geneticsmr.com/articles/2992 --> http://www.geneticsmr.com//year2014/vol13-1/pdf/gmr2764.pdf' },
    'Arq Bras Endocrinol Metabol': { 'example': '15611820: http://www.scielo.br/pdf/abem/v48n1/19521.pdf' },
    'Neoplasma': { 'example': '17319787: http://www.elis.sk/download_file.php?product_id=1006&session_id=skl2f3grcd19ebnie17u15a571' },
    'Clinics (Sao Paulo)': { 'example': '17823699: http://www.scielo.br/scielo.php?script=sci_arttext&pid=S1807-59322007000400003' },
    }

# JSTAGE: mostly free (yay)
# Examples:
# J Biochem: https://www.jstage.jst.go.jp/article/biochemistry1922/125/4/125_4_803/_pdf
# Drug Metab Pharmacokinet: https://www.jstage.jst.go.jp/article/dmpk/20/2/20_2_144/_article --> https://www.jstage.jst.go.jp/article/dmpk/20/2/20_2_144/_pdf
jstage_journals = [ 
    'J Periodontol',
    'J Biochem',
    'Drug Metab Pharmacokinet',
    'Endocr J',
    ]

def exit_jstage_left(pma):
    url = the_doi_2step(pma.doi)
    r = requests.get(url)
    if r.status_code != 200:
        return 'error: %i for %s' % (r.status_code, url)
    if r.url.find('jstage') > -1:
        return r.url.replace('_article', '_pdf')
    else:
        return 'error: %s did not resolve to jstage article' % url

# simple formats are used for URLs that can be deduced from PubMedArticle XML
simple_formats_doi = {
    'Acta Oncol': format_templates['informa'],
    'Hemoglobin': format_templates['informa'],
    'Platelets': format_templates['informa'],

    'Am J Respir Cell Mol Biol': format_templates['ats'],
    'Am J Respir Crit Care Med': format_templates['ats'],

    'Anal Chem': format_templates['acs'],
    'Biochemistry': format_templates['acs'],

    'Genet Test': format_templates['liebert'],
    'Thyroid': format_templates['liebert'],

    'Mol Endocrinol': 'http://press.endocrine.org/doi/pdf/{a.doi}',
    'J Periodontol': 'http://www.joponline.org/doi/pdf/{a.doi}',

    'PLoS Biol': format_templates['plos'],
    'PLoS Comput Biol': format_templates['plos'],
    'PLoS Genet': format_templates['plos'],
    'PLoS Med': format_templates['plos'],
    'PLoS ONE': format_templates['plos'],
    'PLoS Pathog': format_templates['plos'],
    'N Engl J Med':  'http://www.nejm.org/doi/pdf/{a.doi}',
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


wiley_journals = [
    'Acta Neurol Scand',
    'Ann Hum Genet',
    'Ann Neurol',
    'Am J Hematol',
    'Am J Med Genet',
    'Am J Med Genet A',
    'Am J Med Genet B Neuropsychiatr Genet',
    'Arthritis Rheum',
    'Australas J Dermatol',
    'BJU Int',
    'Breast J',
    'Br J Dermatol',
    'Br J Haematol',
    'Cancer',
    'Clin Endocrinol (Oxf)',
    'Clin Genet',
    'Clin Pharmacol Ther',
    'Dev Med Child Neurol',
    'Electrophoresis',
    'Environ Mol Mutagen',
    'Eur J Clin Invest',
    'Eur J Haematol',
    'Eur J Neurol',
    'Exp Dermatol',
    'Genes Chromosomes Cancer',
    'Genet Epidemiol',
    'Head Neck',
    'Hum Mutat',
    'Immunol Rev',
    'Int J Cancer',
    'J Bone Miner Res',
    'J Dermatol',
    'J Gastroenterol Hepatol',
    'J Orthop Res',
    'J Thromb Haemost',
    'J Pathol',
    'Mov Disord',
    'Muscle Nerve',
    'Pediatr Blood Cancer',
    'Pediatr Int',
    'Prenat Diagn',
    'Proteins',
    'Tissue Antigens',
    'Transfus Med',
    'Transfusion',
    'Vox Sang',
    ]

def the_wiley_shuffle(pma):
    r = requests.get(format_templates['wiley'].format(a=pma))
    if r.headers['content-type'].find('html') > -1:
        if r.text.find('ACCESS DENIED') > -1:
            return 'error: Wiley says ACCESS DENIED'
        tree = etree.fromstring(r.text, HTMLParser())
        if tree.find('head/title').text.find('Not Found') > -1:
            return 'error: Wiley says File Not found'

        iframe = tree.find('body/div/iframe')
        return iframe.get('src')
    elif r.headers['content-type'] == 'application/pdf':
        return r.url

# http://www.ajconline.org/article/S0002-9149(07)00515-2/pdf

simple_formats_pii = {
    'Am J Cardiol': 'http://www.ajconline.org/article/{a.pii}/pdf',
    'Am J Ophthalmol': 'http://www.ajo.com/article/{a.pii}/pdf', #ScienceDirect
    'Am J Med': 'http://www.amjmed.com/article/{a.pii}/pdf', #ScienceDirect
    'Atherosclerosis': 'http://www.atherosclerosis-journal.com/article/{a.pii}/pdf', #ScienceDirect
    'Biol Psychiatry': 'http://www.biologicalpsychiatryjournal.com/article/{a.pii}/pdf', #ScienceDirect
    'Bone': 'http://www.thebonejournal.com/article/{a.pii}/pdf', #ScienceDirect
    'Brain Dev': 'http://www.brainanddevelopment.com/article/{a.pii}/pdf', #ScienceDirect
    'Cancer Genet Cytogenet': 'http://www.cancergeneticsjournal.org/article/{a.pii}/pdf', #ScienceDirect
    'Cancer Lett': 'http://www.cancerletters.info/article/{a.pii}/pdf', #ScienceDirect
    'Clin Neurol Neurosurg': 'http://www.clineu-journal.com/article/{a.pii}/pdf', #ScienceDirect
    'Diabetes Res Clin Pract': 'http://www.diabetesresearchclinicalpractice.com/article/{a.pii}/pdf', #ScienceDirect
    'Epilepsy Res': 'http://www.epires-journal.com/article/{a.pii}/pdf', #ScienceDirect
    'Eur J Paediatr Neurol': 'http://www.ejpn-journal.com/article/{a.pii}/pdf', #ScienceDirect
    'Fertil Steril': 'http://www.fertstert.org/article/{a.pii}/pdf',    #ScienceDirect
    'Gastroenterology': 'http://www.gastrojournal.org/article/{a.pii}/pdf',
    'Gynecol Oncol': 'http://www.gynecologiconcology-online.net/article/{a.pii}/pdf', #ScienceDirect
    'Heart Rhythm': 'http://www.heartrhythmjournal.com/article/{a.pii}/pdf',
    'Int J Pediatr Otorhinolaryngol': 'http://www.ijporlonline.com/article/{a.pii}/pdf', #ScienceDirect
    'Int J Cardiol': 'http://www.internationaljournalofcardiology.com/article/{a.pii}/pdf', #ScienceDirect
    'J Dermatol': 'http://www.jdsjournal.com/article/{a.pii}/pdf', #ScienceDirect
    'J Mol Cell Cardiol': 'http://www.jmmc-online.com/article/{a.pii}/pdf', #ScienceDirect
    'J Mol Diagn': 'http://jmd.amjpathol.org/article/{a.pii}/pdf',  #ScienceDirect
    'J Neurol Sci': 'http://www.jns-journal.com/article/{a.pii}/pdf',   
    'J Pediatr': 'http://www.jpeds.com/article/{a.pii}/pdf',  #ScienceDirect
    'J Pediatr Urol': 'http://www.jpurol.com/article/{a.pii}/pdf',  #ScienceDirect
    'Ophthalmology': 'http://www.aaojournal.org/article/{a.pii}/pdf', #ScienceDirect
    'Orv Hetil': format_templates['akademii'],
    'Metabolism': 'http://www.metabolismjournal.com/article/{a.pii}/pdf', #ScienceDirect
    'Metab Clin Exp': 'http://www.metabolismjournal.com/article/{a.pii}/pdf', #ScienceDirect
    'Mol Genet Metab': 'http://www.mgmjournal.com/article/{a.pii}/pdf', #ScienceDirect
    'Neuromuscul Disord': 'http://www.nmd-journal.com/article/{a.pii}/pdf', #ScienceDirect
    'Parkinsonism Relat Disord': 'http://www.prd-journal.com/article/{a.pii}/pdf', #ScienceDirect
    'Pediatr Neurol': 'http://www.pedneur.com/article/{a.pii}/pdf', #ScienceDirect
    'Surg Neurol': 'http://www.worldneurosurgery.org/article/{a.pii}/pdf', #ScienceDirect
    'Thromb Res': 'http://www.thrombosisresearch.com/article/{a.pii}/pdf', #ScienceDirect
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
        'Blood': { 'host': 'bloodjournal.org' }, #TODO: real url is http://www.bloodjournal.org/content/bloodjournal/122/23/3844.full.pdf
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
        'Genome Res': { 'host': 'genome.cshlp.org'},
        'Genes Dev' : {'host': 'genesdev.cshlp.org'},
        'Gut' : {'host' : 'gut.bmj.com'},
        'Haematologica' : {'host' : 'haematologica.org'},
        'Hum Mol Genet': { 'host': 'hmg.oxfordjournals.org' },
        'Hum Reprod': { 'host': 'humrep.oxfordjournals.org' },
        'Hypertension': { 'host': 'hyper.ahajournals.org' },
        'Int J Oncol' : {'host' : 'spandidos-publications.com/ijo/'},
        'Int J Mol Med': {'host': 'spandidos-publications.com/ijmm/'},
        'Invest Ophthalmol Vis Sci': { 'host': 'www.iovs.org' },
        'IOVS' : {'host' : 'iovs.org'},
        'J Am Soc Nephrol' : {'host' : 'jasn.asnjournals.org'},
        'J Biol Chem': { 'host': 'www.jbc.org' },
        'J Cell Biol' : {'host' : 'jcb.rupress.org'},
        'J Cell Sci' : {'host' : 'jcs.biologists.org'},
        'J Child Neurol': { 'host': 'jcn.sagepub.com'},
        'J Clin Endocrinol Metab': { 'host': 'jcem.endojournals.org' },
        'J Clin Oncol': { 'host': 'jco.ascopubs.org' },
        'J Dent Res': { 'host': 'jdr.sagepub.com' },
        'J Gerontol A Biol Sci Med Sci': { 'host': 'biomedgerontology.oxfordjournals.org' },
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
        'QJM': { 'host': 'qjmed.oxfordjournals.org'},
        'Science': { 'host': 'sciencemag.org' },
        }

# cell journals
#cell_format = 'http://download.cell.com{ja}/pdf/PII{pii}.pdf'
cell_format = 'http://www.cell.com{ja}/pdf/{pii}.pdf'
cell_journals = {
    'Am J Hum Genet': { 'ja': '/AJHG' },
    'Cell': { 'ja': '' },
    'Trends Mol Med': { 'ja': '/trends' },
    'Cancer Cell': { 'ja': '/cancer-cell' },
    'Neuron': {'ja': '/neuron' },
    'Mol Cell': {'ja': '/molecular-cell' },
    'Curr Biol': {'ja': '/current-biology' },
    }

# nature journals
nature_format = 'http://www.nature.com/{ja}/journal/v{a.volume}/n{a.issue}/pdf/{a.pii}.pdf'
nature_journals = {
    'Eur J Hum Genet': { 'ja': 'ejhg' },
    'Eye (Lond)': { 'ja': 'eye' },
    'J Hum Genet': { 'ja': 'jhg' },
    'Kidney Int': { 'ja': 'ki' },
    'Leukemia': { 'ja': 'leu' },
    'Mod Pathol': { 'ja': 'modpathol' },
    'Mol Psychiatry': { 'ja': 'mp' },
    'Nature': { 'ja': 'nature' },
    'Nat Genet': { 'ja': 'ng' },
    'Nat Neurosci': { 'ja': 'neuro' },
    'Nat Med': { 'ja': 'nm' },
    'Nat Methods': { 'ja': 'nmeth' },
    'Nat Rev. Genet': { 'ja': 'nrg' },
    'Nature reviews Immunology': { 'ja': 'nri' },
    'Neuropsychopharmacology': { 'ja': 'npp' },
    'Oncogene': { 'ja': 'onc' },
    }

def the_nature_show(pma):
    if pma.pii==None and pma.doi:
        url = the_doi_2step(pma.doi)
    else:
        url = nature_format.format(a=pma, ja=nature_journals[pma.journal.translate(None, '.')])
    r = requests.get(url)
    if r.headers['content-type'].find('pdf') > -1:
        return r.url
    elif r.headers['content-type'].find('html') > -1:
        return 'error: Nature says ACCESS DENIED'
    else:
        return None

# the doi2step_journals should work in nature_journals, but the urls are weird. 
# e.g. http://www.nature.com/gim/journal/v8/n11/pdf/gim2006115a.pdf
#      http://www.nature.com/jid/journal/v113/n2/full/5603216a.html
doi2step_journals = [ 'Genet Med', 'J Invest Dermatol' ]

# TODO
#
#21196708: no URL because No URL format for Journal Dermatology (Basel)
#21196779: no URL because No URL format for Journal Nephron Physiol
#21198350: no URL because No URL format for Journal Genet Test Mol Biomarkers
#21198393: no URL because No URL format for Journal Genet Test Mol Biomarkers
#21198395: no URL because No URL format for Journal Genet Test Mol Biomarkers
#21198797: no URL because No URL format for Journal Clin Exp Dermatol
#21199372: no URL because No URL format for Journal Basic Clin Pharmacol Toxicol
#20607725: no URL because No URL format for Journal Mol Carcinog
#16401428: no URL because No URL format for Journal Curr Biol
#15533574: no URL because No URL format for Journal Int J Pediatr Otorhinolaryngol
#15533621: no URL because No URL format for Journal Med Hypotheses
#15234147: no URL because No URL format for Journal Ophthalmology
#15234312: no URL because No URL format for Journal Am J Ophthalmol
#15234655: no URL because No URL format for Journal Am J Med
#17100396: no URL because No URL format for Journal J Med Assoc Thai
#17413447: no URL because No URL format for Journal Psychiatr. Genet.
#17414143: no URL because No URL format for Journal J. Pediatr. Gastroenterol. Nutr.
#17415575: no URL because No URL format for Journal Arch. Dermatol. Res.
#17415800: no URL because No URL format for Journal Mov. Disord.
#17416296: no URL because No URL format for Journal Arch. Med. Res.
#17143317: no URL because No URL format for Journal Nat Clin Pract Endocrinol Metab
#17145028: no URL because No URL format for Journal Med Clin (Barc)
#17145065: no URL because No URL format for Journal Mutat Res
#15452722: no URL because No URL format for Journal Graefes Arch Clin Exp Ophthalmol
#15453866: no URL because No URL format for Journal Acta Ophthalmol Scand


# Below: Journals with really annoying paywalls guarding their precious secrets.
schattauer_journals = [
    'Thromb Haemost',
    ]

wolterskluwer_journals = [
    'Clin Dysmorphol',
    'J Hypertens',
    'J Glaucoma',
    'Obstet Gynecol',
    'Pharmacogenet Genomics',
    'Pharmacogenetics',
    'Plast Reconstr Surg',
    ]

karger_journals = [
    'Cytogenet Genome Res',
    'Horm Res',
    'Hum Hered',
    ]

springer_journals = [
    'Acta Neuropathol',
    'Ann Surg Oncol',
    'Breast Cancer Res Treat',
    'Cell Mol Neurobiol',
    'Diabetologia',
    'Eur J Pediatr',
    'Fam Cancer',
    'HNO',
    'Hum Genet',
    'Immunogenetics',
    'J Bone Miner Metab',
    'J Endocrinol Invest',
    'J Inherit Metab Dis',
    'J Neurol',
    'J Mol Med (Berl)',
    'J Mol Neurosci',
    'Mod Rheumatol',
    'Neurogenetics',
    'Ophthalmologe',
    'Pediatr Nephrol',
    'Physiol Genomics',
    ]

# thieme journals so far don't seem to have any open access content.
# example links to article page: https://www.thieme-connect.com/DOI/DOI?10.1055/s-0028-1085467
#           https://www.thieme-connect.com/DOI/DOI?10.1055/s-2007-1004566
thieme_journals = ['Neuropediatrics', 'Semin Vasc Med', 'Exp Clin Endocrinol Diabetes']

paywall_journals = schattauer_journals + wolterskluwer_journals + springer_journals + thieme_journals + karger_journals


def find_article_from_doi(doi):
    #1) lookup on CrossRef
    #2) pull a PubMedArticle based on CrossRef results
    #3) run it through find_article_from_pma
    pma = fetch.article_by_pmid(doi2pmid(doi))
    return find_article_from_pma(pma)
    

PMC_PDF_URL = 'http://www.ncbi.nlm.nih.gov/pmc/articles/pmid/{a.pmid}/pdf'
def get_pdf_url_from_pmc_unless_embargoed(pma):
    url = PMC_PDF_URL.format(a=pma)
    r = requests.get(url)
    if r.headers['content-type'].find('html') > -1:
        return None
    else:
        return url


def find_article_from_pma(pma, crossref_doi=True, paywalls=False):
    reason = None
    url = None

    jrnl = pma.journal.translate(None, '.')

    if pma.pmc:
        url = get_pdf_url_from_pmc_unless_embargoed(pma)
        if url:
            return url, reason

    if jrnl in simple_formats_pii.keys():
        if pma.pii:
            url = simple_formats_pii[jrnl].format(a=pma)
            r = requests.get(url)
            if r.text.find('Access Denial') > -1:
                reason = 'error: ScienceDirect says ACCESS DENIED'
                url = None
            return url, reason
        else:
            reason = 'pii missing from PubMedArticle XML'

    if pma.doi==None and crossref_doi:
        pma.doi = PubMedArticle2doi(pma)
        if pma.doi==None:
            reason = 'DOI missing from PubMedArticle and CrossRef lookup failed.'
        else:
            reason = 'DOI missing from PubMedArticle.'
 
    if jrnl in simple_formats_doi.keys():
        if pma.doi != None:
            url = simple_formats_doi[jrnl].format(a=pma)
            reason = ''

    elif jrnl in doi2step_journals:
        if pma.doi:
            try:
                baseurl = the_doi_2step(pma.doi)
                url = baseurl.replace('full', 'pdf').replace('html', 'pdf')
                reason = ''
            except MetaPubError, e:
                reason = '%s' % e

    elif jrnl in jstage_journals:
        if pma.doi:
            result = exit_jstage_left(pma)
            if result.find('error') > -1:
                reason = result
                url = None
            else:
                reason = None
                url = result

    elif jrnl in wiley_journals:
        if pma.doi:
            url = the_wiley_shuffle(pma)
            if url.find('error') > -1:
                reason = url
                url = None

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
        result = the_nature_show(pma)
        if result.find('error') > -1:
            reason = result
            url = None
        else:
            url = result

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
            if url.find('error') > -1:
                reason = url
                url = None
        else:
            reason = 'pii missing from PubMedArticle XML (%s in ScienceDirect format)' % jrnl

    elif jrnl in paywall_journals:
        if paywalls == False:
            reason = '%s behind obnoxious paywall' % jrnl
        else:
            reason = '%s in paywall; not yet smart enough to navigate paywalls, sorry!' % jrnl

    elif jrnl in todo_journals:
        reason = 'TODO format -- example: %s' % todo_journals[jrnl]['example']

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
            print self.pmid
            try:
                self.url, self.reason = find_article_from_pma(self.pma, paywalls=self.paywalls)
            except requests.exceptions.ConnectionError, e:
                self.url = None
                self.reason = 'tx_error: %r' % e

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


