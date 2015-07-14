# -*- coding: utf-8 -*-

from __future__ import print_function

import os, sys, shutil
import logging

from metapub import FindIt

#DEBUG = True

####
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)
####

if __name__=='__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        print('Supply a filename containing a list of PMIDs as argument to this script.')
        sys.exit()

    pmids = open(filename, 'r').readlines()
    for pmid in [item.strip() for item in pmids if item.strip() != '']:
        try:
            src = FindIt(pmid, retry_errors=True)
        except Exception as error:
            print(error)
            continue

        print(pmid, src.doi, src.pma.title)
        if src.url:
            print("     url: ", src.url)
        else:
            print("     reason: ", src.reason)

