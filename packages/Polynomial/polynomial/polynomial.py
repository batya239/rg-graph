#!/usr/bin/python
# -*- coding: utf8
"""
immutable Polynomial:

self.degree -- (a, b) --> a + eps*b

self.monomials -- dict of monomials

self.c -- coefficient in front of polynomial

c * (polynomial)^degree

"""
import itertools
import eps_number
import formatter
import polynomial_product
import multiindex
import rggraphutil.variable_aware_number as v_number
from util import dict_hash1, zeroDict


def _prepareMonomials(monomials):
    emptyKeys = set()
    for mi, c in monomials.iteritems():
        if c == 0:
            emptyKeys.add(mi)
    for mi in emptyKeys:
        del monomials[mi]
    return monomials if len(monomials) != 0 else None


class Polynomial:
    def __init__(self, monomials, degree=1, c=1, doPrepare=True):
        """
        monomials -- dictionary MultiIndex->int
        """
        nMonomials = _prepareMonomials(monomials) if doPrepare else monomials
        if nMonomials:
            self.monomials = nMonomials
            self.degree = eps_number.epsNumber(degree)
            self.c = eps_number.epsNumber(c)
        else:
            self.monomials = zeroDict()
            self.degree = eps_number.epsNumber(1)
            self.c = eps_number.epsNumber(0)
        self.hash = None

    def changeDegree(self, newDegree):
        return Polynomial(self.monomials, newDegree, self.c, doPrepare=False)

    def set1toVar(self, varIndex):
        nMonomials = zeroDict()
        for mi, c in self.monomials.items():
            nmi = mi.set1toVar(varIndex)
            nMonomials[nmi] += c
        return Polynomial(nMonomials, self.degree, self.c, doPrepare=False)

    def set0toVar(self, varIndex):
        """
        remove all monomials contains this var
        """
        nMonomials = zeroDict()
        for m in self.monomials.iteritems():
            if not m[0].hasVar(varIndex):
                nMonomials[m[0]] = m[1]
        return Polynomial(nMonomials, self.degree, self.c, doPrepare=False)

    def changeVarToPolynomial(self, varIndex, polynomial):
        """
        polynomial should be Polynomial type
        """
        if polynomial.degree.b <> 0 or polynomial.c.b <> 0 or not isinstance(polynomial.degree.a, int) or polynomial.degree.a < 0:
            raise ValueError, "Complex polynomial not supported now"

        nMonomials = zeroDict()
        for mi, c in self.monomials.items():
            if mi.hasVar(varIndex):
                power = mi.vars[varIndex]
                nPolynomial = polynomial._inPowerOf(power)
                factor = nPolynomial.c
                nMi = mi.set1toVar(varIndex)
                for pMi, pC in nPolynomial.monomials.items():
                    Polynomial._append(nMonomials, pMi * nMi, c * pC * factor)
            else:
                Polynomial._append(nMonomials, mi, c)

        return Polynomial(nMonomials, self.degree, self.c, doPrepare=False)

    @staticmethod
    def _append(monomials, mi, c):
        try:
            monomials[mi] += c
        except TypeError as e:
            print c, type(c), isinstance(c, int)
            raise e


    def _inPowerOf(self, power):
        if self.degree.b <> 0 or self.c.b <> 0 or not isinstance(self.degree.a, int) or self.degree.a < 0:
            raise ValueError, "Complex polynomial not supported"
        nC = self.c.a ** power
        rawMonomials = self.monomials.items()
        nMonomials = zeroDict()
        for product in itertools.product(rawMonomials, repeat=power * self.degree.a):
            mi = multiindex.MultiIndex()
            c = 1
            for pMi, pC in product:
                mi *= pMi
                c *= pC
            Polynomial._append(nMonomials, mi, c)
        return Polynomial(nMonomials, c=nC, doPrepare=False)

    def stretch(self, sVar, varList):
        nMonomials = zeroDict()
        for mi, c in self.monomials.items():
            nmi = mi.stretch(sVar, varList)
            nMonomials[nmi] += c
        return Polynomial(nMonomials, self.degree, self.c, doPrepare=False)

    def diff(self, varIndex):
        """
        return list of polynomials
        """
        nMonomials = zeroDict()
        for mi, c in self.monomials.iteritems():
            if not len(mi):
                continue
            deg, nmi = mi.diff(varIndex)
            if deg != 0:
                nMonomials[nmi] = c * deg

        if not len(nMonomials):
            return [Polynomial(zeroDict(), c=0, doPrepare=False)]

        cMonomials = self.monomials.copy()

        result = list()
        result.append(Polynomial(nMonomials))
        if self.c.isRealNumber():
            result.append(Polynomial(cMonomials, self.degree - 1, self.degree * self.c.a, doPrepare=False))
        else:
            result.append(Polynomial(cMonomials, self.degree - 1, self.c, doPrepare=False))
            const = zeroDict()
            const[multiindex.CONST] = 1
            result.append(Polynomial(const, c=self.degree, doPrepare=False))

        return result

    def calcPower(self, varIndex):
        power = None
        for m in self.monomials:
            curPower = m.getVarPower(varIndex)
            if curPower is None or curPower == 0:
                return 0
            else:
                if power is None:
                    power = curPower
                else:
                    power = min(power, curPower)
        return 0 if power is None else power * self.degree

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

        nMonomials = zeroDict()
        for i in self.monomials.iteritems():
            nMonomials[i[0] - factorMultiIndex] = i[1]

        nPolynomial = Polynomial(nMonomials, degree=self.degree, c=self.c, doPrepare=False)

        result.append(nPolynomial)
        return result

    def changeDegree(self, newDegree):
        return Polynomial(self.monomials, newDegree, self.c, doPrepare=False)

    @staticmethod
    def _merge(p1, p2):
        if p1.c.isRealNumber() or p2.c.isRealNumber():
            degree = p1.degree + p2.degree
            if degree.isRealNumber() and degree.a == 0:
                # (p1.c+p2.c)*(1)^1
                return [Polynomial({multiindex.MultiIndex(): 1}, c=p1.c * p2.c)]
            else:
                return [Polynomial(p1.monomials, degree=p1.degree + p2.degree, c=p1.c * p2.c)]
        else:
            return [Polynomial({multiindex.MultiIndex(): 1}, c=p1.c),
                    Polynomial(p1.monomials, degree=p1.degree + p2.degree, c=p2.c)]

    def __neg__(self):
        return Polynomial(self.monomials, degree=self.degree, c=-self.c, doPrepare=False)

    def __mul__(self, other):
        if isinstance(other, v_number.VariableAwareNumber) and other.isRealNumber():
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
        elif isinstance(_other, v_number.VariableAwareNumber):
            return polynomial_product.PolynomialProduct(
                [self, Polynomial({multiindex.MultiIndex(): 1}, c=eps_number.epsNumber(_other))])
        elif isinstance(_other, int):
            return Polynomial(self.monomials, degree=self.degree, c=self.c * _other, doPrepare=False)

    __rmul__ = __mul__

    def __eq__(self, other):
        if not isinstance(other, Polynomial):
            return False
        return self.monomials == other.monomials and self.degree == other.degree and self.c == other.c

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        if self.hash is None:
            hashCode = dict_hash1(self.monomials)
            hashCode = 31 * hashCode + hash(self.c)
            hashCode = 31 * hashCode + hash(self.degree)
            self.hash = hashCode
        return self.hash

    def __repr__(self):
        return formatter.format(self)


def poly(p, degree=1, c=1):
    monomials = zeroDict()
    for tMonomial in p:
        dMonomial = zeroDict()
        coefficient = tMonomial[0]
        for varIndex in tMonomial[1]:
            dMonomial[varIndex] += 1
        mi = multiindex.MultiIndex(dMonomial)
        monomials[mi] += coefficient
    return Polynomial(monomials, degree, c)

