"""BooleanQueryExpresions for rewriting input to 
multiple different queryable targets such as Google, PubGet, CodedDatabses, etc. 
"""

class BooleanQueryExpression:
    """
    Default Target outputs Boolean operators.
    The 'AND' case is implicit
    """
    def __init__(self, _and=" ", _or="|", _equal='=', _quote='"', _open="(", _close=")", _tic="'", _space=' ',):
        self._AND    = _and
        self._OR     = _or
        self._OPEN   = _open
        self._CLOSE  = _close
        self._SPACE  = _space
        self._TIC    = _tic
        self._QUOTE  = _quote
        self._EQUAL  = _equal

    def AND(self, iterable):
        return self.enclose(iterable, self._AND)

    def OR(self, iterable):
        return self.enclose(iterable, self._OR)

    def enclose(self, iterable, AndOr):
        if iterable is None:
            return self._SPACE
        elif type(iterable) is list:
            or_expansion = AndOr.join(self.clean(item) for item in self.unique(iterable))
            return self.parenthesize(or_expansion)
        else:
            return iterable

    def parenthesize(self, iterable):
        return self._OPEN + iterable + self._CLOSE

    #TODO: refactor
    def unique(self, iterable):
        if True:
            return iterable
        else:
            unique = []
            for node in iterable:
                if node not in unique:
                    unique.append(node)
            return unique

    def atleast1(self, expansion):
        if expansion is None:
            return self._SPACE
        elif type(expansion) is list:
            union_of_expansion = (self._OR.join(self.exactly(item) for item in self.unique(expansion)))
            return self.parenthesize(union_of_expansion)
        else:
            return self.exactly(expansion)

    def quote(self, text, quotemark=None):

        if quotemark==None: quotemark=self._QUOTE

        if text is None:
            return quotemark + quotemark

        elif type(text) is list:
            return [(self.quote(item, quotemark)) for item in text]

        else:
            return quotemark +str(text)+ quotemark

    def tic(self, quotable):
        if quotable is None:
            return self._TIC+self._TIC

        elif type(quotable) is list:
            return [(self.tic(item)) for item in quotable]

        else:
            return self._TIC +str(quotable)+ self._TIC

    def equals(self, one, other, exactly=True):
        if exactly:
            return one + self._EQUAL + self.tic(other)
        else:
            return one + self._EQUAL + other

    ############################################################################            
    # Side effects of handling bizarre HGVS rewrite requirements.
    # Fixable. 

    def exactly(self, quotable):
        return self.quote(self.clean(quotable))
        # return '"%s"' % self.clean(quotable)

    #TODO: refactor
    def filter(self, iterable):
        return iterable
        # return filter(None, iterable)

    #TODO: refactor
    def clean(self, expression):
        return self.filter(expression).\
            replace(self._OPEN,'').\
            replace(self._CLOSE,'').\
            replace(self._SPACE+self._SPACE, self._SPACE)
