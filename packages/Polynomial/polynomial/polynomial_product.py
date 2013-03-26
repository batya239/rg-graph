#!/usr/bin/python
# -*- coding: utf8

import copy
import eps_number
import formatter
import polynomial
import multiindex
import rggraphutil.variable_aware_number as v_number
from math import factorial
import util


def _preparePolynomials(polynomials):
    pOne = None
    for p in polynomials:
        if p.isZero():
            return list()
        elif p.isOne():
            pOne = p

    filteredPolynomials = filter(lambda p: not p.isOne(), polynomials)

    if pOne is not None and len(filteredPolynomials) == 0:
        return [pOne]
    else:
        return filteredPolynomials


class PolynomialProduct(object):
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
            polyList = filter(lambda _p: _p != p, self.polynomials)
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

        rawAMap = map(lambda p: polynomial.Polynomial(p.monomials, degree=p.degree.a),
                      filter(lambda p: p.degree.a != 0, self.polynomials))
        aPart = PolynomialProduct(rawAMap) if len(rawAMap) else polynomial.PP_ONE

        rawBMap = map(lambda p: polynomial.Polynomial(p.monomials, degree=p.degree.b),
                      filter(lambda p: p.degree.b != 0, self.polynomials))
        bPart = PolynomialProduct(rawBMap) if len(rawBMap) else polynomial.PP_ONE
        epsPolynomial = v_number.VariableAwareNumber.getPolynomialCoefficients(map(lambda p: p.c, self.polynomials))

        mainEpsExpansion = dict()
        for i in xrange(0, toIndex + 1):
            coefficient = []
            for j in xrange(0, len(epsPolynomial)):
                if i - j < 0:
                    continue
                coefficient.append(Logarithm(bPart, float(epsPolynomial[j]) / float(factorial(i - j)), i - j))

            while coefficient[-1].isZero() and len(coefficient) > 1:
                del coefficient[-1]
            mainEpsExpansion[i] = coefficient
        return aPart, mainEpsExpansion

    def changeVarToPolynomial(self, varIndex, polynomial):
        return PolynomialProduct(map(lambda p: p.changeVarToPolynomial(varIndex, polynomial), self.polynomials))

    def calcPower(self, varIndex):
        return reduce(lambda a, p: eps_number.epsNumber(p.calcPower(varIndex)) + a, filter(lambda p: not p.isConst(),
                                                                                           self.polynomials),
                      eps_number.epsNumber(0))

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
        factorDict = util.emptyListDict()
        for p in polynomials:
            key = util.unordered_hashable(tuple(p.monomials.items()))
            factorDict[key].append(p)

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
                else:
                    raise ValueError('invalid merge length %s' % mergeResult)
            nPolynomials.append(mainPolynomial)

        while len(nPolynomials) > 1:
            constPolynomial = None
            for p in nPolynomials:
                if p.isConst() and p.c.isRealNumber():
                    constPolynomial = p
                    break

            if constPolynomial:
                const = constPolynomial.c
                nonConstPolynomial = nPolynomials[0] if nPolynomials[0] != constPolynomial else nPolynomials[1]
                nonConstPolynomial.c *= const
                nPolynomials.remove(constPolynomial)
            else:
                break

        return nPolynomials

    def isOne(self):
        return len(self.polynomials) == 1 and self.polynomials[0].isOne()

    def isZero(self):
        return len(self.polynomials) == 0

    def __neg__(self):
        polynomials = [-self.polynomials[0]] + self.polynomials[1:]
        return PolynomialProduct(polynomials)

    def __mul__(self, other):
        if isinstance(other, PolynomialProduct):
            if self.isZero() or other.isZero():
                return PolynomialProduct([])
            return PolynomialProduct(self.polynomials + other.polynomials)
        elif isinstance(other, v_number.VariableAwareNumber) or isinstance(other, int):
            if self.isZero() or other == 0:
                return PolynomialProduct([])
            if (isinstance(other, int) or other.isRealNumber()) and len(self.polynomials):
                self.polynomials[0] *= other
            return PolynomialProduct(
                self.polynomials + [polynomial.Polynomial({multiindex.MultiIndex(): 1}, c=eps_number.epsNumber(other))])
        elif isinstance(other, polynomial.Polynomial):
            return self * other.toPolyProd()
        else:
            raise NotImplementedError, "multiplication on type (%s) not implemented" % type(other)

    __rmul__ = __mul__

    def __len__(self):
        return len(self.polynomials)

    def __eq__(self, other):
        if isinstance(other, polynomial.Polynomial):
            if other.isZero() and self.isZero():
                return True
            elif len(self.polynomials) == 1:
                return self.polynomials[1] == other
        elif not isinstance(other, PolynomialProduct):
            return False
        copiedSelfPolynomials = copy.copy(self.polynomials)
        for p in other.polynomials:
            if p in copiedSelfPolynomials:
                copiedSelfPolynomials.remove(p)
        return len(copiedSelfPolynomials) == 0

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return formatter.format(self)


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
        return formatter.format(self)

    def isZero(self):
        return not self.c or (self.polynomialProduct.isOne() and self.power != 0)


