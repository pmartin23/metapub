from __future__ import absolute_import, unicode_literals

try:
    from urlparse import urlparse
except ImportError:
    # assume python3
    from urllib.parse import urlparse

from metapub.findit.journals import misc_vip, misc_doi, misc_pii
from metapub.findit.journals import biochemsoc, aaas, 

fh = open('metapub/urlreverse/hostname2jrnl.py', 'w')

fh.write('from __future__ import absolute_import, unicode_literals\n')
fh.write('\n')
fh.write('HOSTNAME_TO_JOURNAL_MAP = {\n')

def write_one_mapping(hostname, jrnl):
    fh.write("\t\t'%s': '%s',\n" % (hostname, jrnl))

# Volume-Issue-Page format
for jrnl, value in misc_vip.vip_journals.items():
    write_one_mapping(value['host'], jrnl)

# PII based
for jrnl, url in misc_pii.simple_formats_pii.items():
    hostname = urlparse(url).hostname
    write_one_mapping(hostname, jrnl)

# BIOCHEMSOC (VIP format)
for jrnl, value in biochemsoc.biochemsoc_journals.items():
    write_one_mapping(value['host'], jrnl)

# AAAS (VIP format)
for jrnl, value in aaas.aaas_journals.items():
    hostname = urlparse(aaas_format.format(ja=value['ja'])
    write_one_mapping(hostname, jrnl)


fh.write('}\n')


# More complicated reversals...

# JAMA? 

# JSTAGE: mostly free (yay)
# Examples:
# J Biochem: https://www.jstage.jst.go.jp/article/biochemistry1922/125/4/125_4_803/_pdf
# Drug Metab Pharmacokinet:
# https://www.jstage.jst.go.jp/article/dmpk/20/2/20_2_144/_article -->
#        Vol. 20 (2005) No. 2 P 144-151 

# KARGER
# {kid} comes from the final nonzero numbers of the article's DOI.
#karger_format = 'http://www.karger.com/Article/Pdf/{kid}'

# CELL
#cell_format = 'http://www.cell.com{ja}/pdf/{pii}.pdf'
#cell_journals = {
#   'Am J Hum Genet': {'ja': '/AJHG'},
#   'Biophys J': {'ja': '/biophysj'},
#   ...
# }    

# 

