from __future__ import absolute_import

import os
from lxml import etree

from .exceptions import MetaPubError

def pick_from_kwargs(args, options, default=None):
    for opt in options:
        if args.get(opt, None):
            return args[opt]
    return default

def asciify(inp):
    '''nuke all the unicode from orbit. it's the only way to be sure.'''
    if inp:
        return inp.encode('ascii', 'ignore')
    else:
        return ''

def parameterize(inp, sep='+'):
    '''make strings suitable for submission to GET-based query service'''
    return asciify(inp).replace(' ', sep)

def deparameterize(inp, sep='+'):
    '''undo parameterization in string. replace separators (sep) with spaces.'''
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


