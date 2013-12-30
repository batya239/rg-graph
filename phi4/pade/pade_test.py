#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sympy


def pade_aproximant(L, M, tau):
    numerator = 0
    for i in range(0, L + 1):
        coeff = sympy.var('a%s' % i)
        numerator += coeff * tau ** (i )
    denominator = 1
    for i in range(1, M + 1):
        coeff = sympy.var('b%s' % i)
        denominator += coeff * tau ** (i )

    return numerator, denominator



def dict2poly(series_dict, var):
    res = 0
    for power, coeff in series_dict.iteritems():
        res += var**power * coeff
    return res


def eqs2matrix(eqs, vars):
    matrix_list=list()
    for eq in eqs:
        row = list()
        const = eq
        for var in vars:
            row.append(eq.coeff(var, 1))
            const = const.subs(var, 0)
#        print "const", const
        row.append(-const)
        matrix_list.append(row)
    return sympy.Matrix(matrix_list)


def solve_pade_sympy(pade_num, pade_denom, series_dict, n, tau):
    vars = list()
    atoms = set()
    for poly in (pade_num, pade_denom):
        try:
            atoms = atoms | poly.atoms()
        except:
            pass
    for atom in atoms:
        if isinstance(atom, sympy.Symbol) and atom <> tau:
            vars.append(atom)
    series_poly = dict2poly(series_dict, tau)
    eq = (pade_num-pade_denom*series_poly).expand()
    eqs = list()
    for i in range(n+1):
        eqs.append(eq.coeff(tau, i))
    return sympy.solve_linear_system(eqs2matrix(eqs, vars), *vars)


def borel_transform(series_dict, b=0):
    return dict(map(lambda x: (x, series_dict[x]/sympy.gamma(x+b+1).evalf()), series_dict))


def resummation_pade(L,M, series_dict):
    tau = sympy.var('tau')
    padeNum, padeDenom = pade_aproximant(L, M, tau)
    padeFunc = padeNum/padeDenom
    res = solve_pade_sympy(padeNum, padeDenom, series_dict, L + M, tau)
#    print res
    padeFunc_ = padeFunc
    for var, value in res.iteritems():
        var_ = sympy.var(str(var))
        padeFunc_ = padeFunc_.subs(var_, value)

    return padeFunc_.subs(tau,1)

gStar = {1: 1, 2: 0.716173621, 3: 0.095042867, 4: 0.086080396, 5: -0.204139}

gamma_minus = {0: 1, 1: -1./3, 2: -0.113701246, 3: 0.024940678, 4: -0.039896059, 5: 0.0645212}

nu_minus = {0: 2, 1: -2./3, 2: -0.2613686, 3: 0.0145746, 4: -0.0913127, 5: 0.118121}

#b = 0
#gStarBorel = borel_transform(gStar, b=0)
#print gStarBorel

N = 5
print "\ngStar\n"
for M in range(0, N):
    for L in range(1, N-M+1):
#        print M, L,
        print "%10.4f" % (resummation_pade(L, M, gStar)),
    print

print "\ngamma^-1\n"
for M in range(0, N+1):
    for L in range(0, N-M+1):
#        print M, L,
        print "%10.4f" % (1/resummation_pade(L, M, gamma_minus)),
    print

print "\nnu^-1\n"
for M in range(0, N+1):
    for L in range(0, N-M+1):
#        print M, L,
        print "%10.4f" % (1/resummation_pade(L, M, nu_minus)),
    print
