# -*- coding: utf-8 -*-

from __future__ import print_function

import os, sys, shutil
import logging, time

from requests.exceptions import ConnectionError

from metapub import PubMedFetcher, CrossRef 
from metapub.exceptions import XMLSyntaxError, MetaPubError
from metapub.text_mining import find_doi_in_string
from metapub.config import get_data_log
from metapub.pubmedcentral import get_pmcid_for_otherid
from metapub.utils import asciify

# configurables (edit as you like):
RESULTS_DIR = 'sandbox/results/'
DEBUG = False
CONNECTION_ERROR_LIMIT = 10

# non-configurables (don't touch):
error_log = None
data_log = None
CONNECTION_ERRORS = 0

# process_log: logs processing messages to stdout
process_log = logging.getLogger('pmid2doi')
ch = logging.StreamHandler()
if DEBUG:
    ch.setLevel(logging.DEBUG)
else:
    ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
process_log.addHandler(ch)
process_log.addHandler(ch)


def get_filename(base_fpath):
    def check_and_bump(x):
        if os.path.exists('%s.%i' % (base_fpath, x)):
            return check_and_bump(x+1)
        else:
            return '%s.%i' % (base_fpath, x)
    return check_and_bump(0)

def open_logs(run_span):
    global error_log
    global data_log
    fname_base = '%s.%s.log'
    errorlog_path = get_filename(os.path.join(RESULTS_DIR, fname_base % (run_span, 'error')))
    mapping_path = get_filename(os.path.join(RESULTS_DIR, fname_base % (run_span, 'mapping')))
    error_log = get_data_log(errorlog_path, 'pmid2doi.error')
    data_log = get_data_log(mapping_path, 'pmid2doi.mapping')
 

fetch = PubMedFetcher()
crossref = CrossRef()

def record_error(pmid, source, e):
    error_log.info('%s, %s, %r' % (pmid, source, e))

def record_entry(**kwargs):
    #{'doi': 'NA', 'score': 0, 'cr_results': [], 'connection_errors': 0, 'pma': None, 'cr_top_result': None, 'pmid': 1234567}
    fmt = '{pmid},{doi},{score},{pubmed_type}'   #,{crossref_query},{crossref_coins}'
    data_log.info(fmt.format(**kwargs))


def handle_connection_error(debug_msg=''):
    global CONNECTION_ERRORS
    CONNECTION_ERRORS += 1
    if CONNECTION_ERRORS > CONNECTION_ERROR_LIMIT:
        if debug_msg:
            process_log.debug(debug_msg)
        process_log.info('Too many connection errors (%i); quitting!' % CONNECTION_ERRORS)
        sys.exit()


class PMIDMapping(object):
    '''represents a mapping of a single pubmed ID (pmid) to as many IDs as 
        can be mapped to it.'''

    # number of times to retry getting XML from pubmed
    PMA_RETRY_LIMIT = 3

    def __init__(self, pmid):
        self.connection_errors = 0

        # set sensible defaults intended for display in records.
        self.pmid = pmid
        self.pma = None
        self.pm_type = None
        self.cr_top_result = None
        self.doi = 'NA'
        #self.pmcid = 'NA'       # not doing PMC just yet.
        self.score = 0          # becomes '10' if found in Pubmed, or a CrossRef score if found there.

        # 1) look up article in PubMed
        self._get_pma()         # fills self.pma

        if self.pma:
            # 2a) try to get doi first in PubMed, then in PMC, then in CrossRef.
            self._get_doi()     # fills self.doi, self.cr_top_result, self.score
            self.pm_type = self.pma.pubmed_type

            # 2b) try to get pmcid first in PubMed, then in PMC.
            # self._get_pmcid()
        else:
            self.score = -1

        # 3) record our efforts.
        outd = self.__dict__
        outd['crossref_query'] = asciify(crossref.last_query)
        outd['crossref_coins'] = None if not self.cr_top_result else self.cr_top_result['coins']
        outd['pubmed_type'] = self.pm_type

        record_entry(**outd)

    def _verify_doi(self, doi):
        return find_doi_in_string(doi)

    def _get_pma(self, tries=1):
        try:
            self.pma = fetch.article_by_pmid(self.pmid)
            process_log.debug("looking up %s (title: %s, journal: %s)" % (self.pmid, self.pma.title, self.pma.journal))

        except XMLSyntaxError:
            # XML did not completely download... try again.
            if tries < self.PMA_RETRY_LIMIT:
                tries += 1
                self._get_pma(tries)
        except ConnectionError:
            handle_connection_error()
        except Exception, e:
            record_error(self.pmid, 'PubMedArticle', e)

    def _get_pmcid(self):
        if self.pma.pmc:
            pmcid = self.pma.pmc
        else:
            pmcid = get_pmcid_for_otherid(pmid)
        if pmcid:
            self.pmcid = pmcid

    def _get_doi(self):
        if self.pma.doi:
            # there are quite a few DOIs are aren't real DOIs in PubMed XML.
            if self._verify_doi(self.pma.doi):
                process_log.debug("%s: Found DOI in PubMed XML", self.pma.pmid)
                self.doi = self.pma.doi
                self.score = 10
                self.source = 'PubMed'

        # No DOI yet?  keep going
        try:
            cr_results = crossref.query_from_PubMedArticle(self.pma)
        except ConnectionError:
            handle_connection_error('CrossRef could not be reached')
        except Exception, e:
            record_error(self.pmid, 'CrossRef', e)
            return

        if cr_results:
            self.top_result = crossref.get_top_result(cr_results)
        else:
            return        

        if self.top_result:
            self.doi = self.top_result['doi']
            self.score = float(self.top_result['score'])
            process_log.debug("%s: CrossRef found doi=%s with score=%.2f" % (self.pma, self.doi, self.score))
        else:
            process_log.debug("%s: CrossRef had no good results for query with q=%s" % (self.pmid, crossref.last_query))
            self.doi = 'NA'
            self.score = '0'


def main():
    pmid = stop = None
    try:
        pmid = int(sys.argv[1])
    except IndexError:
        print('Supply a STARTING PubMed ID number as the argument to this script.')
        sys.exit()
    except ValueError:
        print('First argument (PMID) must be an integer.')
        sys.exit()

    try:
        stop = int(sys.argv[2])
    except IndexError:
        print('No stopping point specified; default to +1000 from initial PMID.')
        stop = 1000
    except ValueError:
        print('Second argument (optional) must be an integer.')
        sys.exit()

    open_logs('%i_%i' % (pmid, stop))

    for pmid in xrange(pmid, pmid+stop):
        blah = PMIDMapping(pmid)
    

if __name__=='__main__':
    main()        


