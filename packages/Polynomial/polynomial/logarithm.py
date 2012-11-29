#!/usr/bin/python
# -*- coding: utf8

"""
logarithm from polynomial product
"""

class LogarithmSum:
    def __init__(self, polynomialProduct):
        self.polynomialProduct = polynomialProduct

    def __repr__(self):
        return 'log(%s)' % self.polynomialProduct
