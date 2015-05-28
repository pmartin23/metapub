from __future__ import print_function

from metapub import PubMedFetcher
fetch = PubMedFetcher()

term = 'Global developmental delay'

print('%s: etiology broad' % term)
results = fetch.pmids_for_clinical_query(term, 'etiology', debug=True, year=2013)

print('First three results:')
print(results[:3])

print('')

print('%s: etiology narrow' % term)

results = fetch.pmids_for_clinical_query(term, 'etiology', 'narrow', debug=True, year=2013)
print('First three results:')
print(results[:3])
print('')

