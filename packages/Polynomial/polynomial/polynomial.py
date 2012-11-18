#!/usr/bin/python
# -*- coding: utf8
"""
immutable Polynomial:

self.degree -- (a, b) --> a + eps*b

self.monomials -- dict of monomials

self.c -- coefficient in front of polynomial

c * (polynomial)^degree

"""
from eps_power import epsPower

class Polynomial:
    def __init__(self, monomials, degree=(1, 0), c=(1, 0)):
        """
        monomials -- dictionary MultiIndex->int
        """
        self.monomials = monomials
        self.degree = epsPower(degree)
        self.c = epsPower(c)

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
        differentiate all monomials and remove zeros from list
        """
        nMonomials = dict()
        for mi in self.monomials.keys():
            deg, nmi = mi.diff(varIndex)
            nMonomials[nmi] = self.monomials[mi] * deg
        nMonomials = dict(filter(lambda m: m[1] <> 0, nMonomials.items()))

        if len(nMonomials) == 0:
            return [Polynomial(dict(), 1, 0)]

        result = list()
        if self.c.isInt():
            result.append(Polynomial(nMonomials, self.degree - 1, self.degree.multiplyOnInt(self.c.a)))
        else:
            result.append(Polynomial(nMonomials, self.degree - 1, self.c))
            result.append(Polynomial(dict(), 1, self.degree))

        return result

    def isZero(self):
        if self.c == 0:
            return True
        isZero = True
        for c in self.monomials.values():
            if c:
                isZero = False
                break
        return isZero

    def __repr__(self):
        if len(self.monomials) == 0:
            if self.c == 0:
                return 'empty polynomial'
            else:
                return '(%s)^(%s)' % (self.c, self.degree)
        internal = '+'.join(map(lambda v: '%s*%s' % (v[1], v[0]), self.monomials.items()))
        return '(%s)(%s)^(%s)' % (self.c, internal, self.degree)

