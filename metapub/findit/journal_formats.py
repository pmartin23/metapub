# journals whose articles can best be accessed by loading up via dx.doi.org
#       and then doing some text replacement on the URL.
doi2step_journals = (
    # ex.
    # http://www.palgrave-journals.com/jphp/journal/v36/n2/pdf/jphp201453a.pdf
    'J Public Health Policy'
)

todo_journals = {
    'Pharmacol Rep': {'example': 'http://www.ncbi.nlm.nih.gov/pubmed/?term=23238479[uid] --> www.if-pan.krakow.pl/pjp/pdf/2012/5_1234.pdf'},
    'Med Sci Monit': {'example': 'http://www.medscimonit.com/download/index/idArt/869530'},
    'Asian Pac J Cancer Prev': {'example': 'http://www.apocpcontrol.org/paper_file/issue_abs/Volume12_No7/1771-1776%20c%206.9%20Lei%20Zhong.pdf'},
    'Rev Esp Cardiol': {'example': 'http://www.revespcardiol.org/en/linkresolver/articulo-resolver/13131646/'},
    'Ann Dermatol Venereol': {'example': 'http://www.em-consulte.com/article/152959/alertePM'},
    'Mol Cells': {'example': 'http://www.molcells.org/journal/view.html?year=2004&volume=18&number=2&spage=141 --> http://pdf.medrang.co.kr/KSMCB/2004/018/mac-18-2-141.pdf'},
    'Mol Vis': {'example': 'http://www.molvis.org/molvis/v10/a45/ --> http://www.molvis.org/bin/pdf.cgi?Zheng,10,45'},
    'Singapore Med J': {'example': 'http://www.sma.org.sg/smj/4708/4708cr4.pdf'},
    'Rev Port Cardiol': {'example': '16335287: http://www.spc.pt/DL/RPC/artigos/74.pdf'},
    'World J Gastroenterol': {'example': 'http://www.wjgnet.com/1007-9327/full/v11/i48/7690.htm --> http://www.wjgnet.com/1007-9327/pdf/v11/i48/7690.pdf'},
    'Genet Mol Res': {'example': '24668667: http://www.geneticsmr.com/articles/2992 --> http://www.geneticsmr.com//year2014/vol13-1/pdf/gmr2764.pdf'},
    'Arq Bras Cardiol': {'example': '20944894: http://www.scielo.br/pdf/abc/v95n5/en_aop13210.pdf'},
    'Arq Bras Endocrinol Metabol': {'example': '15611820: http://www.scielo.br/pdf/abem/v48n1/19521.pdf'},
    'Neoplasma': {'example': '17319787: http://www.elis.sk/download_file.php?product_id=1006&session_id=skl2f3grcd19ebnie17u15a571'},
    'Clinics (Sao Paulo)': {'example': '17823699: http://www.scielo.br/scielo.php?script=sci_arttext&pid=S1807-59322007000400003'},
    'Mem Inst Oswaldo Cruz': {'example': '17308790: http://www.scielo.br/scielo.php?script=sci_pdf&pid=S0074-02762006000900051 --> http://www.scielo.br/pdf/mioc/v101s1/v101s1a51.pdf'},
    'Asian J Androl': {'example': '18097502: http://www.asiaandro.com/Abstract.asp?doi=10.1111/j.1745-7262.2008.00376.x'},
    'Anesthesiology': {'example': '18212565: http://dx.doi.org/10.1097/01.anes.0000299431.81267.3e --> html w/ <a id="pdfLink" data-article-url="THE_URL">'},
    'Nat Prod Commun': {'example': '19634325 (no direct link found yet) -- http://www.naturalproduct.us/'},
    'Oncotarget': {'example': '26008984 (pii = 3900) --> http://www.impactjournals.com/oncotarget/index.php?journal=oncotarget&page=article&op=view&path=3900'},
    'Clin Ter': {'example': '25756258 --> dx.doi.org/10.7417/CT.2015.1799 --> parse page to get PDF'},
    'J Pediatr (Rio J)': {'example': '17102902 --> dx.doi.org/10.2223/JPED.1550 --> http://www.jped.com.br/conteudo/06-82-06-437/port.pdf'},
    'Teach Learn Med': {'example': '17144842 --> dx.doi.org/10.1207/s15328015tlm1804_13 --> pdf link?'},
    'Med Clin (Barc)': {'example': '17145028 --> http://www.elsevier.es/es-revista-medicina-clinica-2-linkresolver-alopecia-androgenica-prematura-un-varon-13094419 --> http://apps.elsevier.es/watermark/ctl_servlet?_f=10&pident_articulo=13094419&pident_usuario=0&pcontactid=&pident_revista=2&ty=94&accion=L&origen=zonadelectura&web=www.elsevier.es&lan=es&fichero=2v127n16a13094419pdf001.pdf'},
    'Int J Syst Evol Microbiol': {'example': '18175687 --> http://ijs.sgmjournals.org/content/journal/ijsem/10.1099/ijs.0.65305-0 --> pdf link'},
    'J Gen Virol': {'example': '8757995 --> http://jgv.sgmjournals.org/content/journal/jgv/10.1099/0022-1317-77-7-1521 --> pdf'},
}


