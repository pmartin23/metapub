from __future__ import absolute_import, print_function

__doc__ = '''metapub.PubMedFetcher -- tools to deal with NCBI's E-utilities interface to PubMed'''
__author__ = 'nthmost'

from lxml import etree
import requests

from .eutils_common import get_cache_path, get_eutils_client
from .pubmedarticle import PubMedArticle
from .pubmedcentral import get_pmid_for_otherid
from .pubmed_clinicalqueries import *
from .utils import kpick, lowercase_keys, remove_chars
from .text_mining import re_pmid
from .exceptions import MetaPubError, EutilsRequestError, InvalidPMID
from .base import Borg
from .config import DEFAULT_EMAIL


def get_uids_from_esearch_result(xmlstr):
    dom = etree.fromstring(xmlstr)
    uids = []
    idlist = dom.find('IdList')
    for item in idlist.findall('Id'):
        uids.append(item.text.strip())
    return uids


def parse_related_pmids_result(xmlstr):
    outd = {}
    dom = etree.fromstring(xmlstr)
    for linkset in dom.findall('LinkSet/LinkSetDb'):
        heading = linkset.find('LinkName').text.split('_')[-1]
        outd[heading] = []
        for Id in linkset.findall('Link/Id'):
            outd[heading].append(Id.text)
    return outd


