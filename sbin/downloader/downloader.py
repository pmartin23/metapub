# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import zipfile
import os, logging

from six.moves import urllib

import requests
from requests.packages import urllib3

REQUESTS_TIMEOUT = 2000

#DEFAULT_HEADERS = { 
#    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30', 
#                  }

DEFAULT_HEADERS = {}

log = logging.getLogger('library.downloader')

#suppress those unfortunate SSL-cert warnings from journal websites.
urllib3.disable_warnings()

def is_pdf_file(filepath):
    '''uses file's "magic number" to check whether the file is a PDF.

       :param: filepath (string) - path to file
       :return: bool - True if PDF, False if not.
    '''
    try:
        infile = open(filepath,'rb')
        magicNumber = infile.read(4)
        infile.close()
        return magicNumber=='%PDF'
    except Exception as error:
        return False

def has_nonzero_filesize(filepath, min_size=10):
    '''uses os.stat to check filesize of file.

    :param: filepath (string) - path to file
    :param: min_size (int) [default: 10] - expected min size in bytes
    :return: bool - True size > min_size; False if not.
    '''

    if os.path.exists(filepath):
        # check that it has a nonzero filesize
        filestat = os.stat(filepath)
        if filestat.st_size > min_size:
            return True
    return False


class Downloader(object):
    '''handles downloading of PDFs to a temporary location.

    In the not too distant future, it should do nice things that keep us from losing access
    privileges to PMC and the like, such as batch-timing.'''

    TMPDIR = '/tmp'
    TMPFILE_TMPL = '{pmid}.pdf'
    
    def get_tmppath_for_pmid(self, pmid):
        return os.path.join(self.TMPDIR, self.TMPFILE_TMPL.format(pmid=pmid))

    def get_tmppath(self, filename):
        return os.path.join(self.TMPDIR, filename)

    def unzip(self, zipfilepath, destdir=None, remove_zip=False):
        '''unzips zipfilepath into specified destdir (if specified), or into its own 
        directory if destdir not specified.
    
        If remove_zip param True (default: False), remove the source zip file
        after successful extraction.

            :param: zipfilepath (string) - absolute path to zipfile
            :param: destdir (string) [default: None] 
            :param: remove_zip (bool) [default: False] 
            :return: list of absolute paths to the extracted files.
        '''
        if not destdir:
            destdir = os.path.split(zipfilepath)[0]

        with zipfile.ZipFile(zipfilepath, "r") as the_zip:
            the_zip.extractall(destdir)

        results = []
        for fname in os.listdir(destdir):
            if fname != os.path.split(zipfilepath)[1]:
                results.append(os.path.join(destdir, fname))

        if remove_zip:
            os.remove(zipfilepath)

        return results


    def article_from_sources(self, pmid, sources, refile=True):
        '''takes pmid and list of ranked ArticleSources, iterates over each source.url 
        until it successfully downloads the desired file.

        If refile == True, immediately use PubMedFileManager to refile article.

        If PDF successfully downloaded, return the ArticleSource object that
        was used to provide the url to download the file.

        If all sources.url entries become exhausted, return None.

            :param: pmid (string)
            :param: sources (list of ArticleSource objects)
            :param: refile (bool) [default: True] 
            :return: ArticleSource or None
        '''
        filepath = self.get_tmppath_for_pmid(pmid)
        for source in sources:
            # try downloading from explicit URLs
            if source.url and source.source != 'Library':
                result = self.request_write_file(source.url, filepath, 'pdf')
                if result[2]:
                    return (source, filepath) 
        return None

    def request_write_file(self, url, filepath, expected_filetype=None, post_args=None,
                           headers=DEFAULT_HEADERS, timeout=REQUESTS_TIMEOUT):
        '''
        :param: url (string) - target url pointing to content for download
        :param: filepath (string) - output filepath
        :param: expected_filetype (string) [default:None]
        :param: post_args (dict) [default: None] - arguments to submit as POST request
        :param: headers (dict) [default: downloader.DEFAULT_HEADERS] - HTTP headers to submit with query
        :param: timeout (int) [default: downloader.REQUESTS_TIMEOUT] - milliseconds to wait for a response
        :return: tuple - (response.status_code, response.headers['content-type'], None)
        '''
        check_if_pdf = False
        if expected_filetype:
            check_if_pdf = True if expected_filetype.lower()=='pdf' else False

        # verify=False means it ignores bad SSL certs
        if post_args:
            response = requests.post(url, stream=True, verify=False, data=post_args,
                                        timeout=timeout, headers=headers)
        else:
            response = requests.get(url, stream=True, verify=False, 
                                        timeout=timeout, headers=headers)

        if response.status_code == 200:
            # If it's sending us something we're not expecting, cut it off right away:
            if expected_filetype and expected_filetype.lower() not in response.headers.get('content-type'):
                return (response.status_code, response.headers['content-type'], None)

            # If we don't care what it is, or we do care and our filetype expectations are met:
            else:
                with open(filepath, 'wb') as handle:
                    for block in response.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)

        # check if file was downloaded and has a filesize greater than 10 bytes:
        if self._verify_download(filepath, check_if_pdf):
            return (response.status_code, response.headers['content-type'], filepath)
        else:
            return (response.status_code, response.headers['content-type'], None)

    def ftp(self, url, filepath):
        '''Uses FTP to download file from designated url to designated filepath.'''
        #result = urllib.urlretrieve(url, filepath)
        result = urllib.request.urlretrieve(url, filepath)
        return result

    def ftp_get_remote_filesize(self, url):
        '''Uses FTP to check and return integer 'content-length' value of remote file 
            at provided url.'''
        #req = urllib.urlopen(url)
        req = urllib.request.urlopen(url)
        return int(req.headers.get('content-length'))

    def http_get_remote_filesize(self, url):
        '''Checks and returns integer 'Content-Length' header sent from remote url.''' 
        #req = urllib2.urlopen(url)
        req = urllib.request.urlopen(url)
        return int(req.headers['Content-Length'])

    def mirror(self, url, filepath, post_args=None, expected_filetype=None):
        '''Downloads specified url into specified filepath, doing a Content-Length
        comparison of remote and local files to avoid re-downloading identical 
        files.

        url protocol may be FTP or HTTP.

        If post_args is set and protocol is HTTP, uses POST method rather than GET,
        HOWEVER -- WARNING -- no filesize comparison can be done, only a check to 
        see whether the target filepath already exists.
        
        :param: url (string) - url to mirror
        :param: filepath (string) - path to place new/updated file
        :param: post_args (dict) [default: None] - if set, switches to POST method
        :param: expected_filetype (string) [default: None] - set to 'pdf' if desired
        :return: tuple - (response.status_code, response.headers['content-type'], None)
        '''

        protocol = urllib.parse.urlparse(url).scheme
        method = 'GET' if not post_args else 'POST'

        if os.path.exists(filepath) and method=='GET':
            fileinfo = os.stat(filepath)

            if protocol=='ftp':
                remote_filesize = self.ftp_get_remote_filesize(url)
            else:
                remote_filesize = self.http_get_remote_filesize(url)

            log.debug('[MIRROR] %s: Content-Length = %i, %s: Filesize = %i', url, 
                        remote_filesize, filepath, fileinfo.st_size)
        
            if remote_filesize == fileinfo.st_size:
                log.info('[MIRROR] %s: Not downloading since local file %s is identical', url, filepath)
                return (200, None, filepath)
            else:
                log.info('[MIRROR] %s: Starting download since local file %s needs an update.', url, filepath)

        elif os.path.exists(filepath) and method=='POST':
            return (200, 'filesystem', filepath)

        else:
            log.info('[MIRROR] %s: Starting download since no copy exists at %s.', url, filepath)

        if protocol=='ftp':
            log.debug('[MIRROR] %s: downloading via FTP')
            return self.ftp(url, filepath)
        else:
            log.debug('[MIRROR] %s: downloading via HTTP')
            return self.request_write_file(url, filepath, post_args=post_args, 
                                           expected_filetype=expected_filetype)
        

    def _verify_download(self, filepath, check_if_pdf=False):
        if check_if_pdf:
            if not is_pdf_file(filepath):
                return False

        return has_nonzero_filesize(filepath)

