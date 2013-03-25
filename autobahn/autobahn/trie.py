###############################################################################
##
##  Copyright (c) 2009, George Sakkis
##
##  All rights reserved.
##
##  Redistribution and use in source and binary forms, with or without
##  modification, are permitted provided that the following conditions are met:
##
##      * Redistributions of source code must retain the above copyright notice,
##        this list of conditions and the following disclaimer.
##      * Redistributions in binary form must reproduce the above copyright
##        notice, this list of conditions and the following disclaimer in the
##        documentation and/or other materials provided with the distribution.
##      * The names of its contributors may not be used to endorse or promote
##        products derived from this software without specific prior written
##        permission.
##
##  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
##  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
##  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
##  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
##  OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
##  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
##  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
##  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
##  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
##  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
##  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
###############################################################################

''':mod:`pytrie` is a pure Python implementation of the
`trie <http://en.wikipedia.org/wiki/Trie>`_ (prefix tree) data structure.

A *trie* is a tree data structure that is used to store a mapping where the keys
are sequences, usually strings over an alphabet. In addition to implementing the
mapping interface, tries facilitate finding the items for a given prefix, and
vice versa, finding the items whose keys are prefixes of a given key ``K``. As a
common special case, finding the longest-prefix item is also supported.

Algorithmically, tries are more efficient than binary search trees (BSTs) both
in lookup time and memory when they contain many keys sharing relatively few
prefixes. Unlike hash tables, trie keys don't need to be hashable. In the current
implementation, a key can be any finite iterable with hashable elements.

Usage
-----
>>> from pytrie import SortedStringTrie as trie
>>> t = trie(an=0, ant=1, all=2, allot=3, alloy=4, aloe=5, are=6, be=7)
>>> t
SortedStringTrie({'all': 2, 'allot': 3, 'alloy': 4, 'aloe': 5, 'an': 0, 'ant': 1, 'are': 6, 'be': 7})
>>> t.keys(prefix='al')
['all', 'allot', 'alloy', 'aloe']
>>> t.items(prefix='an')
[('an', 0), ('ant', 1)]
>>> t.longest_prefix('antonym')
'ant'
>>> t.longest_prefix_item('allstar')
('all', 2)
>>> t.longest_prefix_value('area', default='N/A')
6
>>> t.longest_prefix('alsa')
Traceback (most recent call last):
    ...
KeyError
>>> t.longest_prefix_value('alsa', default=-1)
-1
>>> list(t.iter_prefixes('allotment'))
['all', 'allot']
>>> list(t.iter_prefix_items('antonym'))
[('an', 0), ('ant', 1)]
'''

__all__ = ['Trie', 'StringTrie', 'SortedTrie', 'SortedStringTrie', 'Node']

#TODO:
# - bitbucket project + ANN
# - (0.2 benchmarks/profiling/optimization)

from copy import copy
from operator import itemgetter
from UserDict import DictMixin

# Singleton sentinel - works with pickling
class NULL(object): pass


class Node(object):
    '''Trie node class.

    Subclasses may extend it to replace :attr:`ChildrenFactory` with a different
    mapping class (e.g. `sorteddict <http://pypi.python.org/pypi/sorteddict/>`_).

    :ivar value: The value of the key corresponding to this node or :const:`NULL`
        if there is no such key.
    :ivar children: A ``{key-part : child-node}`` mapping.
    '''
    __slots__ = ('value', 'children')

    #: A callable for creating a new :attr:`children` mapping.
    ChildrenFactory = dict

    def __init__(self, value=NULL):
        self.value = value
        self.children = self.ChildrenFactory()

    def numkeys(self):
        '''Return the number of keys in the subtree rooted at this node.'''
        return ((self.value is not NULL) +
                 sum(child.numkeys() for child in self.children.itervalues()))

    def __repr__(self):
        return '(%s, {%s})' % (
            self.value is NULL and 'NULL' or repr(self.value),
            ', '.join('%r: %r' % t for t in self.children.iteritems()))

    def __copy__(self):
        clone = self.__class__(self.value)
        clone_children = clone.children
        for key,child in self.children.iteritems():
            clone_children[key] = child.__copy__()
        return clone

    def __getstate__(self):
        return (self.value, self.children)

    def __setstate__(self, state):
        self.value, self.children = state


