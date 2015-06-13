# -*- coding: utf-8 -*-

from __future__ import print_function

import os, sys, shutil
import logging

from metapub import PubMedFetcher, CrossRef 
from metapub.exceptions import MetaPubError

####
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)
####

fetch = PubMedFetcher()

if __name__=='__main__':
    try:
        doi = sys.argv[1]
    except IndexError:
        print('Supply doi (or other search string) as the argument to this script.')
        sys.exit()

    CR = CrossRef()
    results = CR.query(doi, params={})
    top_result = results[0]
    pmids = fetch.pmids_for_citation(**top_result['slugs'])
    print(top_result['slugs'])
    print(pmids)
    

