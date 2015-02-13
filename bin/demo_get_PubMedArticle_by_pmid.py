import sys

from metapub import PubMedFetcher

# examples of different formats:
# 18612690: PubMedArticle with multiple AbstractText sections
# 1234567:  PubMedArticle with no abstract whatsoever
# 20301546: PubMedBookArticle from GeneReviews

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
#print 'pages: '+article.pages
print 'authors: %s' % ','.join(article.authors)
print 'abstract: %s' % article.abstract
if article.pii:
    print 'pii: '+article.pii
if article.doi:
    print 'doi: '+article.doi

#print article.xmlstr

