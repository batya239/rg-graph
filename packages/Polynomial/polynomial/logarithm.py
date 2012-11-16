#!/usr/bin/python
# -*- coding: utf8

"""
immutable LogarithmSum
log \sum (d_i*P_i) --> {P_i -> c_i}
"""

class LogarithmSum:
    def __init__(self, polynomials):
        self.polynomials = polynomials

    def __repr__(self):
        return 'log(%s)' % ''.join(map(lambda p: '%s' % p.__repr__()))