class PubMedFetcher(Borg):
    '''PubMedFetcher (a Borg singleton object backed by an optional SQLite cache)

    An interaction layer for querying via specified method to return PubMedArticle objects.

    Currently available methods: eutils

    Basic Usage:

        fetch = PubMedFetcher()

    To specify a service method (more coming soon):

        fetch = PubMedFetcher('eutils')

    To return an article by querying the service with a known PMID:

        paper = fetch.article_by_pmid('123456')

    Similar methods exist for returning papers by DOI and PM Central id:

        paper = fetch.article_by_doi('10.1038/ng.379')
        paper = fetch.article_by_pmcid('PMC3458974')

    Finally, you can search for PMIDs via citation details by using the pmids_for_citation
    method, for which you only need 3 out of 5 details as a list of one or more PMIDs:

        pmids = fetch.pmids_for_citation(journal='Science', year='2008', volume='4',
                first_page='7', author_name='Grant')
    '''

    _cache_filename = 'eutils-cache.db'

    def __init__(self, method='eutils', api_key=None, email=DEFAULT_EMAIL, cachedir='default'):
        Borg.__init__(self)
        self.method = method
        self._cache_path = None

        if method == 'eutils':
            self.api_key = api_key
            self._cache_path = get_cache_path(cachedir, self._cache_filename)
            self.qs = get_eutils_client(self._cache_path, email=email)
            self.article_by_pmid = self._eutils_article_by_pmid
            self.article_by_pmcid = self._eutils_article_by_pmcid
            self.article_by_doi = self._eutils_article_by_doi
            self.batch_query_doi = self._eutils_pmids_for_dois
            self.pmids_for_query = self._eutils_pmids_for_query
        else:
            raise NotImplementedError('coming soon: fetch from local pubmed via medgen-mysql or filesystem cache.')

    def _eutils_article_by_pmid(self, pmid):
        pmid = str(pmid)
        try:
            result = self.qs.efetch(args={'db': 'pubmed', 'id': pmid, 'api_key':self.api_key})
        except EutilsRequestError:
            raise MetaPubError('Invalid ID "%s" (rejected by Eutils); please check the number and try again.' % pmid)

        if result is None:
            return None

        # if result.find('ERROR') > -1:
        #    raise MetaPubError('PMID %s returned ERROR; cannot construct PubMedArticle' % pmid)

        pma = PubMedArticle(result)
        if pma.pmid is None:
            raise InvalidPMID('Pubmed ID "%s" not found' % pmid)
        return pma

    def _eutils_article_by_pmcid(self, pmcid):
        # if user submitted a bare number, prepend "PMC" to make sure it is submitted correctly
        # the conversion API at pubmedcentral.
        pmcid = str(pmcid)
        if re_pmid.findall(pmcid)[0] == pmcid:
            pmcid = 'PMC' + pmcid

        pmid = get_pmid_for_otherid(pmcid)
        if pmid is None:
            raise MetaPubError('No PMID available for PubMedCentral id %s' % pmcid)
        return self._eutils_article_by_pmid(pmid)

    def _eutils_article_by_doi(self, doi):
        pmid = get_pmid_for_otherid(doi)
        if pmid is None:
            raise MetaPubError('No PMID available for doi %s' % doi)
        return self._eutils_article_by_pmid(pmid)


    def _eutils_pmids_for_dois(self, dois,  retstart=0, retmax=500):
        '''batch search for article pmids given a list of dois

        NOTE: this only returns a list of pmids and does not indicate which pmids match the DOIs you supply
        It is recommended that you cross-check the results by retrieving the pubmed metadata for each returned
        pmid and check that the DOIs for the returned pubmed articles match the ones in your set

        Example of series of queries to accomplish "pagination" of data:

        first_250 = fetch.pmids_for_query('some query')
        second_250 = fetch.pmids_for_query('some query', retstart=500, retmax=250)

        :param: dois (list) default None
        :param: retstart (int) default 0
        :param: retmax (int) default 500
        '''

        # We use the advanced query token [AID] to match against article IDs (in this case, DOIs)
        # Using the 'OR' operator allows us to do a batch search and retrieve many results in one request
        query = ' OR '.join(['"'+doi+'"[AID]' for doi in dois])

        print(query)

        result = self.qs.esearch({'db': 'pubmed', 'term': query,
                                  'retmax': retmax, 'retstart': retstart,'api_key':self.api_key})

        return get_uids_from_esearch_result(result)


    def _eutils_pmids_for_query(self, query='', since=None, until=None, retstart=0, retmax=250,
                                pmc_only=False, **kwargs):
        '''returns list of pmids for given freeform query string plus keyword arguments.

        Freeform queries encased in quotes will be considered "exact match" queries.

        All Pubmed Advanced Query tokens (e.g. "TI" for title) are supported, plus many
        "soft" keywords that will, when parsed, map to the correct token for you. For example,
        you can supply journal name with any of the following keywords:

            "journal" == "jtitle" == "journal_title" == "TA"

        Keyword arguments are case-INsensitive since they are lowercased upon arrival.

        Example of series of queries to accomplish "pagination" of data:

        first_250 = fetch.pmids_for_query('some query')
        second_250 = fetch.pmids_for_query('some query', retstart=500, retmax=250)

        :param: query (string) default ''
        :param: since (string) default None  # Y/m/d format expected. Y alone or Y/m allowed.
        :param: until (string) default None  # Y/m/d format expected. Y alone or Y/m allowed.
        :param: retstart (int) default 0
        :param: retmax (int) default 250
        :param: pmc_only (bool) default False  # constructs query to only search Pubmed Central.
        '''

        # lowercase all the things.
        kwargs = lowercase_keys(kwargs)

        q = {}

        query = query.strip()
        # if we find brackets in the query string, assume they are query keyword tags.
        # otherwise, submit the query string with an "ALL" keyword tag.
        # if query.find('[') == -1 and not kwargs.get('clinical_query', False):
        # if this query is surrounded in quotation marks, consider it an "exact match"
        # search against "ALL" fields. Otherwise, leave it untouched.
        if query and query[0] in ['"', "'"]:
            q['ALL'] = query.replace('"', '').replace("'", '')

        # Search within date range (since / until)
        #
        # working examples. search by creation date only works within defined ranges (not "< X" or "> Y")
        # ("2015/3/1"[Date - Create] : "2015/3/3"[Date - Create])
        # ("2015/2/14"[CRDT] : "2015/3/14"[CRDT])
        created_date_template = '"%s"[CRDT]'
        date_range_template = " (%s : %s)"
        if since:
            start = created_date_template % since
            if until:
                end = created_date_template % until
            else:
                end = '"3000"[CRDT]'

            query += date_range_template % (start, end)

        # unique ID referents.
        q['PMID'] = kpick(kwargs, options=['pmid', 'uid', 'pubmed_id'])
        q['AID'] = kpick(kwargs, options=['aid', 'doi'])
        q['book'] = kwargs.get('book', None)
        q['JID'] = kpick(kwargs, options=['jid', 'nlm uid', 'nlm unique id'])
        q['ISBN'] = kwargs.get('ISBN', None)
        q['RN'] = kpick(kwargs, options=['rn', 'rcn', 'ecn'])
        q['GR'] = kpick(kwargs, options=['gr', 'grant number'])

        # Pubmed Date features:
        q['DA'] = kpick(kwargs, options=['da', 'date created'])
        q['LR'] = kpick(kwargs, options=['lr', 'date revised', 'date last revised'])
        q['EDAT'] = kpick(kwargs, options=['edat', 'entrez date'])

        # Journal name:
        q['TA'] = kpick(kwargs, options=['ta', 'journal', 'jtitle', 'journal_title'])

        # Article-level characteristics (title, authors, etc):
        q['TIAB'] = kpick(kwargs, options=['tiab', 'abstract', 'title/abstract'])
        q['TI'] = kpick(kwargs, options=['ti', 'title', 'atitle', 'article_title'])
        q['TT'] = kpick(kwargs, options=['tt', 'transliterated title'])

        q['AU'] = kpick(kwargs, options=['au', 'author'])
        q['1AU'] = kpick(kwargs, options=['1au', 'aulast', 'author1_lastfm', 'author1_last_fm'])
        q['FAU'] = kpick(kwargs, options=['fau', 'first_author', 'author1'])
        q['LASTAU'] = kpick(kwargs, options=['lastau', 'last author'])
        q['CN'] = kpick(kwargs, options=['cn', 'corporate author'])
        q['FIR'] = kpick(kwargs, options=['fir', 'full investigator name'])
        q['IR'] = kpick(kwargs, options=['ir', 'investigator'])
        q['PG'] = kpick(kwargs, options=['pg', 'pages', 'spage', 'first_page'])

        # Volume / Issue characteristics
        q['IP'] = kpick(kwargs, options=['ip', 'issue'])
        q['VTI'] = kpick(kwargs, options=['vta', 'volume title'])
        q['VI'] = kpick(kwargs, options=['vi', 'volume', 'vol'])

        # Content characteristics
        q['LA'] = kpick(kwargs, options=['la', 'language'])
        q['TW'] = kpick(kwargs, options=['tw', 'text'])
        q['PS'] = kpick(kwargs, options=['ps', 'personal name as subject'])
        q['PA'] = kpick(kwargs, options=['pa', 'pharmacological action'])
        q['SB'] = kpick(kwargs, options=['sb', 'subset'])
        q['NM'] = kpick(kwargs, options=['nm', 'supplementary concept'])

        # MeSH characteristics
        q['MHDA'] = kpick(kwargs, options=['mhda', 'mesh date'])
        q['MH'] = kpick(kwargs, options=['mh', 'mesh', 'mesh terms'])
        q['MAJR'] = kpick(kwargs, options=['majr', 'mesh major topic', 'mesh major'])
        q['SH'] = kpick(kwargs, options=['sh', 'mesh subheadings'])

        # Publication characteristics
        q['DCOM'] = kpick(kwargs, options=['dcom', 'completion date'])
        q['DP'] = kpick(kwargs, options=['dp', 'date of publication', 'year',
                                         'pdat'])  # most aligned w/ PubMedArticle.year and CrossRef 'year'
        q['LID'] = kpick(kwargs, options=['lid', 'location id', 'location identifier'])
        q['PUBN'] = kpick(kwargs, options=['pubn', 'publisher'])
        q['PT'] = kpick(kwargs, options=['pt', 'pubmed_type', 'publication type'])
        q['PL'] = kpick(kwargs, options=['pl', 'place of publication'])

        # Miscellaneous, alphabetized by Medline feature tag.
        q['AD'] = kpick(kwargs, options=['ad', 'affiliation'])
        q['OT'] = kpick(kwargs, options=['ot', 'other term'])
        q['NM'] = kpick(kwargs, options=['nm', 'substance name'])
        q['SI'] = kpick(kwargs, options=['si', 'secondary source id'])

        for feature in q.keys():
            if q[feature] != None:
                query += ' "%s"[%s]' % (q[feature], feature)

        # option to query pubmed central only:
        # pubmed pmc[sb]
        if pmc_only:
            query += ' "pubmed pmc"[sb]'

        # if kwargs.get('debug', False):
        print(query)

        result = self.qs.esearch({'db': 'pubmed', 'term': query,
                                  'retmax': retmax, 'retstart': retstart,'api_key':self.api_key})
        return get_uids_from_esearch_result(result)

    def pmids_for_clinical_query(self, query, category, optimization='broad',
                                 since=None, until=None, retstart=0, retmax=250, pmc_only=False, **kwargs):
        '''Takes a query and a category (required, see below) and returns a list
        of pubmed IDs returned by NCBI for that query.

        See also PubMedFetcher.pmids_for_query for other parameters.

            available categories:

                therapy
                diagnosis
                etiology
                prognosis
                prediction

           available optimizations:
                broad   (default)
                narrow

        :param: query (string)
        :param: category (string)
        :param: optimization (string) [default: broad]
        :return: list of pubmed IDs
        '''

        key = '%s_%s' % (category, optimization)
        if query:
            query += ' ' + clinical_query_map[key]
        else:
            raise MetaPubError('Query string required for Clinical Query.')

        kwargs['clinical_query'] = True
        return self.pmids_for_query(query, retstart=retstart, retmax=retmax, since=since, until=until, **kwargs)

    def pmids_for_medical_genetics_query(self, query, category='all', since=None, until=None,
                                         retstart=0, retmax=250, pmc_only=False, **kwargs):
        '''Takes a query and category (see below) and returns a list of pubmed IDs.
        IDs returned by NCBI for that query.

        See also PubMedFetcher.pmids_for_query for other parameters.

            available categories:

                all     (default)
                diagnosis
                differential_diagnosis
                clinical_description
                management
                genetic_counseling
                genetic_testing

        :param: query (string)
        :param: category (string) [default: all]
        :return: list of pubmed IDs
        '''
        if query:
            query += ' ' + medical_genetics_query_map[category]
        else:
            raise MetaPubError('Query string required for Medical Genetics query.')

        kwargs['clinical_query'] = True
        return self.pmids_for_query(query, retstart=retstart, retmax=retmax, since=since, until=until, **kwargs)


    def pmids_for_citation(self,**kwargs):
        '''returns list of pmids for given citation. requires at least 3/5 of these keyword arguments:
            jtitle or journal (journal title)
            year or date
            volume
            spage or first_page (starting page / first page)
            aulast (first author's last name) or author1_first_lastfm (as produced by PubMedArticle class)

        (Note that these arguments were made to match the tokens that arise from CrossRef's result['slugs'].)

        Strings submitted for journal/jtitle will be run through metapub.utils.remove_chars to deal with HTML-
        encoded characters and to remove punctuation.
        '''
        # output format in return:
        # journal_title|year|volume|first_page|author_name|your_key|

        base_uri = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/ecitmatch.cgi?'
        params = {'db': 'pubmed', 'retmode': 'xml', 'bdata': '', 'api_key': self.api_key}
        kwargs = lowercase_keys(kwargs)

        # accept 'journal-title' key from CrossRef
        journal_title = remove_chars(
            kpick(kwargs, options=['jtitle', 'journal', 'journal_title', 'journal-title'], default=''), urldecode=True)
        author_name = _reduce_author_string(kpick(kwargs,
                                                  options=['aulast', 'author1_last_fm', 'author', 'authors'],
                                                  default=''))
        # accept 'first-page' key from CrossRef 'references' list items
        first_page = kpick(kwargs, options=['spage', 'first_page', 'first-page'], default='')
        year = kpick(kwargs, options=['year', 'date', 'pdat'], default='')
        volume = kpick(kwargs, options=['volume'], default='')

        inp_dict = {'journal_title': journal_title,
                    'year': str(year),
                    'volume': str(volume),
                    'first_page': str(first_page),
                    'author_name': author_name,
                    }

        if kwargs.get('debug', False):
            print('Submitted to pmids_for_citation: %r' % inp_dict)

        # clean up any "n/a" values.  eutils doesn't understand them.
        for k in inp_dict:
            if inp_dict[k].lower() == 'n/a':
                inp_dict[k] = ''

        params['bdata'] = '{journal_title}|{year}|{volume}|{first_page}|{author_name}|'.format(**inp_dict)
        content = requests.post(base_uri, params=params).text
        pmids = []
        for item in content.split('\n'):
            if item.strip():
                pmid = item.split('|')[-1]
                pmids.append(pmid.strip())
        return pmids

    def batch_pmids_for_citation(self, citations):
        '''returns list of pmids for batch of citations. requires at least 3/5 of these keyword arguments:
            jtitle or journal (journal title)
            year or date
            volume
            spage or first_page (starting page / first page)
            aulast (first author's last name) or author1_first_lastfm (as produced by PubMedArticle class)

        (Note that these arguments were made to match the tokens that arise from CrossRef's result['slugs'].)

        Strings submitted for journal/jtitle will be run through metapub.utils.remove_chars to deal with HTML-
        encoded characters and to remove punctuation.
        '''
        # output format in return:
        # journal_title|year|volume|first_page|author_name|your_key|
        base_uri = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/ecitmatch.cgi?'
        params = {'db': 'pubmed', 'retmode': 'xml', 'bdata': '', 'api_key': self.api_key}
        joined = []
        for citation in citations:
            citation = lowercase_keys(citation)
            # accept 'journal-title' key from CrossRef
            journal_title = remove_chars(
                kpick(citation, options=['jtitle', 'journal', 'journal_title', 'journal-title'], default=''),
                urldecode=True)
            author_name = _reduce_author_string(kpick(citation,
                                                      options=['aulast', 'author1_last_fm', 'author', 'authors'],
                                                      default=''))
            # accept 'first-page' key from CrossRef 'references' list items
            first_page = kpick(citation, options=['spage', 'first_page', 'first-page'], default='')
            year = kpick(citation, options=['year', 'date', 'pdat'], default='')
            volume = kpick(citation, options=['volume'], default='')
            if '(' in volume:
                volume = ''

            inp_dict = {'journal_title': journal_title.encode('utf-8', 'ignore').decode('utf-8'),
                        'year': str(year),
                        'volume': str(volume),
                        'first_page': str(first_page),
                        'author_name': author_name.encode('utf-8', 'ignore').decode('utf-8'),
                        }
            if citation.get('debug', False):
                print('Submitted to pmids_for_citation: %r' % inp_dict)

            # clean up any "n/a" values.  eutils doesn't understand them.
            for k in inp_dict:
                if inp_dict[k].lower() == 'n/a':
                    inp_dict[k] = ''
            joined.append('{journal_title}|{year}|{volume}|{first_page}|{author_name}|'.format(**inp_dict))
        for j in joined:
            print(j)
        pmids = []
        while True:
            params['bdata'] = ''
            while len(params['bdata']) < 1900 and len(joined) > 0:
                params['bdata']+= joined[-1]+'\r'
                joined.pop()
            req = requests.get(base_uri, params=params)
            if req.status_code == 200:
                content = req.text
                print(content)
                for item in content.split('\n'):
                    if item.strip():
                        pmid = item.split('|')[-1]
                        pmids.append(pmid.strip())
            if len(joined) == 0:
                break
        return pmids

    def related_pmids(self, pmid):
        '''For supplied pmid, return related ids of related pubmed articles,
        organized into a dictionary keyed by type of relation.  The keys include:

            * pubmed    (all related links)
            * citedin   (papers that cited this paper)
            * five      (the "five" that pubmed displays as the top related results)
            * reviews   (review papers that cite this paper)
            * combined  (?)

        query example:
        https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?retmode=xml&dbfrom=pubmed&id=14873513&cmd=neighbor
        '''
        outd = {}
        xmlstr = self.qs.elink({'dbfrom': 'pubmed', 'id': pmid, 'cmd': 'neighbor','api_key':self.api_key})
        outd = parse_related_pmids_result(xmlstr)
        return outd


