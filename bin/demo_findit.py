from metapub.findit import FindIt

JAMA_pmids = ['25742465', '23754022', '25739104']

for pmid in JAMA_pmids:
    source = FindIt(pmid=pmid)
    filename = '%s.pdf' % pmid
    print source.url

