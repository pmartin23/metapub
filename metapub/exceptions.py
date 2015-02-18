from lxml.etree import XMLSyntaxError

class MetaPubError(Exception):
    pass

class InvalidPMID(MetaPubError):
    pass

class CrossRefConnectionError(MetaPubError):
    pass