def _reduce_author_string(author_string):
    # try splitting by commas
    authors = author_string.split(',')
    if len(authors) < 2:
        # try splitting by semicolons
        authors = author_string.split(';')

    author1 = authors[0]
    # presume last name is at the end of the string
    return author1.split(' ')[-1]


""" 
Search Field Descriptions and Tags

from https://www.ncbi.nlm.nih.gov/books/NBK3827/

Affiliation [AD]
Article Identifier [AID]
All Fields [ALL]
Author [AU]
Author Identifier [AUID]
Book [book]
Comment Corrections
Corporate Author [CN]
Create Date [CRDT]
Completion Date [DCOM]
EC/RN Number [RN]
Editor [ED]
Entrez Date [EDAT]
Filter [FILTER]
First Author Name [1AU]
Full Author Name [FAU]
Full Investigator Name [FIR]
Grant Number [GR]   Investigator [IR]
ISBN [ISBN]
Issue [IP]
Journal [TA]
Language [LA]
Last Author [LASTAU]
Location ID [LID]
MeSH Date [MHDA]
MeSH Major Topic [MAJR]
MeSH Subheadings [SH]
MeSH Terms [MH]
Modification Date [LR]
NLM Unique ID [JID]
Other Term [OT]
Owner
Pagination [PG]
Personal Name as Subject [PS]   Pharmacological Action [PA]
Place of Publication [PL]
PMID [PMID]
Publisher [PUBN]
Publication Date [DP]
Publication Type [PT]
Secondary Source ID [SI]
Subset [SB]
Supplementary Concept[NM]
Text Words [TW]
Title [TI]
Title/Abstract [TIAB]
Transliterated Title [TT]
UID [PMID]
Version
Volume [VI]
"""

