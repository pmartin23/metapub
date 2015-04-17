from __future__ import absolute_import

import os
from lxml import etree
import unicodedata

PUNCS_WE_DONT_LIKE = "[],.()<>'/?;:\"&"

def kpick(args, options, default=None):
    for opt in options:
        if args.get(opt, None):
            return args[opt]
    return default

def asciify(inp):
    '''nuke all the unicode from orbit. it's the only way to be sure.'''
    if inp:
        try:
            return inp.encode('ascii', 'ignore')
        except UnicodeDecodeError:
            return unicodedata.normalize('NFKD', inp.decode('utf-8')).encode('ascii', 'ignore')
    else:
        return ''

def squash_spaces(inp):
    '''convert multiple ' ' chars to a singles'''
    return ' '.join(inp.split())

def parameterize(inp, sep='+'):
    '''make strings suitable for submission to GET-based query service. strips
        out these characters: %s''' % PUNCS_WE_DONT_LIKE
    return squash_spaces(asciify(inp).translate(None, PUNCS_WE_DONT_LIKE)).replace(' ', sep)

def deparameterize(inp, sep='+'):
    '''somewhat-undo parameterization in string. replace separators (sep) with spaces.'''
    return inp.replace(sep, ' ')

def remove_html_markup(s):
    '''remove html and xml tags from text. preserves HTML entities like &amp;'''
    tag = False
    quote = False
    out = ""

    for c in s:
            if c == '<' and not quote:
                tag = True
            elif c == '>' and not quote:
                tag = False
            elif (c == '"' or c == "'") and tag:
                quote = not quote
            elif not tag:
                out = out + c
    return out

def lowercase_keys(d):
    result = {}
    for key, value in d.items():
        result[key.lower()] = value
    return result



