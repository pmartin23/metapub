# -*- coding: utf-8 -*-

from __future__ import print_function

import os, sys, shutil
import logging

from metapub import PubMedFetcher, CrossRef 
from metapub.exceptions import MetaPubError
from metapub.text_mining import find_doi_in_string

DEBUG = True

####
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)
####

fetch = PubMedFetcher()
CR = CrossRef()

def get_doi(pmid):
    pma = fetch.article_by_pmid(pmid)
    if DEBUG:
        print("looking up %s (title: %s, journal: %s)" % (pmid, pma.title, pma.journal))
    if pma.doi:
        if DEBUG:
            print("Found it in Medline XML")
        return pma.doi

    results = CR.query_from_PubMedArticle(pma)
    top_result = CR.get_top_result(results, min_score=2.5)     #, CR.last_params, use_best_guess=True)
    #if DEBUG:
    #    print(results)
    if top_result is None:
        if DEBUG:
            print("CrossRef had no good results for query with search=%s and params=%r" % (pma.title, CR.last_params))
        return "N/A"

    if DEBUG:
        print("CrossRef found it with score=%f" % top_result['score'])
    return top_result['doi']


if __name__=='__main__':
    try:
        pmid = sys.argv[1]
    except IndexError:
        print('Supply a PubMed ID as the argument to this script.')
        sys.exit()

    doi = get_doi(pmid)
    print("DOI: %s" % doi)
    print("")

    result = find_doi_in_string(doi)
    print(result)
    

