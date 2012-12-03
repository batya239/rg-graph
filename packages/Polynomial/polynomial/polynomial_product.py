#!/usr/bin/python
# -*- coding: utf8

import copy
from math import factorial
from eps_number import getCoefficients
from polynomial import Polynomial
import formatter

def _preparePolynomials(polynomials):
    isZero = False
    for p in polynomials:
        if p.isZero():
            isZero = True
            break

    return list() if isZero else polynomials


class PolynomialProduct:
    """
    immutable PolynomialProduct

    self.polynomials -- list of Polynomial
    """

    def __init__(self, polynomials):
        self.polynomials = _preparePolynomials(polynomials)

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
        result = list()
        for p in self.polynomials:
            polyList = copy.deepcopy(filter(lambda _p: _p <> p, self.polynomials))
            polyList += p.diff(varIndex)
            pp = PolynomialProduct(polyList)
            if not pp.isZero(): result.append(pp)

        return result

    def getVarsIndexes(self):
        return reduce(lambda indexes, p: indexes | p.getVarsIndexes(), self.polynomials, set())

    def epsExpansion(self, toIndex):
        """
        toIndex includes,
        return tuple of polynomial product and list (with size = toIndex + 1) of lists of polynomials
        """
        if self.isZero():
            return None

        aPart = PolynomialProduct(map(lambda m: Polynomial(m.monomials, c=m.degree.a), self.polynomials))

        bPart = PolynomialProduct(map(lambda m: Polynomial(m.monomials, c=m.degree.b), self.polynomials))

        epsPolynomial = getCoefficients(map(lambda p: p.c, self.polynomials))

        mainEpsExpansion = dict()
        for i in xrange(0, toIndex + 1):
            coefficient = []
            for j in xrange(0, len(epsPolynomial)):
                if i - j < 0:
                    continue
                coefficient.append(Logarithm(bPart, epsPolynomial[j] / factorial(i), i))
            mainEpsExpansion[i] = coefficient
        return aPart, mainEpsExpansion

    def isZero(self):
        return len(self.polynomials) == 0

    def __repr__(self):
        return formatter.formatRepr(self)


def poly_prod(polynomials):
    return PolynomialProduct(polynomials)

class Logarithm:
    """
    logarithm from polynomial product
    """
    def __init__(self, polynomialProduct, c=1, power=1):
        self.polynomialProduct = polynomialProduct
        self.power = power
        self.c = c

    def __repr__(self):
        return formatter.formatRepr(self)


