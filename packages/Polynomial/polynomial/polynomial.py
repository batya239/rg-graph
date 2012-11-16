#!/usr/bin/python
# -*- coding: utf8
"""
immutable Polynomial:

self.degree -- (a, b) --> a + eps*b

self.monomials -- list of monomials

self.c -- coefficient in front of polynomial

c * (polynomial)^degree

"""
from packages.polymonial.eps_power import epsPower

def _factorize(monomials):
    """
    groups elements by MultiIndex
    """
    nMonomials = dict()
    for mi, c in monomials.items():
        if nMonomials[mi]:
            nMonomials[mi] = c
        else:
            nMonomials[mi] += c

class Polynomial:
    def __init__(self, monomials, degree=(1, 0), c=(1, 0)):
        """
        monomials -- dictionary MultiIndex->int
        """
        self.monomials = _factorize(monomials)
        self.degree = epsPower(degree)
        self.c = c

    def set1toVar(self, varIndex):
        nMonomials = {}
        for mi, c in self.monomials.items():
            nmi = mi.set1toVar(varIndex)
            if nMonomials[nmi]:
                nMonomials[nmi] += c
            else:
                nMonomials[nmi] = c
        return Polynomial(nMonomials, self.degree, self.c)

    def set0toVar(self, varIndex):
        """
        remove all monomials contains this var
        """
        nMonomials = filter(lambda m: not m.hasVar(varIndex), self.monomials.keys())
        return Polynomial(nMonomials, self.degree, self.c)

    def stretch(self, sVar, varList):
        nMonomials = {}
        for mi, c in self.monomials.items():
            nmi = mi.stretch(sVar, varList)
            if nMonomials[nmi]:
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

        nMonomials = dict(filter(lambda mi, c: c <> 0, nMonomials.items()))
        return Polynomial(nMonomials, self.degree, self.c)

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
        internal = '+'.join(map(lambda v: '%s*%s' % (v[1], v[0]), self.monomials.items()))
        return '(%s)^(%s)' % (internal, self.degree)

