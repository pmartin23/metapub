from metapub import PubMedFetcher
fetch = PubMedFetcher()
stuff = fetch.pmids_for_citation(journal_title='American Journal of Medical Genetics', 
                    year=1996, 
                    volume=61, 
                    first_page=10, 
                    author_name='Katherine M. Hegmann; Aimee S. Spikes; Avi Orr-Urtreger; Lisa G. Shaffer')

print stuff

stuff = fetch.pmids_for_citation(journal_title='Journal of Neural Transmission', 
                    year=2014, 
                    volume=121, 
                    first_page=1077, 
                    )  # author_name='Freitag'

print stuff