'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE eSearchResult PUBLIC "-//NLM//DTD esearch 20060628//EN" "https://eutils.ncbi.nlm.nih.gov/eutils/dtd/20060628/esearch.dtd">
<eSearchResult><Count>1</Count><RetMax>1</RetMax><RetStart>0</RetStart><QueryKey>1</QueryKey><WebEnv>NCID_1_129952677_165.112.9.37_9001_1426564126_1266564592_0MetA0_S_MegaStore_F_1</WebEnv><IdList>
<Id>25023161</Id>
</IdList><TranslationSet><Translation>     <From>Journal of Neural Transmission[TA]</From>     <To>"J Neural Transm"[Journal] OR "J Neural Transm"[Journal] OR "J Neural Transm Suppl"[Journal] OR "J Neural Transm Park Dis Dement Sect"[Journal] OR "J Neural Transm Gen Sect"[Journal]</To>    </Translation></TranslationSet><TranslationStack>   <TermSet>    <Term>2014[DP]</Term>    <Field>DP</Field>    <Count>1171381</Count>    <Explode>N</Explode>   </TermSet>   <TermSet>    <Term>"J Neural Transm"[Journal]</Term>    <Field>Journal</Field>    <Count>1177</Count>    <Explode>N</Explode>   </TermSet>   <TermSet>    <Term>"J Neural Transm"[Journal]</Term>    <Field>Journal</Field>    <Count>3005</Count>    <Explode>N</Explode>   </TermSet>   <OP>OR</OP>   <TermSet>    <Term>"J Neural Transm Suppl"[Journal]</Term>    <Field>Journal</Field>    <Count>1409</Count>    <Explode>N</Explode>   </TermSet>   <OP>OR</OP>   <TermSet>    <Term>"J Neural Transm Park Dis Dement Sect"[Journal]</Term>    <Field>Journal</Field>    <Count>226</Count>    <Explode>N</Explode>   </TermSet>   <OP>OR</OP>   <TermSet>    <Term>"J Neural Transm Gen Sect"[Journal]</Term>    <Field>Journal</Field>    <Count>526</Count>    <Explode>N</Explode>   </TermSet>   <OP>OR</OP>   <OP>GROUP</OP>   <OP>AND</OP>   <TermSet>    <Term>121[VI]</Term>    <Field>VI</Field>    <Count>44530</Count>    <Explode>N</Explode>   </TermSet>   <OP>AND</OP>   <TermSet>    <Term>Freitag[1AU]</Term>    <Field>1AU</Field>    <Count>496</Count>    <Explode>N</Explode>   </TermSet>   <OP>AND</OP>  </TranslationStack><QueryTranslation>2014[DP] AND ("J Neural Transm"[Journal] OR "J Neural Transm"[Journal] OR "J Neural Transm Suppl"[Journal] OR "J Neural Transm Park Dis Dement Sect"[Journal] OR "J Neural Transm Gen Sect"[Journal]) AND 121[VI] AND Freitag[1AU]</QueryTranslation></eSearchResult>'''
