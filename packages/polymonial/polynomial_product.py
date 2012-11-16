#!/usr/bin/python
# -*- coding: utf8
"""
immutable PolynomialProduct

self.polynomials -- set of Polynomial
"""
import copy
from phi4.graphs.methods.poly_tools import Polynomial

class PolynomialProduct:

    def __init__(self, polynomials):
        self.polynomials = polynomials

    def set1toVar(self, varIndex):
        return PolynomialProduct(map(lambda p: p.set1toVar(varIndex), self.polynomials))

    def set0toVar(self, varIndex):
        return PolynomialProduct(filter(lambda p: not p.isZero(), map(lambda p: not p.set0toVar(varIndex), self.polynomials)))

    def stretch(self, sVar, varList):
        nPolynomials= []
        for p in self.polynomials:
            nPolynomials.append(p.stretch(sVar, varList))
        return PolynomialProduct(nPolynomials)

    def diff(self, varIndex):
        """
        return set of PolynomialProduct
        """
        result = set()
        for p in self.polynomials:
            polySet = copy.deepcopy(self.polynomials)
            polySet.remove(p)
            polySet.add(p.diff(varIndex))
            result.add(PolynomialProduct(polySet))

        return result

    def epsExpansion(self, toIndex):
        """
        return tuple of polynomial product and list (with size = toIndex + 1) of lists of polynomials
        """
        mainPart = PolynomialProduct(map(lambda m: Polynomial(m.monomials, m.degree.a, m.c), self.polynomials))
        #TODO


    def __repr__(self):
        internal = '+'.join(map(lambda v: '%s*%s' % (v[1], v[0]), self.monomials.items()))
        return '(%s)^(%s)' % (internal, self.degree)

