from __future__ import absolute_import, unicode_literals

import os, sys
import re
import unicodedata

import six
from lxml import etree
from unidecode import unidecode


PUNCS_WE_DONT_LIKE = "[],.()<>'/?;:\"&"

def kpick(args, options, default=None):
    for opt in options:
        if args.get(opt, None):
            return args[opt]
    return default

def remove_chars(inp, chars=PUNCS_WE_DONT_LIKE):
    chars = re.escape(chars)

    #TODO: use six.binary_type and whatnot here -- this is getting nuts
    if six.PY2:
        outp = re.sub(b'['+chars+']', b'', b'inp')
    else:
        outp = re.sub('['+chars+']', '', inp)
    return outp

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
    inp = remove_chars(inp, PUNCS_WE_DONT_LIKE) 
    inp = squash_spaces(inp).replace(' ', sep)

    if six.PY2:
        return asciify(inp)
    else:
        return unidecode(inp)

def deparameterize(inp, sep='+'):
    '''somewhat-undo parameterization in string. replace separators (sep) with spaces.'''
    return inp.replace(sep, ' ')

def remove_html_markup(inp):
    '''remove html and xml tags from text. preserves HTML entities like &amp;'''
    tag = False
    quote = False
    out = ""

    for char in inp:
        if char == '<' and not quote:
            tag = True
        elif char == '>' and not quote:
            tag = False
        elif (char == '"' or char == "'") and tag:
            quote = not quote
        elif not tag:
            out = out + char
    return out

def lowercase_keys(dct):
    '''takes an input dictionary, returns dictionary with all keys lowercased.'''
    result = {}
    for key, value in list(dct.items()):
        result[key.lower()] = value
    return result

