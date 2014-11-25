import sys

from metapub import PubMedFetcher

####
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.WARNING)
####

try:
    pmid = sys.argv[1]
except IndexError:
    print "Supply a pubmed ID as the argument to this script."
    print ""
    print "Example: python demo_pubmed.py 123456"
    sys.exit()

fetch = PubMedFetcher()

article = fetch.article_by_pmid(pmid)
print article.pmid, article.title
print ','.join(article.authors)

