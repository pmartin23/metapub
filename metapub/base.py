from __future__ import absolute_import

from lxml import etree


def parse_elink_response(xmlstr):
    '''return all Ids from an elink XML response'''
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

    def __init__(self, xmlstr, root=None, *args, **kwargs):
        if not xmlstr:
            if xmlstr == '':
                xmlstr = 'empty'
            raise MetaPubError('Cannot build MetaPubObject; xml string was %s' % xmlstr)
        self.xmlstr = xmlstr
        self.content = self._parse_xml(xmlstr, root)

    def _parse_xml(self, xmlstr, root=None):
        dom = etree.fromstring(xmlstr)
        if root:
            return dom.find(root)
        else:
            return dom

    def _get(self, tag):
        n = self.content.find(tag)
        if n is not None:
            return n.text
        return None

# singleton class used by the fetchers.
class Borg(object):
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state


