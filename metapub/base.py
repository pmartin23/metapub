from __future__ import absolute_import, unicode_literals

import six

from lxml import etree

from .exceptions import MetaPubError


def parse_elink_response(xmlstr):
    '''return all Ids from an elink XML response'''
    if six.PY3 and type(xmlstr) == six.binary_type:
        xmlstr = xmlstr.decode()
    dom = etree.fromstring(xmlstr)
    ids = []
    if dom.find('LinkSet/LinkSetDb/LinkName').text:
        linkset = dom.find('LinkSet/LinkSetDb')
        for link in linkset.getchildren():
            if link.find('Id') is not None:
                ids.append(link.find('Id').text)
        return ids
    else:
        return None


class MetaPubObject(object):
    '''Base class for XML parsing objects (e.g. PubMedArticle)'''

    def __init__(self, xml, root=None, *args, **kwargs):
        '''Instantiate with "xml" as string or bytes containing valid XML.

        Supply name of root element (string) to set virtual top level. (optional).''' 
 
        if not xml:
            if xml == '':
                xml = 'empty'
            raise MetaPubError('Cannot build MetaPubObject; xml string was %s' % xml)
        self.xml = xml
        self.content = self.parse_xml(xml, root)

    @staticmethod
    def parse_xml(xml, root=None):
        '''Takes xml (str or bytes) and (optionally) a root element definition string.

        If root element defined, DOM object returned is rebased with this element as
        root.

        Args:
            xml (str or bytes)
            root (str): (optional) name of root element

        Returns:
            lxml document object.
        '''
        if isinstance(xml, str) or isinstance(xml, bytes):
            dom = etree.XML(xml)
        else:
            dom = etree.XML(xml)

        if root:
            return dom.find(root)
        else:
            return dom

    def _get(self, tag):
        '''Returns content of named XML element, or None if not found.'''
        elem = self.content.find(tag)
        if elem is not None:
            return elem.text
        return None

# singleton class used by the fetchers.
class Borg(object):
    '''singleton class backing cache engine objects.'''
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
