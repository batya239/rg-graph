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
try:
    import swiginac
    from rggraphenv import symbolic_functions
except:
    pass


def _prepareMonomials(monomials):
    emptyKeys = set()
    for mi, c in monomials.iteritems():
        if c == 0:
            emptyKeys.add(mi)
    for mi in emptyKeys:
        del monomials[mi]
    return monomials if len(monomials) != 0 else None


class Polynomial(object):
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
        self._monomialsWithHash = None

    def asSwiginac(self, varToSwiginacVar):
        deg = self.degree.subs(symbolic_functions.e)
        c = self.c.subs(symbolic_functions.e)
        res = reduce(lambda r, m: r + self.trySimplify(m[1]) * m[0].asSwiginac(varToSwiginacVar), self.monomials.iteritems(), symbolic_functions.CLN_ZERO)
        return c * res ** deg

    @staticmethod
    def trySimplify(value):
        assert "." not in str(value)
        return swiginac.numeric(str(value))

    def integrate(self, varIndex):
        """
        integration of real polynomial (self.degree == 1)
        """
        assert self.degree == 1
        nMonomials = zeroDict()
        for m, c in self.monomials.iteritems():
            nm, degree = m.integrate(varIndex)
            nc = c / float(degree)
            nMonomials[nm] += nc
        return Polynomial(nMonomials, self.degree, self.c, doPrepare=False)

    def getMonomialsWithHash(self):
        if self._monomialsWithHash is None:
            self._monomialsWithHash = MonomialsWithHash(self.monomials)
        return self._monomialsWithHash

    def hasOnlyOneSimpleMonomial(self):
        return len(self.monomials) == 1 and len(self.monomials.items()[0][0]) == 1

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

    def isProportional(self, other_polynomial):
        if self.monomials != other_polynomial.monomials:
            return None
        if self.degree != other_polynomial.degree:
            return None
        if self.c == other_polynomial.c:
            return 1
        return self.c / other_polynomial.c

    def changeVarToPolynomial(self, varIndex, polynomial):
        """
        polynomial should be Polynomial type
        """
        if polynomial.degree.b <> 0 or polynomial.c.b <> 0 or not isinstance(polynomial.degree.a,
                                                                             int) or polynomial.degree.a < 0:
            raise ValueError, "Complex polynomial not supported now"

        nMonomials = zeroDict()
        for mi, c in self.monomials.items():
            if mi.hasVar(varIndex):
                power = mi.vars[varIndex]
                nPolynomial = polynomial._inPowerOf(power)
                assert nPolynomial.c.isRealNumber()
                factor = nPolynomial.c.a
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

    def getIfConstOrNone(self):
        """
        return None if polynomials is not const
        """
        if not self.c.isRealNumber():
            return None
        if self.degree == 0:
            return self.c.a
        if len(self.monomials) == 1 and self.monomials.has_key(multiindex.CONST) and self.degree.isRealNumber():
            return self.c.a * self.monomials[multiindex.CONST] ** self.degree.a
        return None

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

        result = map(lambda i: Polynomial(zeroDict({i[0]: 1}), degree=self.degree * i[1]), factorMultiIndex.split())

        nMonomials = zeroDict()
        for i in self.monomials.iteritems():
            nMonomials[i[0] - factorMultiIndex] = i[1]

        nPolynomial = Polynomial(nMonomials, degree=self.degree, c=self.c, doPrepare=False)

        result.append(nPolynomial)
        return result

    def changeConst(self, newConst):
        return Polynomial(self.monomials, self.degree, newConst, doPrepare=False)

    @staticmethod
    def _merge(p1, p2):
        if p1.isOne():
            return [p2]
        if p2.isOne():
            return [p1]
        if p1.c.isRealNumber() or p2.c.isRealNumber():
            degree = p1.degree + p2.degree
            if degree.isRealNumber() and degree.a == 0:
                # (p1.c+p2.c)*(1)^1
                return [Polynomial(zeroDict({multiindex.MultiIndex(): 1}), c=p1.c * p2.c)]
            else:
                if p1.isConst():
                    return [Polynomial(p2.monomials, degree=p2.degree, c=p1.c * p2.c)]
                elif p2.isConst():
                    return [Polynomial(p1.monomials, degree=p1.degree, c=p1.c * p2.c)]
                else:
                    return [Polynomial(p1.monomials, degree=p1.degree + p2.degree, c=p1.c * p2.c)]
        else:
            if p1.isConst():
                return [Polynomial(zeroDict({multiindex.MultiIndex(): 1}), c=p1.c),
                        Polynomial(p2.monomials, degree=p2.degree, c=p2.c)]
            else:
                return [Polynomial(zeroDict({multiindex.MultiIndex(): 1}), c=p1.c),
                        Polynomial(p1.monomials, degree=p1.degree + p2.degree, c=p2.c)]

    def __neg__(self):
        return Polynomial(self.monomials, degree=self.degree, c=-self.c, doPrepare=False)

    def __add__(self, other):
        return self._doAddOrSub(other, 1)

    def __sub__(self, other):
        return self._doAddOrSub(other, -1)

    def _doAddOrSub(self, other, sign):
        if isinstance(other, Polynomial):
            assert self.degree == 1 and other.degree == 1
            if self.c.isRealNumber() and other.c.isRealNumber():
                return Polynomial._addOrSubCoefficientsIsRealNumber(self, other, sign)
            elif self.c == other.c:
                return Polynomial._addOrSubCoefficientsAreEqual(self, other, sign)
        raise AssertionError

    @staticmethod
    def _addOrSubCoefficientsIsRealNumber(p1, p2, sign):
        nMonomials = zeroDict()
        for m, c in p1.monomials.iteritems():
            nMonomials[m] += c * p1.c
        for m, c in p2.monomials.iteritems():
            nMonomials[m] += c * p2.c * sign
        return Polynomial(nMonomials, degree=1, c=1, doPrepare=True)

    @staticmethod
    def _addOrSubCoefficientsAreEqual(p1, p2, sign):
        nMonomials = zeroDict()
        for m, c in p1.monomials.iteritems():
            nMonomials[m] += c
        for m, c in p2.monomials.iteritems():
            nMonomials[m] += c * sign
        return Polynomial(nMonomials, degree=1, c=p1.c, doPrepare=True)

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
                [self, Polynomial(zeroDict({multiindex.MultiIndex(): 1}), c=eps_number.epsNumber(_other))])
        elif isinstance(_other, (int, float)):
            return Polynomial(self.monomials, degree=self.degree, c=self.c * _other, doPrepare=False)
        else:
            raise NotImplementedError("multiplication of poly with %s not implemented" % type(other))

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

    def __pow__(self, power, modulo=None):
        assert modulo is None
        assert power == -1
        assert self.c.isRealNumber()
        return Polynomial(self.monomials, degree=-self.degree, c=1./self.c.a, doPrepare=False)


class MonomialsWithHash(object):
    def __init__(self, monomials):
        self._monomials = monomials
        self._asPolynomial = None

    def asPolynomial(self):
        if self._asPolynomial is None:
            self._asPolynomial = Polynomial(self._monomials, degree=1, c=1, doPrepare=False)
        return self._asPolynomial

    def isSimple(self):
        return len(self._monomials) == 1

    @property
    def monomials(self):
        return self._monomials

    def __eq__(self, other):
        if not isinstance(other, MonomialsWithHash):
            return False
        return self._monomials == other._monomials

    def __hash__(self):
        return dict_hash1(self.monomials)


P_ONE = Polynomial(zeroDict({multiindex.CONST: 1}), 1, 1)

PP_ONE = P_ONE.toPolyProd()


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

