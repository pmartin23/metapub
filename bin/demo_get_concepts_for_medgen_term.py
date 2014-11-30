import sys

from tabulate import tabulate
from metapub import MedGenFetcher

try:
    input_gene = sys.argv[1]
except IndexError:
    print 'Supply a Hugo gene name to this script as its argument.'
    sys.exit()

####
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)
####

fetch = MedGenFetcher()
uids = fetch.uids_by_term(input_gene)
#print ids

# TODO: Term Hierarchy Children (only 1 tier below), Term Hierarchy Parents (only 1 tier above)

headers = ['CUI', 'Hugo', 'Medgen Disease or Syndrome', 'MedGenUID', 
           'OMIM ID', 'Modes of Inheritance', 'Assoc Genes', ]

table = []

for this_id in uids:
    concept = fetch.concept_by_uid(this_id)
    #print concept.to_dict()
    if concept.semantic_type=='Disease or Syndrome':
        assert concept.medgen_uid == this_id
        line = [concept.CUI, input_gene, concept.title, concept.medgen_uid, concept.OMIM]
        modes = concept.modes_of_inheritance
        if modes:
            line.append(','.join([mode['name'] for mode in modes]))
        else:
            line.append('NA')

        genes = concept.associated_genes
        if genes:
            line.append(','.join([gene['hgnc'] for gene in genes]))
        else:
            line.append('NA')

        table.append(line)

print tabulate(table, headers, tablefmt="simple")

