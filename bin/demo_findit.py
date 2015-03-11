from metapub.findit import FindIt

JAMA_pmids = ['25742465', '23754022', '25739104']

PMC_pmids = ['25717385',     # Lancet Psychiatry
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
            ]

def print_urls_and_reasons_from_pmid_list(pmids):
    for pmid in pmids:
        source = FindIt(pmid=pmid)
        if source.url:
            print pmid, source.url
        else:
            print pmid, source.reason

print "PMC (or should be):"
print_urls_and_reasons_from_pmid_list(PMC_pmids)

print ""
print "ScienceDirect:"
print_urls_and_reasons_from_pmid_list(SD_pmids)

print ""
print "JAMA:"
print_urls_and_reasons_from_pmid_list(JAMA_pmids)

print ""
print "Lancet:"
print_urls_and_reasons_from_pmid_list(Lancet_pmids)

