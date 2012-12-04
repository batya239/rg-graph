#!/usr/bin/python
# -*- coding: utf8
"""
immutable MultiIndex, represent by dictionary
ex: (3, 0, 1) --> x_1^3 * x_3 -->  {1: 3, 3: 1}
"""
import copy
from util import dict_hash1

def formatVar(var):
    return 'u%s' % var if isinstance(var, int) else str(var)


def _prepareVars(vars):
    return dict((v, p) for v, p in vars.items() if p <> 0)

class MultiIndex:
    def __init__(self, vars=dict()):
        """self.vars -- dictionary {variable index --> variable power}
        """
        self.vars = _prepareVars(vars)

    def hasVar(self, varIndex):
        return self.vars.has_key(varIndex)

    def set1toVar(self, varIndex):
        nVars = copy.copy(self.vars)
        if nVars.has_key(varIndex):
            del nVars[varIndex]
        return MultiIndex(nVars)

    def diff(self, varIndex):
        """
        decrease power of varIndex if exist and returns old power
        """
        if self.vars.has_key(varIndex):
            deg = self.vars[varIndex]
            nVars = copy.copy(self.vars)
            if deg == 1:
                del nVars[varIndex]
            else: nVars[varIndex] -= 1
            return deg, MultiIndex(nVars)
        else:
            return 0, MultiIndex()

    def stretch(self, sVar, varList):
        deltaDegree = 0
        nVars = copy.copy(self.vars)
        for v in varList:
            if nVars.has_key(v):
                deltaDegree += nVars[v]
        if nVars.has_key(sVar):
            deg = nVars[sVar]
            nVars[sVar] = deg + deltaDegree
        elif deltaDegree:
            nVars[sVar] = deltaDegree
        return MultiIndex(nVars)

    def getVarsIndexes(self):
        indexes = set()
        map(lambda v: indexes.add(formatVar(v)), self.vars.keys())
        return indexes

    def __sub__(self, other):
        result = dict()
        for k, v in self.vars.items():
            result[k] = v - (other.vars[k] if other.vars.has_key(k) else 0)
        return MultiIndex(result)

    def __len__(self):
        return len(self.vars)

    def __eq__(self, other):
        return self.vars == other.vars

    def __hash__(self):
        return dict_hash1(self.vars)

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
    result = dict()
    for k, v in mi1.vars.items():
        if mi2.vars.has_key(k):
            result[k] = min(v, mi2.vars[k])
    return MultiIndex(result)




