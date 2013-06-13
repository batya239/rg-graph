#!/usr/bin/python
# -*- coding: utf8
import collections

__author__ = 'daddy-bear'

_emptyListFactory = lambda: []


def emptyListDict():
    return collections.defaultdict(_emptyListFactory)