from __future__ import print_function

from metapub.findit import FindIt

SAMPLE_PMIDS = { 'embargoed': [ '25575644', '25700512', '25554792', '25146281', '25766237' ],
                 'nonembargoed': ['26098888',],
                 'non_pmc': ['26111251', '17373727']
               }

def print_url_and_reasons_from_pmid_list(pmids, listname='LIST'):
    print(listname)
    for pmid in pmids:
        source = FindIt(pmid=pmid)
        print('PMC id:', source.pma.pmc)

        embdate = source.pma.history.get('pmc-release', None)

        print('Embargo date: %r' % embdate)
        if source.url:
            print("Got: ", pmid, source.url, source.pma.journal)
        else:
            print("Nope: ", pmid, source.reason, source.pma.journal)
            print("Backup URL: ", pmid, source.backup_url)

for listname in SAMPLE_PMIDS.keys():
    print_url_and_reasons_from_pmid_list(SAMPLE_PMIDS[listname], listname)

