#!/usr/bin/python
# -*- coding: utf8
import collections

__author__ = 'daddy-bear'

_emptyListFactory = lambda: []


def emptyListDict():
    return collections.defaultdict(_emptyListFactory)


_emptySetFactory = lambda: set()


def emptySetDict():
    return collections.defaultdict(_emptySetFactory)


_zeroFactory = lambda: 0


def zeroDict():
    return collections.defaultdict(_zeroFactory)


class FrozenDict(collections.Mapping):
    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)
        self._hash = None

    def __setattr__(self, key, value):
        raise NotImplementedError("this is frozen dict")

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def __hash__(self):
        if self._hash is None:
            self._hash = 0
            for pair in self.iteritems():
                self._hash ^= hash(pair)
        return self._hash

    def __eq__(self, other):
        assert isinstance(other, FrozenDict)
        return frozenset(self.items()) == frozenset(other.items())


class MultiSet(object):
    @staticmethod
    def _read_dict(some_iterable):
        d = zeroDict()
        for e in some_iterable:
            d[e] += 1
        return d

    def __init__(self, *args, **kwargs):
        if isinstance(args[0], (tuple, list)):
            self._d = dict(MultiSet._read_dict(args[0]))
        elif len(args) != 1 or not isinstance(args[0], dict):
            self._d = dict(MultiSet._read_dict(args))
        else:
            self._d = dict(*args, **kwargs)

    def iter_elements(self):
        for entry in self._d.iteritems():
            for i in xrange(entry[1]):
                yield entry[0]

    def iter_entries(self):
        return self._d.iteritems()

    def add(self, item):
        if item in self._d:
            self._d[item] += 1
        else:
            self._d[item] = 1

    def __setitem__(self, key, value):
        assert False

    def __getitem__(self, key):
        return self._d[key]

    def __len__(self):
        _len = 0
        for e in self.iter_entries():
            _len += e[1]
        return _len

    def __hash__(self):
        _hash = 0
        for pair in self.iter_entries():
            _hash ^= hash(pair)
        return _hash

    def __eq__(self, other):
        assert isinstance(other, MultiSet)
        return frozenset(self.iter_entries()) == frozenset(other.iter_entries())

    def __str__(self):
        return "MultiSet" + str(self._d)

    __repr__ = __str__