format_templates = {
    'acs': 'http://pubs.acs.org/doi/pdf/{a.doi}',
    'akademii': 'http://www.akademiai.com/content/{a.pii}/fulltext.pdf',
    'ats': 'http://www.atsjournals.org/doi/pdf/{a.doi}',
    'futuremed': 'http://www.futuremedicine.com/doi/pdf/{a.doi}',
    'informa': 'http://informahealthcare.com/doi/pdf/{a.doi}',
    'lancet': 'http://www.thelancet.com/pdfs/journals/{ja}/PII{a.pii}.pdf',
    'liebert': 'http://online.liebertpub.com/doi/pdf/{a.doi}',
    'plos': 'http://www.plosbiology.org/article/fetchObjectAttachment.action?url=info:doi/{a.doi}&representation=PDF',
    'taylor_francis': 'http://www.tandfonline.com/doi/pdf/{a.doi}',
    'wiley': 'http://onlinelibrary.wiley.com/doi/{a.doi}/pdf',
    'jci': 'http://www.jci.org/articles/view/{a.pii}/pdf',
}

# JCI == Journal of Clinical Investigation
jci_journals = ['J Clin Invest']

# TODO: Dustri Dance
# Dustri: see http://www.dustri.com/journals-in-english.html
dustri_journals = (
    'Clin Nephrol', 'Int J Clin Pharmacol Ther', 'Clin Neuropathol')

# Portlan Press Biochemical Society journals: mostly VIP.
# TODO: detect and redo urls for "early" releases, e.g.:
#      http://www.clinsci.org/content/ppclinsci/early/2015/06/10/CS20150073.full.pdf
biochemsoc_journals = {'Biochem J': {'host': 'www.biochemj.org', 'ja': 'ppbiochemj'},
                       'Clin Sci': {'host': 'www.clinsci.org', 'ja': 'ppclinsci'},
                       }
biochemsoc_format = 'http://{host}/content/{ja}/{a.volume}/{a.issue}/{a.first_page}.full.pdf'

lancet_journals = {
    'Lancet': {'ja': 'lancet'},
    'Lancet Diabetes Endocrinol': {'ja': 'landia'},
    'Lancet Glob Health': {'ja': 'langlo'},
    'Lancet Haematol': {'ja': 'lanhae'},
    'Lancet HIV': {'ja': 'lanhiv'},
    'Lancet Infect Dis': {'ja': 'laninf'},
    'Lancet Neurol': {'ja': 'laneur'},
    'Lancet Oncol': {'ja': 'lanonc'},
    'Lancet Psychiatry': {'ja': 'lanpsy'},
    'Lancet Respir Med': {'ja': 'lanres'},
}


# the SD journals are also represented in simple_formats_pii
# "piit" means pii-translated (i.e. punctuation removed)
sciencedirect_url = 'http://www.sciencedirect.com/science/article/pii/{piit}'
sciencedirect_journals = (
    'Acad Pediatr',
    'Ann Genet',
    'Ann Vasc Surg',
    'Am J Kidney Dis',
    'Am J Otolaryngol',
    'Am J Pathol',
    'Am J Prev Med',
    'Ambul Pediatr',
    'Appetite',
    'Arch Biochem Biophys',
    'Arch Med Res',
    'Arch Oral Biol',
    'Arch Pediatr',
    'Atherosclerosis',
    'Blood Cells Mol Dis',
    'Biochem Biophys Res Commun',
    'Biochem Pharmacol',
    'Biochim Biophys Acta',
    'Bioorg Med Chem',
    'Biophys Chem',
    'Br J Oral Maxillofac Surg',
    'Brain Res',
    'Cell Signal',
    'Chem Biol Interact',
    'Child Abuse Negl',
    'Clin Chim Acta',
    'Clin Immunol',
    'Contemp Clin Trials',
    'Contraception',
    'Crit Care Clin',
    'Cytokine',
    'Diabetes Metab Syndr',
    'Fam Pract',
    'FEBS Lett',
    'Eur J Cancer',
    'Eur J Med Chem',
    'Eur J Med Genet',
    'Eur J Obstet Gynecol Reprod Biol',
    'Eur J Pharmacol',
    'Exp Cell Res',
    'Exp Eye Res',
    'Exp Neurol',
    'Exp Parasitol',
    'Eur Urol',
    'Gene',
    'Genomics',
    'Gynecol Obstet Fertil',
    'Hepatol Res',
    'Hum Immunol',
    'Hum Pathol',
    'Infect Genet Evol',
    'Int J Antimicrob Agents',
    'Int J Biochem Cell Biol',
    'Int J Pediatr Otorhinolaryngol',
    'Int J Pharm',
    'J Acad Nutr Diet',
    'J Affect Disord',
    'J Allergy Clin Immunol',
    'J Am Coll Cardiol',
    'J Am Diet Assoc',
    'J Adolesc Health',
    'J Autoimmun',
    'J Biosci Bioeng',
    'J Biotechnol',
    'J Cardiol',
    'J Chromatogr A',
    'J Clin Neurosci',
    'J Dairy Sci',
    'J Dermatol Sci',
    'J Environ Sci (China)',
    'J Health Econ',
    'J Immunol Methods',
    'J Inorg Biochem',
    'J Mol Biol',
    'J Mol Graph Model',
    'J Neuroimmunol',
    'J Neurol Sci',
    'J Pediatr',
    'J Pediatr Health Care',
    'J Psychiatr Res',
    'J Reprod Immunol',
    'J Steroid Biochem Mol Biol',
    'J Struct Biol',
    'J Urol',
    'J Virol Methods',
    'Leuk Res',
    'Life Sci',
    'Lung Cancer',
    'Mayo Clin Proc',
    'Meth Enzymol',
    'Mitochondrion',
    'Mol Cell Endocrinol',
    'Mol Cell Probes',
    'Mol Genet Metab',
    'Mol Immunol',
    'Mutat Res',
    'Neurobiol Dis',
    'Neuromuscul Disord',
    'Neuropharmacology',
    'Neurosci Lett',
    'Neurosci Res',
    'Neuroscience',
    'Neurotoxicology',
    'Nitric Oxide',
    'Nutr Metab Cardiovasc Dis',
    'Oral Oncol',
    'Parkinsonism Relat Disord',
    'Patient Educ Couns',
    'Pediatr Nurs',
    'Pediatr Pulmonol',
    'Peptides',
    'Prog Neuropsychopharmacol Biol Psychiatry',
    'Protein Expr Purif',
    'Psychiatry Res',
    'Sci Total Environ',
    'Soc Sci Med',
    'Toxicol In Vitro',
    'Transplant Proc',
    'Trends Biochem Sci',
    'Vaccine',
    'Vet Microbiol',
    'Virology',
    'Virus Res',
)


