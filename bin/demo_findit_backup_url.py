import os
import requests

from metapub.findit import FindIt
from metapub.exceptions import *

OUTPUT_DIR = 'findit'
CURL_TIMEOUT = 4000

def try_request(url):
    # verify=False means it ignores bad SSL certs
    OK_STATUS_CODES = [200, 301, 302, 307]
    response = requests.get(url, stream=True, timeout=CURL_TIMEOUT, verify=False)

    if response.status_code in OK_STATUS_CODES:
        if response.headers.get('content-type').find('pdf') > -1:
            return True
    return False

def try_backup_url(pmid):
    source = FindIt(pmid=pmid)
    if source.url:
        print pmid, source.pma.journal, source.url
    else:
        print pmid, source.pma.journal, source.reason
        try:
            print pmid, source.pma.journal, source.backup_url, try_request(source.backup_url)
        except Exception, e:
            print pmid, '%r' % e

if __name__=='__main__':
    import sys
    try:
        start_pmid = int(sys.argv[1])
    except IndexError, TypeError:
        print "Supply a pubmed ID as the starting point for this script."
        sys.exit()

    for pmid in range(start_pmid, start_pmid+1000):
        try_backup_url(pmid)


