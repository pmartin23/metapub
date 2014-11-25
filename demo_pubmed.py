from metapub import PubMedFetcher

fetch = PubMedFetcher()

article = fetch.article_by_pmid('20532249')
print article.pmid
print article.title

