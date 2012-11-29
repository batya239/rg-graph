#!/usr/bin/python
# -*- coding: utf8

import copy
from math import factorial
from eps_power import getCoefficients
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
        toIndex includes,
        return tuple of polynomial product and list (with size = toIndex + 1) of lists of polynomials
        """
        if self.isZero():
            return None

        cPart = PolynomialProduct(map(lambda m: Polynomial(m.monomials, c=m.c), self.polynomials))

        dPart = PolynomialProduct(map(lambda m: Polynomial(m.monomials, c=m.c), self.polynomials))

        epsPolynomial = getCoefficients(map(lambda p: p.c, self.polynomials))

        mainEpsExpansion = dict()
        if len(epsPolynomial) == 1 and epsPolynomial[0].isInt():
            pass
        else:
            for i in xrange(0, toIndex + 1):
                coefficient = []
                for j in xrange(0, len(epsPolynomial)):
                    if i - j < 0:
                        continue
                    coefficient.append(Logarithm(dPart, epsPolynomial[j] / factorial(i), j))
                mainEpsExpansion[i] = coefficient
        return cPart, mainEpsExpansion

    def isZero(self):
        return len(self.polynomials) == 0

    def __repr__(self):
        return "empty polynomial product" if self.isZero() else '*'.join(map(lambda p: '(%s)' % p, self.polynomials))


class Logarithm:
    """
    logarithm from polynomial product
    """
    def __init__(self, polynomialProduct, c=1, power=1):
        self.polynomialProduct = polynomialProduct
        self.power = power
        self.c = c

    def __repr__(self):
        return '(%s*log^(%s)(%s))' % (self.c, self.power, self.polynomialProduct) if self.power else '(%s)' % self.c


