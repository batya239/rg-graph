#!/usr/bin/python
# -*- coding: utf8


def dict_hash1(dict):
    """
    hash from dictionary where key is hashable
    """
    hash = 0
    for p in dict.items():
        hash += p.__hash__()
    return hash

def dict_hash2(dict):
    """
    hash from dictionary where key is dictionary too
    """
    hash = 0
    for p in dict.items():
        hash += dict_hash1(p[0]) + 31 * p[2].__hash__()
    return hash