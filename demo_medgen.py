import sys

from tabulate import tabulate

from metapub import MedGenFetcher

try:
    gene = sys.argv[1]
except IndexError:
    print 'Supply a Hugo gene name to this script as its argument.'
    sys.exit()


####
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)

####

fetch = MedGenFetcher()
ids = fetch.ids_by_term(gene)
#print ids

# TODO: Term Hierarchy Children (only 1 tier below), Term Hierarchy Parents (only 1 tier above)

headers = ['Hugo gene name', 'Medgen Disease or Syndrome', 'MedGen UID', 
           'OMIM ID', 'Modes of Inheritance', 'Assoc Genes', 
          ]

table = []

for this_id in ids:
    concept = fetch.concept_by_id(this_id)
    if concept.semantic_type=='Disease or Syndrome':
        assert concept.uid == this_id
        line = [concept.cui, concept.title, concept.uid, concept.omim]
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

