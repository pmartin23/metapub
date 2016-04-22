from __future__ import absolute_import, unicode_literals

try:
    from urlparse import urlparse
except ImportError:
    # assume python3
    from urllib.parse import urlparse

from metapub.findit.journals import misc_vip, misc_doi, misc_pii

fh = open('metapub/urlreverse/hostname2jrnl.py', 'w')

fh.write('from __future__ import absolute_import, unicode_literals\n')
fh.write('\n')
fh.write('HOSTNAME_TO_JOURNAL_MAP = {\n')
for jrnl, value in misc_vip.vip_journals.items():
    fh.write("\t\t'%s': '%s',\n" % (value['host'], jrnl))

for jrnl, url in misc_pii.simple_formats_pii.items():
    hostname = urlparse(url).hostname
    fh.write("\t\t'%s': '%s',\n" % (hostname, jrnl))

fh.write('}\n')

