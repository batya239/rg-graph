#!/usr/bin/python
# -*- coding: utf8

import copy
import eps_number
import formatter
import polynomial
import multiindex
from math import factorial

def _preparePolynomials(polynomials):
    for p in polynomials:
        if p.isZero():
            return list()

    return filter(lambda p: not p.isOne(), polynomials)

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

        aPart = PolynomialProduct(map(lambda p: polynomial.Polynomial(p.monomials, degree=p.degree.a),
                                      filter(lambda p: p.degree.a <> 0, self.polynomials)))

        bPart = PolynomialProduct(map(lambda p: polynomial.Polynomial(p.monomials, degree=p.degree.b),
                                      filter(lambda p: p.degree.b <> 0, self.polynomials)))

        epsPolynomial = eps_number.getCoefficients(map(lambda p: p.c, self.polynomials))

        mainEpsExpansion = dict()
        for i in xrange(0, toIndex + 1):
            coefficient = []
            for j in xrange(0, len(epsPolynomial)):
                if i - j < 0:
                    continue
                coefficient.append(Logarithm(bPart, float(epsPolynomial[j]) / float(factorial(i - j)), i - j))
            mainEpsExpansion[i] = coefficient
        return aPart, mainEpsExpansion

    def changeVarToPolynomial(self, varIndex, polynomial):
        return PolynomialProduct(map(lambda p: p.changeVarToPolynomial(varIndex, polynomial), self.polynomials))

    def simplify(self):
        """
        trying to simplifying product by polynomials factorization
        """
        rawPolynomials = list()
        for p in self.polynomials:
            rawPolynomials += p.factorize()
        return PolynomialProduct(PolynomialProduct._simplify(rawPolynomials))

    @staticmethod
    def _simplify(polynomials):
        """
        collecting polynomials by monomial part
        """
        factorDict = dict()
        for p in polynomials:
            key = tuple(p.monomials)
            if factorDict.has_key(key):
                factorDict[key].append(p)
            else:
                factorDict[key] = [p]

        nPolynomials = []
        for polyList in factorDict.values():
            mainPolynomial = polyList[0]
            for p in polyList[1:]:
                mergeResult = polynomial.Polynomial._merge(mainPolynomial, p)
                if len(mergeResult) == 1:
                    mainPolynomial = mergeResult[0]
                elif len(mergeResult) == 2:
                    mainPolynomial = mergeResult[1]
                    nPolynomials.append(mergeResult[0])
                else: raise ValueError, 'invalid merge length %s' % mergeResult
            nPolynomials.append(mainPolynomial)


        return nPolynomials

    def isZero(self):
        return len(self.polynomials) == 0

    def __mul__(self, other):
        if isinstance(other, PolynomialProduct):
            return PolynomialProduct(self.polynomials + other.polynomials)
        elif isinstance(other, eps_number.EpsNumber) or isinstance(other, int):
            return PolynomialProduct(self.polynomials + [polynomial.Polynomial({multiindex.MultiIndex(): 1}, c=eps_number.epsNumber(other))])

    __rmul__ = __mul__

    def __repr__(self):
        return formatter.formatRepr(self)


def poly_prod(polynomials):
    return PolynomialProduct(polynomials)


class Logarithm:
    """
    logarithm from polynomial product.
    In real we use this only for formatting out
    """

    def __init__(self, polynomialProduct, c=1, power=1):
        self.polynomialProduct = polynomialProduct
        self.power = power
        self.c = c

    def __repr__(self):
        return formatter.formatRepr(self)


