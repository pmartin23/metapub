from metapub import MedGenFetcher

####
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)

####


fetch = MedGenFetcher()
ids = fetch.ids_by_term('OCRL')
print ids

for this_id in ids:
    concept = fetch.concept_by_id(this_id)
    if concept.semantic_type=='Finding':
        continue
    print concept.title, concept.cui
    print concept.modes_of_inheritance

