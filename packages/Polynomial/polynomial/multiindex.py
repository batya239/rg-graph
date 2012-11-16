#!/usr/bin/python
# -*- coding: utf8
"""
immutable MultiIndex, represent by dictionary
ex: (3, 0, 1) --> x_1^3 * x_3 -->  {1: 3, 3: 1}
"""
import copy

class MultiIndex:
    def __init__(self, vars=dict()):
        """self.vars -- dictionary {variable index --> variable power}
        """
        self.vars = vars

    def hasVar(self, varIndex):
        return self.vars[varIndex]

    def set1toVar(self, varIndex):
        nVars = copy.copy(self.vars)
        if nVars[varIndex]:
            del nVars[varIndex]
        return MultiIndex(nVars)
            
    def diff(self,  varIndex):
        """
        decrease power of varIndex if exist and returns old power
        """
        deg = self.vars[varIndex]
        if deg:
            nVars = copy.copy(self.vars)
            nVars[varIndex] -= deg - 1
            return deg, MultiIndex(nVars)
        else:
            return 0, MultiIndex

    def stretch(self, sVar, varList):
        deltaDegree = 0
        nVars = copy.copy(self.vars)
        for v in varList:
            if nVars[v]:
                deltaDegree += nVars[v]
        deg = nVars[sVar]
        if deg:
            nVars[sVar] = deg + deltaDegree
        elif deltaDegree:
            nVars[sVar] = deltaDegree
        return MultiIndex(nVars)

    #
    # to collect this in dict
    #
    def __eq__(self, other):
        return self.vars == other.vars

    def __hash__(self):
        return self.vars.__hash__

    def __repr__(self):
        return ''.join(map(lambda v: '*x_{%s}^%s' % (v[0], v[1]), self.vars.items()))


