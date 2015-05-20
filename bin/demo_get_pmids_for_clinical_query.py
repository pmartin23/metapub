from metapub import PubMedFetcher
fetch = PubMedFetcher()
results = fetch.pmids_for_medical_genetics_query('Brugada Syndrome', 'diagnosis')

print results


