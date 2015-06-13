import os, sys, logging, shutil, subprocess
import requests

from requests.packages import urllib3 
urllib3.disable_warnings()

from metapub import PubMedFetcher 
from metapub.exceptions import MetaPubError
from metapub import FindIt
from metapub.text_mining import pick_pmid
from metapub.utils import asciify

# produce a report at the end
import pandas

CURL_TIMEOUT = 2000

####
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.WARNING)
####


def get_filename(base_fpath):
    def check_and_bump(x):
        if os.path.exists('%s.%i' % (base_fpath, x)):
            return check_and_bump(x+1)
        else:
            return '%s.%i' % (base_fpath, x)
    return check_and_bump(0)

def requests_write_file(url, filename):
    # skip currently problematic URLs
    if url.find('jcem.endojournals.org') > -1:
        return 'tx_error'

    # verify=False means it ignores bad SSL certs
    response = requests.get(url, stream=True, timeout=CURL_TIMEOUT, verify=False)

    if not response.ok:
        return 'tx_error'

    if response.status_code == 200:
        if response.headers.get('content-type').find('pdf') > -1:
            with open(filename, 'wb') as handle:
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
        return response.headers.get('content-type')
    else:
        return response.status_code


basedir = 'findit'

try:
    pmid_file = sys.argv[1]
except IndexError:
    print 'Supply filename of pmid list as the argument to this script.'
    sys.exit()

try:
    outdir = sys.argv[2]
except IndexError:
    outdir = os.path.join(basedir, pmid_file)

try:
    os.makedirs(outdir)
except OSError:
    pass

fetch = PubMedFetcher()
pmids = open(pmid_file, 'r').readlines()

# condition will be one of "tx_error", "timeout", "invalid", "HTML", or "PDF"
findit = { 'journal': [], 'pmid': [], 'url': [], 'condition': [], 'filename': [] } 

tx_errors = 0
timeouts = 0
invalids = []

for pmid in [pick_pmid(pmid) for pmid in pmids if pmid.strip() != '']:
    findit['pmid'].append(pmid)

    try:
        source = FindIt(pmid=pmid)
    except MetaPubError, e:
        print e
        print "%s: no PubMedArticle" % pmid
        findit['condition'].append('invalid')
        findit['url'].append('NA')
        findit['filename'].append('NA')
        findit['journal'].append('NA')
        continue
    
    #print pmid, 'Grant info (if any): '
    #print source.pma.grants

    if source.pma is None:
        print "%s: no PubMedArticle" % pmid
        findit['condition'].append('invalid')
        findit['url'].append('NA')
        findit['filename'].append('NA')
        findit['journal'].append('NA')
        continue

    findit['journal'].append(asciify(source.pma.journal))

    if source.url is None:
        print '%s: %s -- no URL because %s' % (pmid, source.pma.journal, source.reason) #, source.pma.journal)
        findit['url'].append('NA')
        findit['filename'].append('NA')
        findit['condition'].append('%s' % source.reason)
        continue

    filename = os.path.join(outdir, pmid + '.pdf')

    findit['filename'].append(filename)
    findit['url'].append(source.url)
    
    print '%s: %s (%s)' % (pmid, source.pma.journal, source.url)

    if os.path.exists(filename):
        findit['condition'].append('application/pdf')
        print '%s: already have %s (skipping)' % (pmid, filename)
        continue
    print '%s: downloading %s' % (source.pmid, source.url)
    result = None
    try:
        result = requests_write_file(source.url, filename)
    except Exception, e:
        print "oh noes! %s" % e
        if ('%s' % e).find('timed') > -1:
            findit['condition'].append('timeout')
        #else:
        #    findit['condition'].append('error')
    findit['condition'].append('%s' % result)
    print '%s: %s' % (pmid, result)

f=open('invalid_pmids_FindIt.txt', 'w')
f.write('\n'.join(invalids))
f.close()

df = pandas.DataFrame(findit)
#print df.head()

csvfilename = get_filename(os.path.join(basedir, (pmid_file+'.csv')))

open(csvfilename, 'w').write(df.to_csv())

num_pdfs = len([item for item in findit['condition'] if item=='application/pdf'])
num_html = len([item for item in findit['condition'] if item.find('text/html') > -1])
num_noformat = len([item for item in findit['condition'] if item.find('No URL format')==0])
num_txerror = len([item for item in findit['condition'] if item.find('error') > -1])

print "Finished with", pmid_file 
print ""
print "Results!"
print "========"
print "Total PMIDs attempted: %i" % len(pmids)
print "Total PDFs downloaded: %i" % num_pdfs
print ""
print "No formats: %i" % num_noformat
print "Errors of all kinds: %i" % num_txerror
print "... success rate: %f" % (float(num_pdfs) / float(len(pmids)))
print ""
print "See details in %s" % csvfilename
print "========"
print ""

