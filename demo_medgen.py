from metapub import MedGenFetcher

fetch = MedGenFetcher()
ids = fetch.ids_by_term('OCRL')
print ids

concept = fetch.concept_by_id(ids[0])

#from IPython import embed; embed()


