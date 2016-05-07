from __future__ import absolute_import, unicode_literals

HOSTNAME_TO_JOURNAL_MAP = {
		'rheumatology.oxfordjournals.org': 'Rheumatology (Oxford)',
		'bjo.bmj.com': 'BMC Ophthalmol',
		'spcare.bmj.com': 'BMJ Support Palliat Care',
		'molbiolcell.org': 'Mol Biol Cell',
		'jech.bmj.com': 'J Epidemiol Community Health',
		'bja.oxfordjournals.org': 'Br J Anaesth',
		'heartasia.bmj.com': 'Heart Asia',
		'jmg.bmj.com': 'J Med Genet',
		'jisakos.bmj.com': 'J ISAKOS',
		'stroke.ahajournals.org': 'Stroke',
		'pmj.bmj.com': 'Postgrad Med J',
		'jah.sagepub.com': 'J Aging Health',
		'molpharm.aspetjournals.org': 'Mol Pharmacol',
		'jasn.asnjournals.org': 'J Am Soc Nephrol',
		'biomedgerontology.oxfordjournals.org': 'J Gerontol A Biol Sci Med Sci',
		'sti.bmj.com': 'Sex Transm Infect',
		'jbc.org': 'J Biol Chem',
		'jrr.oxfordjournals.org': 'Radiat Res',
		'care.diabetesjournals.org': 'Diabetes Care',
		'cid.oxfordjournals.org': 'Clin Infect Dis',
		'circep.ahajournals.org': 'Circ Arrhythm Electrophysiol',
		'drc.bmj.com': 'BMJ Open Diabetes Res Care',
		'dmd.aspetjournals.org': 'Drug Metab Dispos',
		'cancerdiscovery.aacrjournals.org': 'Cancer Discov',
		'ard.bmj.com': 'Ann Rheum Dis',
		'jnci.oxfordjournals.org': 'J Natl Cancer Inst',
		'aac.asm.org': 'Antimicrob Agents Chemother',
		'pn.bmj.com': 'Pract Neurol',
		'peds.oxfordjournals.org': 'Protein Eng Des Sel',
		'eje-online.org': 'Eur J Endocrinol',
		'ebn.bmj.com': 'Evid Based Nurs',
		'cfp.ca': 'Can Fam Physician',
		'ar.iiarjournals.org': 'Anticancer Res',
		'inpractice.bmj.com': 'In Pract',
		'dtb.bmj.com': 'Drug Ther Bull',
		'clincancerres.aacrjournals.org': 'Clin Cancer Res',
		'jvi.asm.org': 'J Virol',
		'fg.bmj.com': 'Frontline Gastroenterol',
		'qjmed.oxfordjournals.org': 'QJM',
		'bmjopenrespres.bmj.com': 'BMJ Open Resp Res',
		'diabetes.diabetesjournals.org': 'Diabetes',
		'jramc.bmj.com': 'J R Army Med Corps',
		'innovations.bmj.com': 'BMJ Innov',
		'jme.bmj.com': 'J Med Ethics',
		'openheart.bmj.com': 'Open Heart',
		'circ.ahajournals.org': 'Circulation',
		'pediatrics.aappublications.org': 'Pediatrics',
		'adc.bmj.com': 'Arch Dis Child',
		'carcin.oxfordjournals.org': 'Carcinogenesis',
		'atvb.ahajournals.org': 'Arterioscler Thromb Vasc Biol',
		'genomebiology.com': 'Genome Biol',
		'jlr.org': 'J Lipid Res',
		'erc.endocrinology-journals.org': 'Endocr Relat Cancer',
		'pcp.oxfordjournals.org': 'Plant Cell Physiol',
		'jimmunol.org': 'J Immunol',
		'jrheum.org': 'J Rheumatol',
		'gut.bmj.com': 'Gut',
		'fn.bmj.com': 'Arch Dis Child Fetal Neonatal Ed',
		'mct.aacrjournals.org': 'Mol Canc Therapeut',
		'cpj.sagepub.com': 'Clin Pediatr',
		'humrep.oxfordjournals.org': 'Hum Reprod',
		'jac.oxfordjournals.org': 'J Antimicrob Chemother',
		'circres.ahajournals.org': 'Circ Res',
		'jhl.sagepub.com': 'J Hum Lact',
		'peds.oxfordjournals.org': 'Protein Eng',
		'emj.bmj.com': 'Emerg Med J',
		'vetrecordopen.bmj.com': 'Vet Rec Open',
		'ajcp.ascpjournals.org': 'Am J Clin Pathol',
		'jbjs.org': 'J Bone Joint Surg Am',
		'ejhp.bmj.com': 'Eur J Hosp Pharm',
		'neurology.org': 'Neurology',
		'jid.oxfordjournals.org': 'J Infect Dis',
		'ee.oxfordjournals.org': 'Environ Entomol',
		'jcs.biologists.org': 'J Cell Sci',
		'nar.oxfordjournals.org': 'Nucleic Acids Res',
		'ang.sagepub.com': 'Angiology',
		'cancerres.aacrjournals.org': 'Cancer Res',
		'jcn.sagepub.com': 'J Child Neurol',
		'thorax.bmj.com': 'Thorax',
		'pnas.org': 'Proc Natl Acad Sci USA',
		'ajplung.physiology.org': 'Am J Physiol Lung Cell Mol Physiol',
		'jdr.sagepub.com': 'J Dent Res',
		'bmjopen.bmj.com': 'BMJ Open',
		'sciencemag.org': 'Science',
		'iovs.org': 'Invest Ophthalmol Vis Sci',
		'annonc.oxfordjournals.org': 'Ann Oncol',
		'oem.bmj.com': 'Occup Environ Med',
		'qualitysafety.bmj.com': 'BMJ Qual Saf',
		'heart.bmj.com': 'Heart',
		'jn.nutrition.org': 'J Nutr',
		'mcb.asm.org': 'Mol Cell Biol',
		'asm.sagepub.com': 'Assessment',
		'stel.bmj.com': 'BMJ STEL',
		'jpet.aspetjournals.org': 'J Pharmacol Exp Ther',
		'qir.bmj.com': 'BMJ Qual Improv Report',
		'iovs.org': 'IOVS',
		'clinchem.org': 'Clin Chem',
		'ebm.bmj.com': 'Evid Based Med',
		'mct.aacrjournals.org': 'Mol Cancer Ther',
		'breast-cancer-research.com': 'Breast Cancer Res',
		'circgenetics.ahajournals.org': 'Circ Cardiovasc Genet',
		'eurheartj.oxfordjournals.org': 'Eur Heart J',
		'genome.cshlp.org': 'Genome Res',
		'jb.asm.org': 'J Bacteriol',
		'bmjopensem.bmj.com': 'BMJ Open Sport Exerc Med',
		'physiolgenomics.physiology.org': 'Physiol Genomics',
		'plantcell.org': 'Plant Cell',
		'jnis.bmj.com': 'J Neurointerv Surg',
		'jcb.rupress.org': 'J Cell Biol',
		'molehr.oxfordjournals.org': 'Mol Hum Reprod',
		'lup.sagepub.com': 'Lupus',
		'lupus.bmj.com': 'Lupus Sci Med',
		'jfprhc.bmj.com': 'J Fam Plann Reprod Health Care',
		'hmg.oxfordjournals.org': 'Hum Mol Genet',
		'mutage.oxfordjournals.org': 'Mutagenesis',
		'erj.ersjournals.com': 'Eur Respir J',
		'jnnp.bmj.com': 'J Neurol Neurosurg Psychiatry',
		'tobaccocontrol.bmj.com': 'Tob Control',
		'haematologica.org': 'Haematologica',
		'mh.bmj.com': 'Med Humanities',
		'injuryprevention.bmj.com': 'Inj Prev',
		'cat.sagepub.com': 'Clin Appl Thromb Hemost',
		'jcp.bmj.com': 'J Clin Pathol',
		'ojrd.com': 'Orphanet J Rare Dis',
		'veterinaryrecord.bmj.com': 'Vet Rec',
		'femsle.oxfordjournals.org': 'FEMS Microbiol Lett',
		'genesdev.cshlp.org': 'Genes Dev',
		'jem.rupress.org': 'J Exp Med',
		'jneurosci.org': 'J Neurosci',
		'rmdopen.bmj.com': 'RMD Open',
		'vetrecordcasereports.bmj.com': 'Vet Rec Case Rep',
		'jim.bmj.com': 'J Investig Med',
		'fasebj.org': 'FASEB J',
		'aim.bmj.com': 'Acupunct Med',
		'ajh.oxfordjournals.org': 'Am J Hypertens',
		'acb.sagepub.com': 'Ann Clin Biochem',
		'jco.ascopubs.org': 'J Clin Oncol',
		'bjsm.bmj.com': 'Br J Sports Med',
		'cardiovascres.oxfordjournals.org': 'Cardiovasc Res',
		'ndt.oxfordjournals.org': 'Nephrol Dial Transplant',
		'brain.oxfordjournals.org': 'Brain',
		'cpj.sagepub.com': 'Clin Pediatr (Phila)',
		'jcem.endojournals.org': 'J Clin Endocrinol Metab',
		'hyper.ahajournals.org': 'Hypertension',
		'ep.bmj.com': 'Arch Dis Child Educ Pract Ed',
		'ebmh.bmj.com': 'Evid Based Mental Health',
		'emboj.embopress.org': 'EMBO J',
		'cebp.aacrjournals.org': 'Cancer Epidemiol Biomarkers Prev',
		'eolj.bmj.com': 'End Life J',
		'esmoopen.bmj.com': 'ESMO Open',
		'jme.endocrinology-journals.org': 'J Mol Endocrinol',
		'jra.sagepub.com': 'J Renin Angiotensin Aldosterone Syst',
		'ajpcell.physiology.org': 'Am J Physiol, Cell Physiol',
		'joe.endocrinology-journals.org': 'J Endocrinol',
		'bmj.com': 'BMJ',
		'bloodjournal.org': 'Blood',
		'jmd.amjpathol.org': 'J Mol Diagn',
		'heartrhythmjournal.com': 'Heart Rhythm',
		'ajconline.org': 'Am J Cardiol',
		'cancergeneticsjournal.org': 'Cancer Genet Cytogenet',
		'epires-journal.com': 'Epilepsy Res',
		'amjmed.com': 'Am J Med',
		'nmd-journal.com': 'Neuromuscul Disord',
		'arcmedres.com': 'Arch Med Res',
		'jpeds.com': 'J Pediatr',
		'clineu-journal.com': 'Clin Neurol Neurosurg',
		'ijporlonline.com': 'Int J Pediatr Otorhinolaryngol',
		'mgmjournal.com': 'Mol Genet Metab',
		'ahjonline.com': 'Am Heart J',
		'cancerci.com': 'Cancer Cell Int',
		'internationaljournalofcardiology.com': 'Int J Cardiol',
		'akademiai.com': 'Orv Hetil',
		'placentajournal.org': 'Placenta',
		'prd-journal.com': 'Parkinsonism Relat Disord',
		'pedneur.com': 'Pediatr Neurol',
		'cancerletters.info': 'Cancer Lett',
		'neurobiologyofaging.org': 'Neurobiol Aging',
		'metabolismjournal.com': 'Metabolism',
		'thebonejournal.com': 'Bone',
		'thrombosisresearch.com': 'Thromb Res',
		'brainanddevelopment.com': 'Brain Dev',
		'jpurol.com': 'J Pediatr Urol',
		'metabolismjournal.com': 'Metab Clin Exp',
		'worldneurosurgery.org': 'Surg Neurol',
		'jmmc-online.com': 'J Mol Cell Cardiol',
		'gastrojournal.org': 'Gastroenterology',
		'exphem.org': 'Exp Hematol',
		'medical-hypotheses.com': 'Med Hypotheses',
		'atherosclerosis-journal.com': 'Atherosclerosis',
		'gynecologiconcology-online.net': 'Gynecol Oncol',
		'aaojournal.org': 'Ophthalmology',
		'biologicalpsychiatryjournal.com': 'Biol Psychiatry',
		'ejpn-journal.com': 'Eur J Paediatr Neurol',
		'jdsjournal.com': 'J Dermatol',
		'ajo.com': 'Am J Ophthalmol',
		'fertstert.org': 'Fertil Steril',
		'jns-journal.com': 'J Neurol Sci',
		'diabetesresearchclinicalpractice.com': 'Diabetes Res Clin Pract',
		'clinsci.org': 'Clin Sci',
		'biochemj.org': 'Biochem J',
		'sciencemag.org': 'Science',
		'stm.sciencemag.org': 'Sci Transl Med',
		'advances.sciencemag.org': 'Sci Adv',
		'stke.sciencemag.org': 'Sci Signal',
		'joponline.org': 'J Periodontol',
		'medicinabuenosaires.com': 'Medicina (B Aires)',
}
