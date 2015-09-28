from __future__ import print_function

from metapub import PubMedFetcher

fetch = PubMedFetcher()
pmbook = fetch.article_by_pmid('20301577')


print(pmbook.title)
print(pmbook.abstract)
print(pmbook.year)

