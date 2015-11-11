from __future__ import absolute_import, print_function, unicode_literals

import requests

from downloader import Downloader

JOURNAL_LIST_URL = 'ftp://ftp.ncbi.nih.gov/pubmed/J_Entrez.txt'


def parse_journal_entry(chunk):
    return None

def parse_journal_blob(chunk):
    '''Takes the text content of the JOURNAL_LIST_URL response and
    parses it into a list of chunks that can be parsed by 
    parse_journal_entry.

    :param: blob (string)
    :return: list of chunks
    '''
    
def retrieve_journal_list():
    '''Uses Downloader.mirror function to grab JOURNAL_LIST_URL (if different).

    :return: response.content (string)
    '''
    dldr = Downloader()
    result = dldr.mirror(JOURNAL_LIST_URL, '/tmp/NCBI_journal_list')
    print(result)

if __name__ == '__main__':
    retrieve_journal_list()

