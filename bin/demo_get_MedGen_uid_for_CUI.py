import sys

from tabulate import tabulate

from metapub import MedGenFetcher

# example of CUID: C0000039

try:
    cuid = sys.argv[1]
except IndexError:
    print 'Supply a ConceptID (CUID) to this script as its argument.'
    sys.exit()

####
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)
####

fetch = MedGenFetcher()
cuid = fetch.id_for_cuid(cuid)
print cuid 

