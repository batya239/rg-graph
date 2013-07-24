#!/usr/bin/python
# -*- coding: utf8
"""
immutable MultiIndex, represent by dictionary
ex: (3, 0, 1) --> x_1^3 * x_3 -->  {1: 3, 3: 1}
"""
from util import dict_hash1, zeroDict


def _prepareVars(_vars):
    #if isinstance(_vars, dict):
    #    __vars = zeroDict(_vars)
    #else:
    #    __vars = _vars
    emptyKeys = set()
    for k, v in _vars.iteritems():
        if v == 0:
            emptyKeys.add(k)
    for k in emptyKeys:
        del _vars[k]

    return _vars

class MultiIndex:
    def __init__(self, _vars=zeroDict(), doPrepare=True):
        """self.vars -- dictionary {variable index --> variable power}
        """
        self.vars = _prepareVars(_vars) if doPrepare else _vars
        self.hash = None

    def hasVar(self, varIndex):
        return self.vars.has_key(varIndex)

    def set1toVar(self, varIndex):
        if varIndex in self.vars:
            nVars = zeroDict()
            for k, v in self.vars.iteritems():
                if k != varIndex:
                    nVars[k] = v
            return MultiIndex(nVars, doPrepare=False)
        else:
            return self

    def integrate(self, varIndex):
        nVars = self.vars.copy()
        lastDegree = nVars[varIndex]
        nVars[varIndex] = lastDegree + 1
        return MultiIndex(nVars, doPrepare=False), 1 if lastDegree is 0 else lastDegree

    def diff(self, varIndex):
        """
        decrease power of varIndex if exist and returns old power
        """
        deg = self.vars.get(varIndex, None)
        if deg:
            nVars = self.vars.copy()
            if deg == 1:
                del nVars[varIndex]
            else:
                nVars[varIndex] -= 1
            return deg, MultiIndex(nVars, doPrepare=False)
        else:
            return 0, CONST

    def getVarPower(self, varIndex):
        return self.vars.get(varIndex, None)

    def stretch(self, sVar, varList):
        deltaDegree = 0
        for v in varList:
            deltaDegree += self.vars.get(v, 0)
        if deltaDegree != 0:
            nVars = self.vars.copy()
            nVars[sVar] += deltaDegree
            return MultiIndex(nVars, doPrepare=False)
        return self

    def getVarsIndexes(self):
        indexes = set()
        map(lambda v: indexes.add(v), self.vars.keys())
        return indexes

    def split(self):
        return map(lambda i: (MultiIndex(zeroDict({i[0]: 1})), i[1]), self.vars.items())

    def __mul__(self, other):
        nVars = self.vars.copy()
        for v, p in other.vars.items():
            nVars[v] += p
        return MultiIndex(nVars, doPrepare=False)

    def __sub__(self, other):
        result = zeroDict()
        for k, v in self.vars.items():
            result[k] = v - (other.vars[k] if other.vars.has_key(k) else 0)
        return MultiIndex(result)

    def __len__(self):
        return len(self.vars)

    def __eq__(self, other):
        if not isinstance(other, MultiIndex):
            return False
        return self.vars == other.vars

    def __hash__(self):
        if self.hash is None:
            self.hash = dict_hash1(self.vars)
        return self.hash

    def __repr__(self):
        if len(self.vars) == 0:
            return '1'
        else:
            return '*'.join(map(lambda v: 'x_%s^%s' % (v[0], v[1]) if v[1] <> 1 else 'x_%s' % v[0], self.vars.items()))


CONST = MultiIndex()


def intersection(mi1, mi2):
    """
    finding intersection two dictionaries where values is numbers
    """
    result = zeroDict()
    for k, v in mi1.vars.items():
        if mi2.vars.has_key(k):
            result[k] = min(v, mi2.vars[k])
    return MultiIndex(result)




