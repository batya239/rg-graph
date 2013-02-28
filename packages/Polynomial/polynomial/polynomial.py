#!/usr/bin/python
# -*- coding: utf8
"""
immutable Polynomial:

self.degree -- (a, b) --> a + eps*b

self.monomials -- dict of monomials

self.c -- coefficient in front of polynomial

c * (polynomial)^degree

"""
import copy
import itertools
import eps_number
import formatter
import polynomial_product
import multiindex
from util import dict_hash1


def _prepareMonomials(monomials):
    nMonomials = dict((mi, c) for mi, c in monomials.items() if c <> 0)
    return nMonomials if len(nMonomials) <> 0 else None


class Polynomial:
    def __init__(self, monomials, degree=1, c=1):
        """
        monomials -- dictionary MultiIndex->int
        """
        nMonomials = _prepareMonomials(monomials)
        if nMonomials:
            self.monomials = nMonomials
            self.degree = eps_number.epsNumber(degree)
            self.c = eps_number.epsNumber(c)
        else:
            self.monomials = dict()
            self.degree = eps_number.epsNumber(1)
            self.c = eps_number.epsNumber(0)

    def set1toVar(self, varIndex):
        nMonomials = dict()
        for mi, c in self.monomials.items():
            nmi = mi.set1toVar(varIndex)
            if nMonomials.has_key(nmi):
                nMonomials[nmi] += c
            else:
                nMonomials[nmi] = c
        return Polynomial(nMonomials, self.degree, self.c)

    def set0toVar(self, varIndex):
        """
        remove all monomials contains this var
        """
        nMonomials = dict(filter(lambda m: not m[0].hasVar(varIndex), self.monomials.items()))
        return Polynomial(nMonomials, self.degree, self.c)

    def changeVarToPolynomial(self, varIndex, polynomial):
        """
        polynomial should be Polynomial type
        """
        if polynomial.degree.b <> 0 or polynomial.c.b <> 0 or not isinstance(self.degree.a, int) or self.degree.a < 0:
            raise ValueError, "Complex polynomial not supported now"

        nMonomials = dict()
        for mi, c in self.monomials.items():
            if mi.hasVar(varIndex):
                power = mi.vars[varIndex]
                nPolynomial = polynomial._inPowerOf(power)
                factor = nPolynomial.c
                nMi = copy.deepcopy(mi)
                del nMi.vars[varIndex]
                for pMi, pC in nPolynomial.monomials.items():
                    Polynomial._append(nMonomials, pMi * nMi, c * pC * factor)
            else:
                Polynomial._append(nMonomials, mi, c)

        return Polynomial(nMonomials, self.degree, self.c)

    @staticmethod
    def _append(monomials, mi, c):
        if monomials.has_key(mi):
            monomials[mi] += c
        else:
            monomials[mi] = c

    def _inPowerOf(self, power):
        if self.degree.b <> 0 or self.c.b <> 0 or not isinstance(self.degree.a, int) or self.degree.a < 0:
            raise ValueError, "Complex polynomial not supported"
        nC = self.c.a ** power
        rawMonomials = self.monomials.items()
        nMonomials = dict()
        for product in itertools.product(rawMonomials, repeat=power * self.degree.a):
            mi = multiindex.MultiIndex()
            c = 1
            for pMi, pC in product:
                mi *= pMi
                c *= pC
            Polynomial._append(nMonomials, mi, c)
        return Polynomial(nMonomials, c=nC)

    def stretch(self, sVar, varList):
        nMonomials = {}
        for mi, c in self.monomials.items():
            nmi = mi.stretch(sVar, varList)
            if nMonomials.has_key(nmi):
                nMonomials[nmi] += c
            else:
                nMonomials[nmi] = c
        return Polynomial(nMonomials, self.degree, self.c)

    def diff(self, varIndex):
        """
        return list of polynomials
        """
        nMonomials = dict()
        for mi in self.monomials.keys():
            if not len(mi):
                continue
            deg, nmi = mi.diff(varIndex)
            if deg <> 0:
                nMonomials[nmi] = self.monomials[mi] * deg

        if not len(nMonomials):
            return [Polynomial(dict(), c=0)]

        cMonomials = copy.deepcopy(self.monomials)

        result = list()
        result.append(Polynomial(nMonomials))
        if self.c.isRealNumber():
            result.append(Polynomial(cMonomials, self.degree - 1, self.degree * self.c.a))
        else:
            result.append(Polynomial(cMonomials, self.degree - 1, self.c))
            result.append(Polynomial(dict({multiindex.MultiIndex(): 1}), c=self.degree))

        return result

    def isZero(self):
        return self.c == 0

    def isConst(self):
        return (len(self.monomials) == 1 and self.monomials.has_key(multiindex.CONST) and self.monomials[
            multiindex.CONST] == 1) or self.degree == 0

    def isOne(self):
        return self.c == 1 and self.isConst()

    def getVarsIndexes(self):
        return reduce(lambda indexes, mi: indexes | mi.getVarsIndexes(), self.monomials.keys(), set())

    def toPolyProd(self):
        return polynomial_product.PolynomialProduct([self])

    def factorize(self):
        """
        trying to factorize polynomial ang returns tuple of polynomials
        u1 * u2 + u3 * u1 = u1 (u2 + u3)
        """
        multiIndexes = self.monomials.keys()
        factorMultiIndex = reduce(lambda f, mi: multiindex.intersection(mi, f), multiIndexes[1:], multiIndexes[0])

        if not len(factorMultiIndex.vars):
            return [self]

        result = map(lambda i: Polynomial({i[0]: 1}, degree=self.degree * i[1]), factorMultiIndex.split())

        nMonomials = dict(map(lambda i: (i[0] - factorMultiIndex, i[1]), self.monomials.items()))
        nPolynomial = Polynomial(nMonomials, degree=self.degree, c=self.c)

        result.append(nPolynomial)
        return result

    @staticmethod
    def _merge(p1, p2):
        if p1.c.isRealNumber() or p2.c.isRealNumber():
            degree = p1.degree + p2.degree
            if degree.isRealNumber() and degree.a == 0:
                # (p1.c+p2.c)*(1)^1
                return [Polynomial({(): 1}, c=p1.c * p2.c)]
            else:
                return [Polynomial(p1.monomials, degree=p1.degree + p2.degree, c=p1.c * p2.c)]
        else:
            return [Polynomial({multiindex.MultiIndex(): 1}, c=p1.c),
                    Polynomial(p1.monomials, degree=p1.degree + p2.degree, c=p2.c)]

    def __neg__(self):
        return Polynomial(self.monomials, degree=self.degree, c=-self.c)

    def __mul__(self, other):
        if isinstance(other, eps_number.EpsNumber) and other.isRealNumber():
            _other = other.a
        else:
            _other = other

        if isinstance(_other, Polynomial):
            if _other.isZero() or self.isZero():
                return polynomial_product.PolynomialProduct([])
            return polynomial_product.PolynomialProduct([self, _other])
        elif isinstance(_other, polynomial_product.PolynomialProduct):
            if _other.isZero() or self.isZero():
                return polynomial_product.PolynomialProduct([])
            return polynomial_product.PolynomialProduct(_other.polynomials + [self])
        elif isinstance(_other, eps_number.EpsNumber):
            return polynomial_product.PolynomialProduct(
                [self, Polynomial({multiindex.MultiIndex(): 1}, c=eps_number.epsNumber(_other))])
        elif isinstance(_other, int):
            return Polynomial(self.monomials, degree=self.degree, c=self.c * _other)

    __rmul__ = __mul__

    def __eq__(self, other):
        if not isinstance(other, Polynomial):
            return False
        return self.monomials == other.monomials and self.degree == other.degree and self.c == other.c

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        hashCode = dict_hash1(self.monomials)
        hashCode = 31 * hashCode + hash(self.c)
        hashCode = 31 * hashCode + hash(self.degree)
        return hashCode

    def __repr__(self):
        return formatter.format(self)


def poly(p, degree=1, c=1):
    monomials = dict()
    for tMonomial in p:
        dMonomial = dict()
        coefficient = tMonomial[0]
        for varIndex in tMonomial[1]:
            if dMonomial.has_key(varIndex):
                dMonomial[varIndex] += 1
            else:
                dMonomial[varIndex] = 1
        mi = multiindex.MultiIndex(dMonomial)
        if monomials.has_key(mi):
            monomials[mi] += coefficient
        else:
            monomials[mi] = coefficient
    return Polynomial(monomials, degree, c)

