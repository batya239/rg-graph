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
from eps_power import epsNumber
from multiindex import MultiIndex
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
            self.degree = epsNumber(degree)
            self.c = epsNumber(c)
        else:
            self.monomials = dict()
            self.degree = epsNumber(1)
            self.c = epsNumber(0)


    def set1toVar(self, varIndex):
        nMonomials = {}
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
            return [Polynomial(dict(), 1, 0)]

        cMonomials = copy.deepcopy(self.monomials)

        result = list()
        result.append(Polynomial(nMonomials))
        if self.c.isInt():
            result.append(Polynomial(cMonomials, self.degree - 1, self.degree * self.c.a))
        else:
            result.append(Polynomial(cMonomials, self.degree - 1, self.c))
            result.append(Polynomial(dict({MultiIndex(): 1}), 1, self.degree))

        return result

    def isZero(self):
        return self.c == 0

    def __eq__(self, other):
        return self.monomials == other.monomials and self.degree == other.degree and self.c == other.c

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        hashCode = dict_hash1(self.monomials)
        hashCode = 31 * hashCode + hash(self.c)
        hashCode = 31 * hashCode + hash(self.degree)
        return hashCode

    def __repr__(self):
        if self.c == 0:
            return '0'
        internal = '+'.join(map(lambda v: '%s*%s' % (v[1], v[0]), self.monomials.items()))
        if self.c == 1:
            if self.degree == 0:
                return "1"
            elif self.degree == 1:
                return  '(%s)' % internal
            else:
                return  '(%s)^(%s)' % (internal, self.degree)
        else:
            return '(%s)*(%s)^(%s)' % (self.c, internal, self.degree)


def polynomial(p, degree=1, c=1):
    monomials = dict()
    for tMonomial in p:
        dMonomial = dict()
        coefficient = tMonomial[0]
        for varIndex in tMonomial[1]:
            if dMonomial.has_key(varIndex):
                dMonomial[varIndex] += 1
            else:
                dMonomial[varIndex] = 1
        mi = MultiIndex(dMonomial)
        if monomials.has_key(mi):
            monomials[mi] += coefficient
        else:
            monomials[mi] = coefficient
    return Polynomial(monomials, degree, c)
