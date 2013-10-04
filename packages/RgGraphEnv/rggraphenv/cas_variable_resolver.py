#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dimas'

import swiginac


_vars = dict()


def var(names):
    """
    sympy style "a b c"
    """
    n_vars = []
    names_split = names.split()
    for n in names_split:
        assert len(n) != 0
        v = _vars.get(n, None)
        if v is None:
            v = swiginac.symbol(n)
            _vars[n] = v
        n_vars.append(v)
    return n_vars if len(n_vars) > 1 else n_vars[0]