class Trie(DictMixin, object):
    '''Base trie class.

    As with regular dicts, keys are not necessarily returned sorted. Use
    :class:`SortedTrie` if sorting is required.
    '''

    #: Callable for forming a key from its parts.
    KeyFactory = tuple

    #: Callable for creating new trie nodes.
    NodeFactory = Node

    def __init__(self, seq=None, **kwargs):
        '''Create a new trie.

        Parameters are the same with ``dict()``.
        '''
        self._root = self.NodeFactory()
        self.update(seq, **kwargs)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        '''Create a new trie with keys from ``iterable`` and values set to ``value``.

        Parameters are the same with ``dict.fromkeys()``.
        '''
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    #----- trie-specific methods -----------------------------------------------

    def longest_prefix(self, key, default=NULL):
        '''Return the longest key in this trie that is a prefix of ``key``.

        If the trie doesn't contain any prefix of ``key``:
          - if ``default`` is given, return it
          - otherwise raise ``KeyError``
        '''
        try: return self.longest_prefix_item(key)[0]
        except KeyError:
            if default is not NULL:
                return default
            raise

    def longest_prefix_value(self, key, default=NULL):
        '''Return the value associated with the longest key in this trie that is
        a prefix of ``key``.

        If the trie doesn't contain any prefix of ``key``:
          - if ``default`` is given, return it
          - otherwise raise ``KeyError``
        '''
        current = self._root
        longest_prefix_value = NULL
        for part in key:
            current = current.children.get(part)
            if current is None:
                break
            value = current.value
            if value is not NULL:
                longest_prefix_value = value
        if longest_prefix_value is not NULL:
            return longest_prefix_value
        elif default is not NULL:
            return default
        else:
            raise KeyError

    def longest_prefix_item(self, key, default=NULL):
        '''Return the item (``(key,value)`` tuple) associated with the longest
        key in this trie that is a prefix of ``key``.

        If the trie doesn't contain any prefix of ``key``:
          - if ``default`` is given, return it
          - otherwise raise ``KeyError``
        '''
        prefix = []
        append = prefix.append
        current = self._root
        longest_prefix_value = NULL
        max_non_null_index = -1
        for i, part in enumerate(key):
            current = current.children.get(part)
            if current is None:
                break
            append(part)
            value = current.value
            if value is not NULL:
                longest_prefix_value = value
                max_non_null_index = i
        if longest_prefix_value is not NULL:
            del prefix[max_non_null_index+1:]
            return (self.KeyFactory(prefix), longest_prefix_value)
        elif default is not NULL:
            return default
        else:
            raise KeyError

    def iter_prefixes(self, key):
        'Return an iterator over the keys of this trie that are prefixes of ``key``.'
        key_factory = self.KeyFactory
        prefix = []
        append = prefix.append
        node = self._root
        for part in key:
            node = node.children.get(part)
            if node is None:
                break
            append(part)
            if node.value is not NULL:
                yield key_factory(prefix)

    def iter_prefix_values(self, key):
        '''Return an iterator over the values of this trie that are associated
        with keys that are prefixes of ``key``.
        '''
        node = self._root
        for part in key:
            node = node.children.get(part)
            if node is None:
                break
            if node.value is not NULL:
                yield node.value

    def iter_prefix_items(self, key):
        '''Return an iterator over the items (``(key,value)`` tuples) of this
        trie that are associated with keys that are prefixes of ``key``.
        '''
        key_factory = self.KeyFactory
        prefix = []
        append = prefix.append
        node = self._root
        for part in key:
            node = node.children.get(part)
            if node is None:
                break
            append(part)
            if node.value is not NULL:
                yield (key_factory(prefix), node.value)

    #----- extended mapping API methods ----------------------------------------

    def keys(self, prefix=None):
        '''Return a list of this trie's keys.

        :param prefix: If not None, return only the keys prefixed by ``prefix``.
        '''
        return list(self.iterkeys(prefix))

    def values(self, prefix=None):
        '''Return a list of this trie's values.

        :param prefix: If not None, return only the values associated with keys
            prefixed by ``prefix``.
        '''
        return list(self.itervalues(prefix))

    def items(self, prefix=None):
        '''Return a list of this trie's items (``(key,value)`` tuples).

        :param prefix: If not None, return only the items associated with keys
            prefixed by ``prefix``.
        '''
        return list(self.iteritems(prefix))

    def iterkeys(self, prefix=None):
        '''Return an iterator over this trie's keys.

        :param prefix: If not None, yield only the keys prefixed by ``prefix``.
        '''
        return (key for key,value in self.iteritems(prefix))

    def itervalues(self, prefix=None):
        '''Return an iterator over this trie's values.

        :param prefix: If not None, yield only the values associated with keys
            prefixed by ``prefix``.
        '''
        def generator(node, NULL=NULL):
            if node.value is not NULL:
                yield node.value
            for part,child in node.children.iteritems():
                for subresult in generator(child):
                    yield subresult
        if prefix is None:
            node = self._root
        else:
            node = self._find(prefix)
            if node is None:
                node = self.NodeFactory()
        return generator(node)

    def iteritems(self, prefix=None):
        '''Return an iterator over this trie's items (``(key,value)`` tuples).

        :param prefix: If not None, yield only the items associated with keys
            prefixed by ``prefix``.
        '''
        parts = []
        append = parts.append
        def generator(node, key_factory=self.KeyFactory, parts=parts,
                      append=append, NULL=NULL):
            if node.value is not NULL:
                yield (key_factory(parts), node.value)
            for part,child in node.children.iteritems():
                append(part)
                for subresult in generator(child):
                    yield subresult
                del parts[-1]
        node = self._root
        if prefix is not None:
            for part in prefix:
                append(part)
                node = node.children.get(part)
                if node is None:
                    node = self.NodeFactory()
                    break
        return generator(node)

    #----- original mapping API methods ----------------------------------------

    def __len__(self):
        return self._root.numkeys()

    def __iter__(self):
        return self.iterkeys()

    def __contains__(self, key):
        node = self._find(key)
        return node is not None and node.value is not NULL

    def has_key(self, key):
        return key in self

    def __getitem__(self, key):
        node = self._find(key)
        if node is None or node.value is NULL:
            raise KeyError
        return node.value

    def __setitem__(self, key, value):
        node = self._root
        Node = self.NodeFactory
        for part in key:
            next = node.children.get(part)
            if next is None:
                node = node.children.setdefault(part, Node())
            else:
                node = next
        node.value = value

    def __delitem__(self, key):
        nodes_parts = []
        append = nodes_parts.append
        node = self._root
        for part in key:
            append((node,part))
            node = node.children.get(part)
            if node is None:
                break
        if node is None or node.value is NULL:
            raise KeyError
        node.value = NULL
        pop = nodes_parts.pop
        while node.value is NULL and not node.children and nodes_parts:
            node,part = pop()
            del node.children[part]

    def clear(self):
        self._root.children.clear()

    def copy(self):
        clone = copy(super(Trie,self))
        clone._root = copy(self._root)
        return clone

    def __repr__(self):
        return '%s({%s})' % (
            self.__class__.__name__,
            ', '.join('%r: %r' % t for t in self.iteritems()))

    def _find(self, key):
        node = self._root
        for part in key:
            node = node.children.get(part)
            if node is None:
                break
        return node


class StringTrie(Trie):
    '''A more appropriate for string keys :class:`Trie`.'''
    KeyFactory = ''.join


# XXX: quick & dirty sorted dict; currently only iteritems() has to be overriden.
# However this is implementation detail that may change in the future
class _SortedDict(dict):
    def iteritems(self):
        return sorted(dict.iteritems(self), key=itemgetter(0))


class _SortedNode(Node):
    ChildrenFactory = _SortedDict


class SortedTrie(Trie):
    '''A :class:`Trie` that returns its keys (and associated values/items) sorted.

    .. note::
        This implementation does not keep the keys sorted internally; instead it
        sorts them every time a method returning a list or iterator (e.g.
        :meth:`keys`) is called. In cases where a trie is relatively stable
        (few inserts/deletes) and is iterated often, it is probably more efficient
        to use a :attr:`NodeFactory` based on a sorted dict such as
        `sorteddict <http://pypi.python.org/pypi/sorteddict/>`_.
    '''
    NodeFactory = _SortedNode


class SortedStringTrie(SortedTrie,StringTrie):
    'A :class:`Trie` that is both a :class:`StringTrie` and a :class:`SortedTrie`.'


if __name__ == '__main__':
    import doctest
    doctest.testmod()
