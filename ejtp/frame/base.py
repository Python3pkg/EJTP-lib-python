'''
This file is part of the Python EJTP library.

The Python EJTP library is free software: you can redistribute it 
and/or modify it under the terms of the GNU Lesser Public License as
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

the Python EJTP library is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser Public License for more details.

You should have received a copy of the GNU Lesser Public License
along with the Python EJTP library.  If not, see 
<http://www.gnu.org/licenses/>.
'''

from ejtp.util.py2and3 import RawData, String, RawDataDecorator, StringDecorator
from ejtp.util.compat import json

class BaseFrame(object):
    '''
    Base class for all frames.

    self._ancestors is a list containing all cropped frames that contained
    this one. The list is sorted by occurence in the ancestor chain ascending.
    i.e.: If frame A contains B and B contains C, self._ancestors in C will be
    [B, A]
    '''

    @RawDataDecorator()
    def __init__(self, data, ancestors = None):
        if not isinstance(data, RawData):
            raise TypeError('data must be of type RawData') 
        self._content = data
        if ancestors is None:
            self._ancestors = []
        else:
            self._ancestors = ancestors[:]

    @StringDecorator(args=False, ret=True)
    @RawDataDecorator(args=False, ret=True, strict=True)
    def decode(self, ident_cache):
        '''
        Decodes the content of the frame with ident_cache and returns RawData if the content
        is another Frame or String if it is a json encoded string.
        '''
        raise NotImplementedError('Each subclass of BaseFrame must implement decode')
   
    def unpack(self, ident_cache):
        '''
        Returns a Frame or json-parsed object decoded from the content.
        '''
        decoded = self.decode(ident_cache)
        if isinstance(decoded, RawData):
            # assuming it's a new Frame
            from ejtp.frame.registration import createFrame
            return createFrame(decoded, [self.crop()] + self._ancestors)
        elif isinstance(decoded, String):
            return json.loads(decoded)

    def crop(self):
        '''
        Returns a copy of this frame only containing the header.
        '''
        return self.__class__(self._content[:1+self.header_length])
 
    @property
    def header_length(self):
        if 0 in self._content:
            return self._content.index(0)
        return 0

    @property
    def header(self):
        return self._content[1:self.header_length]

    @property
    def body(self):
        return self._content[self.header_length+1:]

    def last_category(self, category):
        '''
        Returns last (in terms of inheritance) ancestor of category category.
        '''
        if not issubclass(category, BaseCategory):
            raise TypeError('category must be subclass of BaseCategory')
        for ancestor in self._ancestors:
            if isinstance(ancestor, category):
                return ancestor
        


class BaseCategory(object):
    '''
    Base category for all frame categories.

    Inherit from a category if you want your Frame to be in it.

    >>> class FooCategory(BaseCategory):
    ...     pass
    ...
    >>> from ejtp.frame import RegisterFrame
    >>> @RegisterFrame('b')
    ... class BarFrame(BaseFrame, FooCategory):
    ...     pass
    ...
    '''

    pass