from __future__ import absolute_import, print_function, unicode_literals

from metapub import FindIt, PubMedFetcher

from metapub.findit.dances import the_doi_2step

from config import JOURNAL_ISOABBR_LIST_FILENAME, FINDIT_COVERAGE_CSV

fetch = PubMedFetcher()

def get_sample_pmids_for_journal(jrnl, years=None, max_pmids=3):
    samples = []
    if years is None:
        pmids = fetch.pmids_for_query(journal=jrnl)
        idx = 0
        while idx < len(pmids) and idx < max_pmids:
            samples.append(pmids[idx])
            idx += 1
    else:
        for year in years:
            pmids = fetch.pmids_for_query(journal=jrnl, year=year)
            if len(pmids) < 1:
                continue
            samples.append(pmids[0])
    return samples

def main(start_journal=None):
    jrnls = open(JOURNAL_ISOABBR_LIST_FILENAME).read()

    if start_journal:
        start_index = jrnls.find(start_journal)
    else:
        start_index = 0

    for jrnl in jrnls[start_index:].split('\n'):
        jrnl = jrnl.strip()
        if jrnl == '':
            continue

        years = ['1975', '1980', '1990', '2002', '2013']
        num_desired = len(years)
        pmids = get_sample_pmids_for_journal(jrnl, years=years)
        if len(pmids) < num_desired:
            pmids = pmids + get_sample_pmids_for_journal(jrnl, max_pmids=num_desired-len(pmids))

        print('[%s] Sample pmids: %r' % (jrnl, pmids))
        for pmid in pmids:
            try:
                pma = fetch.article_by_pmid(pmid)
                print('    %s: %s' % (pmid, pma.title))
            except Exception as err:
                print('    %s: ERROR - %r' % (pmid, err))

if __name__ == '__main__':
    main()

