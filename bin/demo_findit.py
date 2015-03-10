from metapub.findit import FindIt

JAMA_pmids = ['25742465', '23754022', '25739104']

#for pmid in JAMA_pmids:
#    source = FindIt(pmid=pmid)
#    filename = '%s.pdf' % pmid
#    print source.url

SD_pmids = [
            '25735572', 
            '25543539', 
            '25666562', 
            '24565554', 
            '10545037',
            '16644204',
            '15878741',     #Biochim Biophys Acta / http://www.sciencedirect.com/science/article/pii/S0925443905000177
            ]
for pmid in SD_pmids:
    source = FindIt(pmid=pmid)
    filename = '%s.pdf' % pmid
    print source.url

