#!/usr/bin/python
# -*- coding: utf8

__author__ = 'daddy-bear'

from variable_aware_number import VariableAwareNumber
from ref import Ref, LazyRef
from disjoint_set import DisjointSet
from rg_graph_collections import emptyListDict, zeroDict, emptySetDict, MultiSet, FrozenDict


def swap_pair(pair):
    return pair[1], pair[0]


def dict_hash(a_dict):
    """
    hash from dictionary where key is hashable
    """
    h = 0
    for p in a_dict.iteritems():
        h += hash(p)
    return h