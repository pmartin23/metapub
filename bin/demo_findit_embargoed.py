from metapub.findit import FindIt

pmids = [ '25575644' ]

def print_urls_and_reasons_from_pmid_list(pmids):
    for pmid in pmids:
        source = FindIt(pmid=pmid)
        if source.url:
            print "Got: ", pmid, source.url, source.pma.journal
        else:
            print "Nope: ", pmid, source.reason, source.pma.journal
            print "Backup URL: ", pmid, source.backup_url

for pmid in pmids:
    source = FindIt(pmid=pmid)
    print source.pma.pmc
    from IPython import embed; embed()