jama_journals = (
    'Arch Dermatol',
    'Arch Gen Psychiatry',
    'Arch Neurol',
    'Arch Ophthalmol',
    'Arch Surg',
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
)

# TODO
# doiserbia (Library of Serbia) articles can be grabbed by doing the_doi_2step,
# then ...?
doiserbia_journals = ['Genetika']

# JSTAGE: mostly free (yay)
# Examples:
# J Biochem: https://www.jstage.jst.go.jp/article/biochemistry1922/125/4/125_4_803/_pdf
# Drug Metab Pharmacokinet:
# https://www.jstage.jst.go.jp/article/dmpk/20/2/20_2_144/_article -->
# https://www.jstage.jst.go.jp/article/dmpk/20/2/20_2_144/_pdf
jstage_journals = (
    'Biol Pharm Bull',
    'Circ J',
    'Drug Metab Pharmacokinet',
    'Endocr J',
    'Genes Genet Syst',
    'Intern Med',
    'J Antibiot',
    'J Biochem',
    'J Periodontol',
    'Tohoku J Exp Med',
)

# cell journals
#cell_format = 'http://download.cell.com{ja}/pdf/PII{pii}.pdf'
cell_format = 'http://www.cell.com{ja}/pdf/{pii}.pdf'
cell_journals = {
    'Am J Hum Genet': {'ja': '/AJHG'},
    'Biophys J': {'ja': '/biophysj'},
    'Cancer Cell': {'ja': '/cancer-cell'},
    'Cell': {'ja': ''},
    'Cell Host Microbe': {'ja': '/cell-host-microbe'},
    'Cell Metab': {'ja': '/cell-metabolism'},
    'Cell Stem Cell': {'ja': '/cell-stem-cell'},
    'Chem Biol': {'ja': '/chemistry-biology'},
    'Curr Biol': {'ja': '/current-biology'},
    'Dev Cell': {'ja': '/developmental-cell'},
    'Immunity': {'ja': '/immunity'},
    'Mol Cell': {'ja': '/molecular-cell'},
    'Neuron': {'ja': '/neuron'},
    'Structure': {'ja': '/structure'},
    'Trends Mol Med': {'ja': '/trends'},
}

# nature journals -- COMPLETE
nature_format = 'http://www.nature.com/{ja}/journal/v{a.volume}/n{a.issue}/pdf/{a.pii}.pdf'
nature_journals = {
    'Eur J Clin Nutr': {'ja': 'ejcn'},
    'Eur J Hum Genet': {'ja': 'ejhg'},
    'Eye (Lond)': {'ja': 'eye'},
    'Genes Immun': {'ja': 'gene'},
    'Genet Med': {'ja': 'gim'},
    'Hypertens Res': {'ja': 'hr'},
    'Int J Obes Relat Metab Disord': {'ja': 'ijo'},
    'Int J Obes (Lond)': {'ja': 'ijo'},
    'J Invest Dermatol': {'ja': 'jid'},
    'J Hum Genet': {'ja': 'jhg'},
    'J Hum Hypertens': {'ja': 'jhh'},
    'Kidney Int': {'ja': 'ki'},
    'Leukemia': {'ja': 'leu'},
    'Mod Pathol': {'ja': 'modpathol'},
    'Mol Psychiatry': {'ja': 'mp'},
    'Nature': {'ja': 'nature'},
    'Nat Chem': {'ja': 'nchem'},
    'Nat Clin Pract Endocrinol Metab': {'ja': 'nrendo'},
    'Nat Clin Pract Cardiovasc Med': {'ja': 'nrcardio'},
    'Nat Clin Pract Oncol': {'ja': 'nrclinonc'},
    'Nat Clin Pract Gastroenterol Hepatol': {'ja': 'nrgastro'},
    'Nat Clin Pract Urol': {'ja': 'nrurol'},
    'Nat Clin Pract Neurol': {'ja': 'nrneurol'},
    'Nat Clin Pract Nephrol': {'ja': 'nrneph'},
    'Nat Clin Pract Rheumatol': {'ja': 'nrrheum'},
    'Nat Genet': {'ja': 'ng'},
    'Nat Commun': {'ja': 'ncomms'},
    'Nat Nanotechnol': {'ja': 'nnano'},
    'Nat Neurosci': {'ja': 'neuro'},
    'Nat Mater': {'ja': 'nmat'},
    'Nat Med': {'ja': 'nm'},
    'Nat Methods': {'ja': 'nmeth'},
    'Nat Protoc': {'ja': 'nprot'},
    'Nat Rev Drug Discov': {'ja': 'nrd'},
    'Nat Rev Cardiol': {'ja': 'nrcardio'},
    'Nat Rev Clin Oncol': {'ja': 'nrclinonc'},
    'Nat Rev Endocrinol': {'ja': 'nrendo'},
    'Nat Rev Genet': {'ja': 'nrg'},
    'Nat Rev Gastroenterol Hepatol': {'ja': 'nrgastro'},
    'Nat Rev Nephrol': {'ja': 'nrneph'},
    'Nat Rev Neurol': {'ja': 'nrneurol'},
    'Nat Rev Rheumatol': {'ja': 'nrrheum'},
    'Nat Rev Urol': {'ja': 'nrurol'},
    'Nat Rev Immunol': {'ja': 'nri'},
    'Neuropsychopharmacology': {'ja': 'npp'},
    'Oncogene': {'ja': 'onc'},
    'Pediatr Res': {'ja': 'pr'},
    'Pharmacogenomics J': {'ja': 'tpj'},
}


