from __future__ import absolute_import, unicode_literals

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
    'Assessment': {'host': 'asm.sagepub.com'},
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
    'Environ Entomol': {'host': 'ee.oxfordjournals.org'},
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
    'J Bone Joint Surg Am': {'host': 'jbjs.org'},
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
    'Radiat Res': {'host': 'jrr.oxfordjournals.org'},
    'Rheumatology (Oxford)': {'host': 'rheumatology.oxfordjournals.org'},
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
