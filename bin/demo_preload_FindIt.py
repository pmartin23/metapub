from __future__ import absolute_import, print_function, unicode_literals

import os, sys, re, logging

from metapub import FindIt

logging.getLogger('eutils').setLevel(logging.INFO)

try:
    filename = sys.argv[1]
except:
    print("supply filename of PMID list as argument to this script")
    sys.exit()

re_pmid = re.compile('^\d+$')
def validate_pmid(pmid):
    pmid = pmid.strip()
    if re_pmid.findall(pmid):
        return True
    else:
        return False

pmids = list(set(open(filename, 'r').readlines()))

for pmid in [item.strip() for item in pmids if validate_pmid(item)]:
    print(pmid)
    try:
        src = FindIt(pmid=pmid, debug=True)
        print(pmid, src.doi, src.pma.title)
        if src.url:
            print(src.url)
        else:
            print(src.reason)
    except Exception as error:
        print(error)

    print()


