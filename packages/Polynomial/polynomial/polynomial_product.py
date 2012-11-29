#!/usr/bin/python
# -*- coding: utf8

import copy
from polynomial import Polynomial

def preparePolynomials(polynomials):
    isZero = False
    for p in polynomials:
        if p.isZero():
            isZero = True
            break

    return set() if isZero else polynomials


class PolynomialProduct:
    """
    immutable PolynomialProduct

    self.polynomials -- set of Polynomial
    """

    def __init__(self, polynomials):
        self.polynomials = preparePolynomials(polynomials)

    def set1toVar(self, varIndex):
        return PolynomialProduct(map(lambda p: p.set1toVar(varIndex), self.polynomials))

    def set0toVar(self, varIndex):
        return PolynomialProduct(map(lambda p: p.set0toVar(varIndex), self.polynomials))

    def stretch(self, sVar, varList):
        nPolynomials = []
        for p in self.polynomials:
            nPolynomials.append(p.stretch(sVar, varList))
        return PolynomialProduct(nPolynomials)

    def diff(self, varIndex):
        """
        return set of PolynomialProduct
        """
        result = set()
        for p in self.polynomials:
            polySet = copy.deepcopy(set(filter(lambda _p: _p <> p, self.polynomials)))
            polySet |= set(p.diff(varIndex))
            pp = PolynomialProduct(polySet)
            if not pp.isZero(): result.add(pp)

        return result

    def epsExpansion(self, toIndex):
        """
        return tuple of polynomial product and list (with size = toIndex + 1) of lists of polynomials
        """
        mainPart = PolynomialProduct(map(lambda m: Polynomial(m.monomials, c=m.c), self.polynomials))
        #TODO

    def isZero(self):
        return len(self.polynomials) == 0

    def __repr__(self):
        return "empty polynomial product" if self.isZero() else '*'.join(map(lambda p: '(%s)' % p, self.polynomials))


class Logarithm:
    """
    logarithm from polynomial product
    """

    def __init__(self, polynomialProduct, power=1):
        self.polynomialProduct = polynomialProduct
        self.power = power

    def __repr__(self):
        return '(log^(%s)(%s))' % self.power, self.polynomialProduct