# simple_formats_pmid: links to PDFs that can be constructed using the
# pubmed ID
simple_formats_pmid = {
    'Medicina (B Aires)': 'http://www.medicinabuenosaires.com/PMID/{pmid}.pdf',
}


# simple formats are used for URLs that can be deduced from PubMedArticle XML
#
#       !ACHTUNG!  informa has been known to block IPs for the capital offense of
#                  having "More than 25 sessions created in 5 minutes"
#
simple_formats_doi = {
    'Acta Oncol': format_templates['informa'],
    'Ann Hum Biol': format_templates['informa'],
    'Hemoglobin': format_templates['informa'],
    'J Matern Fetal Neonatal Med': format_templates['informa'],
    'Ophthalmic Genet': format_templates['informa'],
    'Platelets': format_templates['informa'],
    'Ren Fail': format_templates['informa'],
    'Xenobiotica': format_templates['informa'],

    'Am J Public Health': 'http://ajph.aphapublications.org/doi/pdf/{a.doi}',
    'Am J Respir Cell Mol Biol': format_templates['ats'],
    'Am J Respir Crit Care Med': format_templates['ats'],

    'Anal Chem': format_templates['acs'],
    'Biochemistry': format_templates['acs'],
    'Chem Res Toxicol': format_templates['acs'],
    'Inorg Chem': format_templates['acs'],
    'J Agric Food Chem': format_templates['acs'],
    'J Am Chem Soc': format_templates['acs'],
    'J Med Chem': format_templates['acs'],
    'J Phys Chem A': format_templates['acs'],

    'Radiat Res': 'http://www.bioone.org/doi/pdf/{a.doi}',

    'AIDS Res Hum Retroviruses': format_templates['liebert'],
    'Antioxid Redox Signal': format_templates['liebert'],
    'Child Obes': format_templates['liebert'],
    'Genet Test': format_templates['liebert'],
    'Genet Test Mol Biomarkers': format_templates['liebert'],
    'Thyroid': format_templates['liebert'],

    'Pharmacogenomics': format_templates['futuremed'],

    'Autophagy': format_templates['taylor_francis'],
    'Biosci Biotechnol Biochem': format_templates['taylor_francis'],
    'Cancer Biol Ther': format_templates['taylor_francis'],
    'Cell Cycle': format_templates['taylor_francis'],
    'Health Commun': format_templates['taylor_francis'],
    'J Biomol Struct Dyn': format_templates['taylor_francis'],

    'Endocrinology': 'http://press.endocrine.org/doi/pdf/{a.doi}',
    'Endocr Rev': 'http://press.endocrine.org/doi/pdf/{a.doi}',
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


simple_formats_pii = {
    'Am Heart J': 'http://www.ahjonline.com/article/{a.pii}/pdf',
    'Am J Cardiol': 'http://www.ajconline.org/article/{a.pii}/pdf',
    'Am J Ophthalmol': 'http://www.ajo.com/article/{a.pii}/pdf',
    'Am J Med': 'http://www.amjmed.com/article/{a.pii}/pdf',
    'Atherosclerosis': 'http://www.atherosclerosis-journal.com/article/{a.pii}/pdf',
    'Arch Med Res': 'http://www.arcmedres.com/article/{a.pii}/pdf',
    'Biol Psychiatry': 'http://www.biologicalpsychiatryjournal.com/article/{a.pii}/pdf',
    'Bone': 'http://www.thebonejournal.com/article/{a.pii}/pdf',
    'Brain Dev': 'http://www.brainanddevelopment.com/article/{a.pii}/pdf',
    'Cancer Cell Int': 'http://www.cancerci.com/content/pdf/{a.pii}.pdf',
    'Cancer Genet Cytogenet': 'http://www.cancergeneticsjournal.org/article/{a.pii}/pdf',
    'Cancer Lett': 'http://www.cancerletters.info/article/{a.pii}/pdf',
    'Clin Neurol Neurosurg': 'http://www.clineu-journal.com/article/{a.pii}/pdf',
    'Diabetes Res Clin Pract': 'http://www.diabetesresearchclinicalpractice.com/article/{a.pii}/pdf',
    'Epilepsy Res': 'http://www.epires-journal.com/article/{a.pii}/pdf',
    'Eur J Paediatr Neurol': 'http://www.ejpn-journal.com/article/{a.pii}/pdf',
    'Exp Hematol': 'http://www.exphem.org/article/{a.pii}/pdf',
    'Fertil Steril': 'http://www.fertstert.org/article/{a.pii}/pdf',
    'Gastroenterology': 'http://www.gastrojournal.org/article/{a.pii}/pdf',
    'Gynecol Oncol': 'http://www.gynecologiconcology-online.net/article/{a.pii}/pdf',
    'Heart Rhythm': 'http://www.heartrhythmjournal.com/article/{a.pii}/pdf',
    'Int J Pediatr Otorhinolaryngol': 'http://www.ijporlonline.com/article/{a.pii}/pdf',
    'Int J Cardiol': 'http://www.internationaljournalofcardiology.com/article/{a.pii}/pdf',
    'J Dermatol': 'http://www.jdsjournal.com/article/{a.pii}/pdf',
    'J Mol Cell Cardiol': 'http://www.jmmc-online.com/article/{a.pii}/pdf',
    'J Mol Diagn': 'http://jmd.amjpathol.org/article/{a.pii}/pdf',
    'J Neurol Sci': 'http://www.jns-journal.com/article/{a.pii}/pdf',
    'J Pediatr': 'http://www.jpeds.com/article/{a.pii}/pdf', 
    'J Pediatr Urol': 'http://www.jpurol.com/article/{a.pii}/pdf',
    'Ophthalmology': 'http://www.aaojournal.org/article/{a.pii}/pdf',
    'Orv Hetil': format_templates['akademii'],
    'Med Hypotheses': 'http://www.medical-hypotheses.com/article/{a.pii}/pdf',
    'Metabolism': 'http://www.metabolismjournal.com/article/{a.pii}/pdf',
    'Metab Clin Exp': 'http://www.metabolismjournal.com/article/{a.pii}/pdf',
    'Mol Genet Metab': 'http://www.mgmjournal.com/article/{a.pii}/pdf',
    'Neurobiol Aging': 'http://www.neurobiologyofaging.org/article/{a.pii}/pdf',
    'Neuromuscul Disord': 'http://www.nmd-journal.com/article/{a.pii}/pdf',
    'Parkinsonism Relat Disord': 'http://www.prd-journal.com/article/{a.pii}/pdf',
    'Pediatr Neurol': 'http://www.pedneur.com/article/{a.pii}/pdf',
    'Placenta': 'http://www.placentajournal.org/article/{a.pii}/pdf',
    'Surg Neurol': 'http://www.worldneurosurgery.org/article/{a.pii}/pdf',
    'Thromb Res': 'http://www.thrombosisresearch.com/article/{a.pii}/pdf',
}

# Many BMC journals start with "BMC" (they're covered automatically) --
# this list covers the ones that don't.  #TODO: Gather up the ones not in
# here yet.
BMC_journals = (
    'Diagn Pathol',
    'Genome Biol',
    'Genome Med',
    'Hum Genomics',
    'J Clin Bioinforma',
    'J Transl Med',
)

# the "aid" is the second half of the DOI string (after the slash)
BMC_format = 'http://www.biomedcentral.com/content/pdf/{aid}.pdf'

# vip = Volume-Issue-Page format
#       URLs that have the same format except for the host name

vip_format = 'http://{host}/content/{a.volume}/{a.issue}/{a.first_page}.full.pdf'

vip_journals = {
    'Ann Clin Biochem': {'host': 'acb.sagepub.com'},
    'Am J Clin Pathol': {'host': 'ajcp.ascpjournals.org'},
    'Am J Hypertens': {'host': 'ajh.oxfordjournals.org'},
    'Am J Physiol Lung Cell Mol Physiol': {'host': 'ajplung.physiology.org'},
    'Am J Physiol, Cell Physiol': {'host': 'ajpcell.physiology.org'},
    'Angiology': {'host': 'ang.sagepub.com'},  # TODO: early release format
    'Ann Oncol': {'host': 'annonc.oxfordjournals.org'},
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://aac.asm.org/cgi/pmidlookup?view=long&pmid=7689822
    'Anticancer Res': {'host': 'ar.iiarjournals.org'},
    'Antimicrob Agents Chemother': {'host': 'aac.asm.org'},
    'Arterioscler Thromb Vasc Biol': {'host': 'atvb.ahajournals.org'},
    'Brain': {'host': 'brain.oxfordjournals.org'},
    'Breast Cancer Res': {'host': 'breast-cancer-research.com'},
    'Br J Anaesth': {'host': 'bja.oxfordjournals.org'},
    'Cancer Discov': {'host': 'cancerdiscovery.aacrjournals.org'},
    'Cancer Epidemiol Biomarkers Prev': {'host': 'cebp.aacrjournals.org'},
    'Cancer Res': {'host': 'cancerres.aacrjournals.org'},
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://www.cfp.ca/cgi/pmidlookup?view=long&pmid=19282532
    'Can Fam Physician': {'host': 'www.cfp.ca'},
    'Carcinogenesis': {'host': 'carcin.oxfordjournals.org'},
    'Cardiovasc Res': {'host': 'cardiovascres.oxfordjournals.org'},
    'Circulation': {'host': 'circ.ahajournals.org'},
    'Circ Arrhythm Electrophysiol': {'host': 'circep.ahajournals.org'},
    'Circ Cardiovasc Genet': {'host': 'circgenetics.ahajournals.org'},
    'Circ Res': {'host': 'circres.ahajournals.org'},
    'Clin Appl Thromb Hemost': {'host': 'cat.sagepub.com'},
    'Clin Cancer Res': {'host': 'clincancerres.aacrjournals.org'},
    'Clin Chem': {'host': 'clinchem.org'},
    'Clin Infect Dis': {'host': 'cid.oxfordjournals.org'},
    'Clin Pediatr': {'host': 'cpj.sagepub.com'},
    'Clin Pediatr (Phila)': {'host': 'cpj.sagepub.com'},
    'Diabetes': {'host': 'diabetes.diabetesjournals.org'},
    'Diabetes Care': {'host': 'care.diabetesjournals.org'},
    'Drug Metab Dispos': {'host': 'dmd.aspetjournals.org'},
    # TODO: backup_url: pmid lookup strategy,
    # http://emboj.embopress.org/cgi/pmidlookup?view=long&pmid=9501081
    'EMBO J': {'host': 'emboj.embopress.org'},
    'Endocr Relat Cancer': {'host': 'erc.endocrinology-journals.org'},
    'Eur Heart J': {'host': 'eurheartj.oxfordjournals.org'},
    'Eur J Endocrinol': {'host': 'eje-online.org'},
    'Eur Respir J': {'host': 'erj.ersjournals.com'},
    'FASEB J': {'host': 'fasebj.org'},
    'FEMS Microbiol Lett': {'host': 'femsle.oxfordjournals.org'},
    'Genome Biol': {'host': 'genomebiology.com'},
    'Genome Res': {'host': 'genome.cshlp.org'},
    'Genes Dev': {'host': 'genesdev.cshlp.org'},
    'Gut': {'host': 'gut.bmj.com'},
    'Haematologica': {'host': 'haematologica.org'},
    'Hum Mol Genet': {'host': 'hmg.oxfordjournals.org'},
    'Hum Reprod': {'host': 'humrep.oxfordjournals.org'},
    'Hypertension': {'host': 'hyper.ahajournals.org'},
    'Invest Ophthalmol Vis Sci': {'host': 'www.iovs.org'},
    'IOVS': {'host': 'iovs.org'},
    # TODO: backup_url: pmid lookup strategy,
    # http://jah.sagepub.com/cgi/pmidlookup?view=long&pmid=20056814
    'J Aging Health': {'host': 'jah.sagepub.com'},
    'J Am Soc Nephrol': {'host': 'jasn.asnjournals.org'},
    'J Antimicrob Chemother': {'host': 'jac.oxfordjournals.org'},
    # TODO: backup_url: pmid lookup strategy,
    # http://jb.asm.org/cgi/pmidlookup?view=long&pmid=7683021
    'J Bacteriol': {'host': 'jb.asm.org'},
    # TODO backup_url: pmid lookup strategy, e.g.
    # http://www.jbc.org/cgi/pmidlookup?view=long&pmid=14722075
    'J Biol Chem': {'host': 'www.jbc.org'},
    'J Cell Biol': {'host': 'jcb.rupress.org'},
    'J Cell Sci': {'host': 'jcs.biologists.org'},
    'J Child Neurol': {'host': 'jcn.sagepub.com'},
    'J Clin Endocrinol Metab': {'host': 'jcem.endojournals.org'},
    'J Clin Oncol': {'host': 'jco.ascopubs.org'},
    'J Dent Res': {'host': 'jdr.sagepub.com'},
    'J Endocrinol': {'host': 'joe.endocrinology-journals.org'},
    'J Exp Med': {'host': 'jem.rupress.org'},
    'J Gerontol A Biol Sci Med Sci': {'host': 'biomedgerontology.oxfordjournals.org'},
    'J Hum Lact': {'host': 'jhl.sagepub.com'},
    'J Immunol': {'host': 'jimmunol.org'},
    'J Infect Dis': {'host': 'jid.oxfordjournals.org'},
    'J Lipid Res': {'host': 'www.jlr.org'},
    'J Med Genet': {'host': 'jmg.bmj.com'},
    'J Mol Endocrinol': {'host': 'jme.endocrinology-journals.org'},
    'J Natl Cancer Inst': {'host': 'jnci.oxfordjournals.org'},
    'J Neurol Neurosurg Psychiatry': {'host': 'jnnp.bmj.com'},
    'J Neurosci': {'host': 'jneurosci.org'},
    # TODO:  backup_url: pmid lookup strategy,
    # http://jn.nutrition.org/cgi/pmidlookup?view=long&pmid=10736367
    'J Nutr': {'host': 'jn.nutrition.org'},
    'J Pharmacol Exp Ther': {'host': 'jpet.aspetjournals.org'},
    'J Rheumatol': {'host': 'www.jrheum.org'},
    'J Renin Angiotensin Aldosterone Syst': {'host': 'jra.sagepub.com'},
    'J Virol': {'host': 'jvi.asm.org'},
    'Lupus': {'host': 'lup.sagepub.com'},
    'Mol Biol Cell': {'host': 'molbiolcell.org'},
    'Mol Cell Biol': {'host': 'mcb.asm.org'},
    'Mol Canc Therapeut': {'host': 'mct.aacrjournals.org'},
    'Mol Cancer Ther': {'host': 'mct.aacrjournals.org'},
    'Mol Hum Reprod': {'host': 'molehr.oxfordjournals.org'},
    'Mol Pharmacol': {'host': 'molpharm.aspetjournals.org'},
    'Mutagenesis': {'host': 'mutage.oxfordjournals.org'},
    'Neurology': {'host': 'neurology.org'},
    'Nephrol Dial Transplant': {'host': 'ndt.oxfordjournals.org'},
    'Nucleic Acids Res': {'host': 'nar.oxfordjournals.org'},
    'Orphanet J Rare Dis': {'host': 'ojrd.com'},
    'Pediatrics': {'host': 'pediatrics.aappublications.org'},
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://physiolgenomics.physiology.org/cgi/pmidlookup?view=long&pmid=15252189
    'Physiol Genomics': {'host': 'physiolgenomics.physiology.org'},
    # TODO:  backup_url: pmid lookup strategy, e.g.
    # http://www.plantcell.org/cgi/pmidlookup?view=long&pmid=9501112
    'Plant Cell': {'host': 'www.plantcell.org'},
    'Plant Cell Physiol': {'host': 'pcp.oxfordjournals.org'},
    'Proc Natl Acad Sci USA': {'host': 'pnas.org'},
    'Protein Eng': {'host': 'peds.oxfordjournals.org'},
    'Protein Eng Des Sel': {'host': 'peds.oxfordjournals.org'},
    'QJM': {'host': 'qjmed.oxfordjournals.org'},
    'Rheumatology (Oxford)': {'host' 'rheumatology.oxfordjournals.org'},
    'Science': {'host': 'sciencemag.org'},
    'Stroke': {'host': 'stroke.ahajournals.org'},
    'Thorax': {'host': 'thorax.bmj.com'},
}

# volume-issue-page type URLs but with a nonstandard baseurl construction.
# e.g. Blood: http://www.bloodjournal.org/content/bloodjournal/79/10/2507.full.pdf
#      BMJ:   http://www.bmj.com/content/bmj/350/bmj.h3317.full.pdf
# Thorax:
# http://thorax.bmj.com/content/early/2015/06/23/thoraxjnl-2015-207199.full.pdf+html

# no trailing slash in baseurl (please)
vip_journals_nonstandard = {
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://www.bloodjournal.org/cgi/pmidlookup?view=long&pmid=1586703
    'Blood': 'http://www.bloodjournal.org/content/bloodjournal/{a.volume}/{a.issue}/{a.first_page}.full.pdf',
    'BMJ':   'http://www.bmj.com/content/bmj/{a.volume}/bmj.{a.first_page}.full.pdf',
}

# Science (AAAS) -- requires login "as a courtesy to the community".  Mkay.
aaas_format = 'http://{ja}.sciencemag.org/content/{a.volume}/{a.issue}/{a.pages}.full.pdf'
aaas_journals = {
    'Science': {'ja': 'www'},
    'Sci Adv': {'ja': 'advances'},
    'Sci Signal': {'ja': 'stke'},
    'Sci Transl Med': {'ja': 'stm'},
}


# Spandidos: volume/issue/firstpage AND a journal abbreviation. Fancy.
spandidos_format = 'http://www.spandidos-publications.com/{ja}/{a.volume}/{a.issue}/{a.first_page}/download'
spandidos_journals = {
    'Int J Oncol': {'ja': 'ijo'},
    'Int J Mol Med': {'ja': 'ijmm'},
    'Oncol Lett': {'ja': 'ol'},
    'Oncol Rep': {'ja': 'or'},
    'Rinsho Byori': {'ja': 'ijmm'},
}


wiley_journals = (
    'Acta Neurol Scand',
    'Acta Ophthalmol Scand',
    'Acta Paediatr',
    'Allergy',
    'Anim Genet',
    'Ann Hum Genet',
    'Ann Neurol',
    'Am J Hematol',
    'Am J Med Genet',
    'Am J Med Genet A',
    'Am J Med Genet B Neuropsychiatr Genet',
    'Andrologia',
    'Arthritis Rheum',
    'Australas J Dermatol',
    'Basic Clin Pharmacol Toxicol',
    'Biopolymers',
    'Biotechnol Bioeng',
    'Birth Defects Res A Clin Mol Teratol',
    'BJU Int',
    'Breast J',
    'Br J Dermatol',
    'Br J Clin Pharmacol',
    'Br J Haematol',
    'Cancer',
    'Cancer Sci',
    'Chembiochem',
    'Chemistry',
    'Clin Endocrinol (Oxf)',
    'Clin Exp Allergy',
    'Clin Exp Dermatol',
    'Clin Genet',
    'Clin Pharmacol Ther',
    'Diabet Med',
    'Dev Dyn',
    'Dev Med Child Neurol',
    'Electrophoresis',
    'Environ Mol Mutagen',
    'Epilepsia',
    'Eur J Biochem',
    'Eur J Clin Invest',
    'Eur J Haematol',
    'Eur J Immunogenet',
    'Eur J Neurol',
    'Eur J Neurosci',
    'Exp Dermatol',
    'FEBS J',
    'Genes Brain Behav',
    'Genes Cells',
    'Genes Chromosomes Cancer',
    'Genet Epidemiol',
    'Haemophilia',
    'Head Neck',
    'Headache',
    'Hepatology',
    'HIV Med',
    'Hum Brain Mapp',
    'Hum Mutat',
    'Immunol Rev',
    'Int J Androl',
    'Int J Cancer',
    'Int J Dermatol',
    'Int J Immunogenet',
    'Int J Lab Hematol',
    'Int J Pept Protein Res',
    'J Am Assoc Nurse Pract',
    'J Bone Miner Res',
    'J Cell Biochem',
    'J Cell Physiol',
    'J Clin Lab Anal',
    'J Dermatol',
    'J Eur Acad Dermatol Venereol',
    'J Gastroenterol Hepatol',
    'J Intern Med',
    'J Med Virol',
    'J Neurochem',
    'J Neurosci Res',
    'J Oral Rehabil',
    'J Orthop Res',
    'J Pathol',
    'J Pept Sci',
    'J Physiol',
    'J Rural Health',
    'J Sch Health',
    'J Thromb Haemost',
    'J Viral Hepat',
    'Liver Int',
    'Med Educ',
    'Mol Carcinog',
    'Mol Microbiol',
    'Mol Plant Pathol',
    'Mov Disord',
    'Muscle Nerve',
    'Neurogastroenterol Motil',
    'Neuropathol Appl Neurobiol',
    'Nihon Shokakibyo Gakkai Zasshi',
    'Obesity (Silver Spring)',
    'Pain Med',
    'Pediatr Allergy Immunol',
    'Pediatr Blood Cancer',
    'Pediatr Diabetes',
    'Pediatr Int',
    'Pediatr Transplant',
    'Pest Manag Sci',
    'Photochem Photobiol',
    'Plant J',
    'Prenat Diagn',
    'Prostate',
    'Protein Sci',
    'Proteins',
    'Scand J Immunol',
    'Tissue Antigens',
    'Traffic',
    'Transfus Med',
    'Transfusion',
    'Vox Sang',
    'Wound Repair Regen',
    'Yeast',
)

# TODO: De Gruyter (publisher)
#
# examples:
# 26110471 Arh Hig Rada Toksikol http://www.degruyter.com/view/j/aiht.2015.66.issue-2/aiht-2015-66-2582/aiht-2015-66-2582.xml
# 12199344: J. Pediatr. Endocrinol. Metab.
# 25390015: Horm Mol Biol Clin Investig
#
# load by dx.doi.org: http://dx.doi.org/10.2478/cdth-2014-0001
#       --> http://www.degruyter.com/view/j/cdth.2014.1.issue-1/cdth-2014-0001/cdth-2014-0001.xml
# PDF -->
# http://www.degruyter.com/dg/viewarticle.fullcontentlink:pdfeventlink/$002fj$002fcdth.2014.1.issue-1$002fcdth-2014-0001$002fcdth-2014-0001.pdf?t:ac=j$002fcdth.2014.1.issue-1$002fcdth-2014-0001$002fcdth-2014-0001.xml

degruyter_journals = ('Arh Hig Rada Toksikol',
                      'J Pediatr Endocrinol Metab',
                      'Horm Mol Biol Clin Investig',
                      )
# Below: Journals with really annoying paywalls guarding their precious
# secrets.
schattauer_journals = [
    'Thromb Haemost',
]

# Royal Society of Chemistry
RSC_journals = ['Nat Prod Rep']

wolterskluwer_journals = [
    'AIDS',
    'Blood Coagul Fibrinolysis',
    'Clin Dysmorphol',
    'Curr Opin Hematol',
    'Eur J Gastroenterol Hepatol',
    'Fam Community Health',
    'J Dev Behav Pediatr',
    'J Glaucoma',
    'J Hypertens',
    'J Investig Med',
    'J Neuropathol Exp Neurol',
    'J Pediatr Hematol Oncol',
    'J Pediatr Gastroenterol Nutr',
    'J Trauma',
    'Medicine (Baltimore)',
    'Neuroreport',
    'Obstet Gynecol',
    'Pediatr Emerg Care',
    'Pediatr Infect Dis J',
    'Pharmacogenet Genomics',
    'Pharmacogenetics',
    'Plast Reconstr Surg',
    'Psychiatr Genet',
    'Retina (Philadelphia, Pa)',
]

# karger: mostly paywalled, but sometimes...
# http://www.karger.com/Article/Pdf/351538

karger_journals = (
    'Acta Haematol',
    'Ann Nutr Metab',
    'Cell Physiol Biochem',
    'Cerebrovasc Dis',
    'Cytogenet Genome Res',
    'Dermatology (Basel)',
    'Eur Neurol',
    'Fetal Diagn Ther',
    'Gynecol Obstet Invest',
    'Horm Res',
    'Horm Res Paediatr',
    'Hum Hered',
    'Int Arch Allergy Immunol',
    'Nephron',
    'Nephron Physiol',
    'Neuropsychobiology',
    'Urol Int',
)

# springer is mostly paywalled, but sometimes...
# http://link.springer.com/content/pdf/10.1007%2Fs13238-015-0153-5.pdf
springer_journals = [
    'Acta Neuropathol',
    'Adv Exp Med Biol',
    'Ann Hematol',
    'Ann Surg Oncol',
    'Arch Dermatol Res',
    'Arch Virol',
    'Biochem Genet',
    'Biochemistry Mosc',
    'Biotechnol Lett',
    'Breast Cancer Res Treat',
    'Calcif Tissue Int',
    'Cancer Chemother Pharmacol',
    'Cell Mol Neurobiol',
    'Diabetologia',
    'Dig Dis Sci',
    'Endocrine',
    'Eur J Clin Pharmacol',
    'Eur J Pediatr',
    'Eur J Nutr',
    'Fam Cancer',
    'Graefes Arch Clin Exp Ophthalmol',
    'HNO',
    'Hum Genet',
    'Immunogenetics',
    'Int J Colorectal Dis',
    'Int J Hematol',
    'J Appl Genet',
    'J Bone Miner Metab',
    'J Biol Inorg Chem',
    'J Biomol NMR',
    'J Cancer Res Clin Oncol',
    'J Clin Immunol',
    'J Endocrinol Invest',
    'J Inherit Metab Dis',
    'J Neural Transm',
    'J Neurol',
    'J Neurooncol',
    'J Mol Evol',
    'J Mol Med',
    'J Mol Med (Berl)',
    'J Mol Model',
    'J Mol Neurosci',
    'Matern Child Health J',
    'Med Oncol',
    'Methods Mol Biol',
    'Mod Rheumatol',
    'Mol Biol Rep',
    'Mol Cell Biochem',
    'Mol Genet Genomics',
    'Neurogenetics',
    'Neurol Sci',
    'Ophthalmologe',
    'Osteoporos Int',
    'Pediatr Nephrol',
    'Pflugers Arch',
    'Pharm Res',
    'Plant Cell Rep',
    'Protein Cell',
    'Schizophr Res',
    'Rheumatol Int',
    'Tumour Biol',
    'Virchows Arch',
    'Virus Genes',
    'World J Surg',
]

# thieme journals so far don't seem to have any open access content.
# example links to article page: https://www.thieme-connect.com/DOI/DOI?10.1055/s-0028-1085467
#           https://www.thieme-connect.com/DOI/DOI?10.1055/s-2007-1004566
thieme_journals = ['Neuropediatrics', 'Semin Vasc Med', 'Exp Clin Endocrinol Diabetes',
                   'Int J Sports Med', 'Horm Metab Res', ]

weird_paywall_publishers = ['J Ment Health Policy Econ']

paywall_journals = schattauer_journals + wolterskluwer_journals + \
    thieme_journals + weird_paywall_publishers


# All in PMC (no need to write formats for):
# Nat Comput
# Nat Clim Chang
# Nat Geosci
# Nat Resour Model
# Nat Lang Linguist Theory
# Nat Photonics
# Nat Phys
# Nat Prod Bioprospect
# Nat Lang Eng
# Nat Rep Stem Cells
# Nat Sci (Irvine)
# Nat Sci Sleep
