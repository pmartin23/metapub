from __future__ import absolute_import, print_function, unicode_literals

from metapub import FindIt, PubMedFetcher

from config import JOURNAL_ISOABBR_LIST_FILENAME, FINDIT_COVERAGE_CSV

fetch = PubMedFetcher()

outfile = open(FINDIT_COVERAGE_CSV, 'w')

# template for CSV output
CSV_OUTPUT_TEMPLATE = '{source.pma.jrnl},{source.pma.year},{source.pma.pmid},{url},{source.reason}\n'


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

def get_sample_pmids_for_journal(jrnl):
    years = ['2010', '2005', '1990']
    samples = []
    for year in years:
        pmids = fetch.pmids_for_query(jrnl, year=year)
        if len(pmids) < 1:
            continue
        samples.append(pmids[0])
    return samples

def write_findit_result_to_csv(source):
    url = source.url
    if source.reason.startswith('NOFORMAT') or source.reason.startswith('TODO'):
        url = source.backup_url
    outfile.write(CSV_OUTPUT_TEMPLATE.format(source=source, url=url))
    outfile.flush()

def main():
    jrnls = open(JOURNAL_ISOABBR_LIST_FILENAME).readlines()
    for jrnl in jrnls:
        jrnl = jrnl.strip()
        if jrnl == '':
            continue

        pmids = get_sample_pmids_for_journal(jrnl)
        print('[%s] Sample pmids: %r' % (jrnl, pmids))
        for pmid in pmids:
            source = FindIt(pmid)
            print('[{source.pma.journal]\t{source.pmid}: {source.url} ({source.reason})'.format(source=source))
            write_findit_result_to_csv(source)

if __name__ == '__main__':
    main()

