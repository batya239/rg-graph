#!/usr/bin/python
# -*- coding: utf8


def dict_hash1(dict):
    """
    hash from dictionary where key is hashable
    """
    h = 0
    for p in dict.items():
        h += hash(p)
    return h

def dict_hash2(dict):
    """
    hash from dictionary where key is dictionary too
    """
    h = 0
    for p in dict.items():
        h += dict_hash1(p[0]) + 31 * hash(p[1])
    return h


def dict_intersection(dict1, dict2):
    """
    finding intersection two dictionaries where values is numbers
    """
    result = dict()
    for k, v in dict1.items():
        if dict2.has_key(k):
            result[k] = min(v, dict2[k])
    return result

def dict_subtraction(dict1, dict2):
    """
    dict1 - dict2 where values is numbers
    """
    result = dict()
    for k, v in dict1.items():
        result[k] = v - (dict2[k] if dict2.has_key(k) else 0)
    return result

class frozendict(dict):
    def __setitem__(self, key, value):
        raise AssertionError, 'this is immutable dictionary'

    def __hash__(self):
        items = self.items()
        res = hash(items[0])
        for item in items[1:]:
            res ^= hash(item)
        return res

