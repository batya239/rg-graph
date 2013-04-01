#!/usr/bin/python
# -*- coding: utf8
import collections


_zeroFactory = lambda: 0


def zeroDict(dictionary=None):
    if dictionary is None:
        return collections.defaultdict(_zeroFactory)
    else:
        return collections.defaultdict(_zeroFactory, dictionary)

_emptyListFactory = lambda: []


def emptyListDict():
    return collections.defaultdict(_emptyListFactory)


class UnorderedHashable(object):
    def __init__(self, anIterable):
        self.anIterable = anIterable

    def __eq__(self, other):
        if not isinstance(other, UnorderedHashable):
            return False

        selfAnIterableCopy = list(self.anIterable)
        for e in other.anIterable:
            if e in selfAnIterableCopy:
                selfAnIterableCopy.remove(e)

        return len(selfAnIterableCopy) == 0

    def __repr__(self):
        return repr(self.anIterable)

    def __str__(self):
        return str(self.anIterable)

    def __hash__(self):
        return unordered_hash(self.anIterable)


def unordered_hashable(anIterable):
    return UnorderedHashable(anIterable)


def unordered_hash(iterable):
    h = 0
    for item in iterable:
        h += hash(item)
    return h


def dict_hash1(aDict):
    """
    hash from dictionary where key is hashable
    """
    h = 0
    for p in aDict.iteritems():
        h += hash(p)
    return h


class frozendict(dict):
    def __setitem__(self, key, value):
        raise AssertionError, 'this is immutable dictionary'

    def __hash__(self):
        items = self.items()
        res = hash(items[0])
        for item in items[1:]:
            res ^= hash(item)
        return res

