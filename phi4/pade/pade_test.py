#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sympy
import FuncDesigner
import openopt


def pade(L, M, tau):
    numerator = 0
    for i in range(1, L + 1):
        coeff = sympy.var('a%s' % i)
        numerator += coeff * tau ** (i )
    denominator = 1
    for i in range(1, M + 1):
        coeff = sympy.var('b%s' % i)
        denominator += coeff * tau ** (i )

    return numerator / denominator


def solvePadeOO(padePoly, seriesDict, N, tau):
    vars = list()
    for atom in padePoly.atoms():
        if isinstance(atom, sympy.Symbol) and atom <> tau:
        #            vars.append(FuncDesigner.oovar(str(atom)))
            exec ('%s=FuncDesigner.oovar("%s")\nvars.append(%s)' % (str(atom), str(atom), str(atom)))
    print vars
    expansion = padePoly.series(tau, 0, N + 1)
    equations = list()
    for power in sorted(seriesDict.keys()):
        if power <= N:
            print "%s==%s" % (str(expansion.coeff(tau, power).evalf()), seriesDict[power])
            equations.append(eval("%s==%s" % (str(expansion.coeff(tau, power).evalf()), seriesDict[power])))
    print equations
    start_point = dict([(x, 0) for x in vars])
    print start_point
    p = openopt.SNLE(tuple(equations), start_point)
    res = p.solve('nssolve')
    return dict(zip(vars, res(*vars)))

#    print sympy.solve_linear(equations[0][0], equations[0][1], vars)
#    xxx = sympy.solve_linear(equations[0][0], equations[0][1], vars)
#    print equations[1].subs(x)


def solvePadeSP(padePoly, seriesDict, N, tau):
    vars = list()
    for atom in padePoly.atoms():
        if isinstance(atom, sympy.Symbol) and atom <> tau:
            vars.append(atom)
    print vars
    expansion = padePoly.series(tau, 0, N + 1)
    equations = list()
    for power in sorted(seriesDict.keys()):
        if power <= N:
            print "%s==%s" % (str(expansion.coeff(tau, power).evalf()), seriesDict[power])
            equations.append(expansion.coeff(tau, power).evalf()-seriesDict[power])
    print equations



tau = sympy.var('tau')

gStar = {1: 1, 2: 0.716173621, 3: 0.095042867, 4: 0.086080396, 5: -0.204139}

b = 0

gStarBorel = dict(map(lambda x: (x,gStar[x]/sympy.gamma(x+b+1).evalf()), gStar))
print gStarBorel

L = 1
M = 3

padeFunc = pade(L, M, tau)
padePoly = padeFunc.series(tau, 0, L + M + 1).removeO()

res = solvePadeOO(padePoly, gStar, L + M, tau)
#res = solvePadeOO(padePoly, gStarBorel, L + M, tau)
print res
#print solvePadeSP(padePoly, gStar, L + M, tau)


padeFunc_ = padeFunc
for var, value in res.iteritems():
    var_= sympy.var(str(var))
    padeFunc_ = padeFunc_.subs(var_, value)

print padeFunc_.subs(tau,1)