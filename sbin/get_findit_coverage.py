from __future__ import absolute_import, print_function, unicode_literals

from metapub import FindIt, PubMedFetcher

from metapub.findit.dances import the_doi_2step

from config import JOURNAL_ISOABBR_LIST_FILENAME, FINDIT_COVERAGE_CSV

fetch = PubMedFetcher()

outfile = open(FINDIT_COVERAGE_CSV, 'w')

# template for CSV output
CSV_OUTPUT_TEMPLATE = '{source.pma.journal},{source.pma.year},{source.pma.pmid},{url},{source.reason}\n'


# for each journal listed in JOURNAL_ISOABBR_LIST_FILENAME,
# do a pubmed advanced query to retrieve at least 3 pubmed 
# articles spread across a fairly wide range of years.
# 
# (Some journals will not have issues within intended years;
#  in these cases, pubmed queries will return articles with
#  closest dates to intended years, which is fine.)
#
# Example:
#   for the journal with "Acta Cytol" as its ISOAbbr, 
#   the following years are valid results to produce articles:
#
#   Year    Advanced Query Syntax   Sample PMID
#
#   2010    "Acta Cytol" 2010[DP]   21428157
#   2005    "Acta Cytol" 2005[DP] 
#   1990    "Acta Cytol" 1990[DP]
#
#
# Using this list, create a FindIt source object for each article.
# 
# For each source object, write results to the CSV with heuristics:
#
#   If source.reason.startswith('NOFORMAT'), assign url=source.backup_url
#

def get_sample_pmids_for_journal(jrnl, years=None, max_pmids=3):
    samples = []
    if years is None:
        pmids = fetch.pmids_for_query(journal=jrnl)
        idx = 0
        while idx < len(pmids) and idx <= max_pmids:
            samples.append(pmids[idx])
            idx += 1
    else:
        for year in years:
            pmids = fetch.pmids_for_query(journal=jrnl, year=year)
            if len(pmids) < 1:
                continue
            samples.append(pmids[0])
    return samples

def write_findit_result_to_csv(source):
    url = source.url
    if source.reason and source.reason.startswith(('NOFORMAT', 'TODO')):
        if source.doi:
            try:
                url = the_doi_2step(source.doi)
            except Exception as err:
                url = 'http://dx.doi.org/%s' % source.doi
        else:
            url = '(no doi)'
    outfile.write(CSV_OUTPUT_TEMPLATE.format(source=source, url=url))
    outfile.flush()

def main():
    jrnls = open(JOURNAL_ISOABBR_LIST_FILENAME).read()
    #start_index = jrnls.find('Anat. Embryol.')
    start_index = 0

    for jrnl in jrnls[start_index:].split('\n'):
        jrnl = jrnl.strip()
        if jrnl == '':
            continue

        pmids = get_sample_pmids_for_journal(jrnl, years=['1975', '1980', '1990', '2002', '2013'])
        if pmids == []:
            pmids = get_sample_pmids_for_journal(jrnl)

        print('[%s] Sample pmids: %r' % (jrnl, pmids))
        for pmid in pmids:
            source = FindIt(pmid)
            print('[{source.pma.journal}]\t{source.pmid}: {source.url} ({source.reason})'.format(source=source))
            write_findit_result_to_csv(source)

if __name__ == '__main__':
    main()

