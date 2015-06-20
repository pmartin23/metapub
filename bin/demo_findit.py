from metapub.findit import FindIt

vip_pmids = ['1255861',     # J Virol
            ]

jstage_pmids = ['11446670'] 

wiley_pmids = ['14981756']

biochemsoc_pmids = ['11776', '25896238', '11980567']

JAMA_pmids = ['25742465', '23754022', '25739104']

JCI_pmids = ['26011642', '25985270', '26030226']

BMC_pmids = ['25943194',     # BMC Genet
             '20170543',     # BMC Cancer
             '25927199',     # BMC Bioinformatics
             '25935646',     # BMC Genet
             '25929254',     # BMC Med Genet
             '25954321',     # Genome Med
             '25958000',     # Hum Genomics
             '25937888',     # J Clin Bioinfoma
             '25968637',     # J Transl Med
            ]

PMC_pmids = ['25717385',     # Lancet Psychiatry
             '17534376',     # Eur J Hum Genet
        ]  

Lancet_pmids = ['25529582',     # marked Free Article
                '25483163',     # not marked Free
                '25456370',     #Lancet Oncol, not marked Free
               ]

SD_pmids = [
            '25735572', 
            '25543539', 
            '25666562', 
            '24565554', 
            '10545037',
            '16644204',
            '15878741',     #Biochim Biophys Acta / http://www.sciencedirect.com/science/article/pii/S0925443905000177
            '23246278',     #Molecular Genetics and Metabolism
            '206004',       #Virology
            ]

def print_urls_and_reasons_from_pmid_list(pmids):
    for pmid in pmids:
        source = FindIt(pmid=pmid)
        if source.url:
            print "Got: ", pmid, source.url, source.pma.journal
        else:
            print "Nope: ", pmid, source.reason, source.pma.journal
            print "Backup URL: ", pmid, source.backup_url

print ""
print "vip journals:"
print_urls_and_reasons_from_pmid_list(vip_pmids)

print ""
print "PMC (or should be):"
print_urls_and_reasons_from_pmid_list(PMC_pmids)

print ""
print "Biochemical Society:"
print_urls_and_reasons_from_pmid_list(biochemsoc_pmids)

print ""
print "Wiley E. Publisher:"
print_urls_and_reasons_from_pmid_list(wiley_pmids)

print ""
print "jstage:"
print_urls_and_reasons_from_pmid_list(jstage_pmids)

print ""
print "J Clin Invest (JCI):"
print_urls_and_reasons_from_pmid_list(JCI_pmids)

print ""
print "BMC journals:"
print_urls_and_reasons_from_pmid_list(BMC_pmids)

print ""
print "ScienceDirect:"
print_urls_and_reasons_from_pmid_list(SD_pmids)

print ""
print "JAMA:"
print_urls_and_reasons_from_pmid_list(JAMA_pmids)

print ""
print "Lancet:"
print_urls_and_reasons_from_pmid_list(Lancet_pmids)

