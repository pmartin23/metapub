from metapub import PubMedFetcher
fetch = PubMedFetcher()
params = { 'jtitle': 'American Journal of Medical Genetics', 
                    'year': 1996, 
                    'volume': 61, 
                    'author1_lastfm': 'Hegmann' }

stuff = fetch.pmids_for_query(**params)
print params
print stuff

params = { 'TA':'Journal of Neural Transmission', 
                    'pdat':2014, 
                    'vol':121, 
                    'aulast': 'Freitag'
         } 

stuff = fetch.pmids_for_query(**params)

print params
print stuff

params = { 'mesh': 'breast neoplasm' }
stuff = fetch.pmids_for_query(since='2015/1/1', until='2015/3/1', pmc_only=True, **params)

print params
print stuff
