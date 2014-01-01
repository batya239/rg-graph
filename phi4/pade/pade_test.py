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
        res += var ** power * coeff
    return res


def eqs2matrix(eqs, vars):
    matrix_list = list()
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
    eq = (pade_num - pade_denom * series_poly).expand()
    eqs = list()
    for i in range(n + 1):
        eqs.append(eq.coeff(tau, i))
    return sympy.solve_linear_system(eqs2matrix(eqs, vars), *vars)


def borel_transform(series_dict, b=0):
    return dict(map(lambda x: (x, series_dict[x] / sympy.gamma(x + b + 1).evalf()), series_dict))


def resummation_pade(L, M, series_dict):
    tau = sympy.var('tau')
    padeNum, padeDenom = pade_aproximant(L, M, tau)
    padeFunc = padeNum / padeDenom
    res = solve_pade_sympy(padeNum, padeDenom, series_dict, L + M, tau)
    #    print res
    padeFunc_ = padeFunc
    for var, value in res.iteritems():
        var_ = sympy.var(str(var))
        padeFunc_ = padeFunc_.subs(var_, value)

    return padeFunc_.subs(tau, 1)

func_template = """

def func(tau,arg):
    from pygsl import _numobj as numx
    res = numx.exp(-tau) * ({pade})
    return res
"""

from pygsl import integrate
def resummation_pade_borel(L, M, series_dict, b=0):
    tau = sympy.var('tau')
    borel_dict = borel_transform(series_dict, b=b)
    padeNum, padeDenom = pade_aproximant(L, M, tau)
    padeFunc = padeNum / padeDenom
    res = solve_pade_sympy(padeNum, padeDenom, borel_dict, L + M, tau)
    #    print res
    padeFunc_ = padeFunc
    for var, value in res.iteritems():
        var_ = sympy.var(str(var))
        padeFunc_ = padeFunc_.subs(var_, value)


#    print func_template.format(pade=padeFunc_)
    exec(func_template.format(pade=padeFunc_))
    gfunc = integrate.gsl_function(func, None)
    w = integrate.workspace(1000000)
    try:
        flag, result, error = integrate.qagiu(gfunc, 0, 1e-12, 1e-12, 100000, w)
        return result
    except:
        return None
    #flag, result, error = integrate.qagiu(gfunc, 0, 1e-12, 1e-12, 100000, w)
    #return result


gStar_05 = {1: 1, 2: 0.716173621, 3: 0.095042867, 4: 0.086080396, 5: -0.204139}
gamma_minus_05 = {0: 1, 1: -1. / 3, 2: -0.113701246, 3: 0.024940678, 4: -0.039896059, 5: 0.0645212}
nu_minus_05 = {0: 2, 1: -2. / 3, 2: -0.2613686, 3: 0.0145746, 4: -0.0913127, 5: 0.118121}


#13
#n=1
gamma_13_n1 = {0: 1, 1: 1. / 3, 2: 0.224812357, 3: 0.087897190, 4: 0.086443008, 5: -0.0180209}
gamma_13_n1_minus = {0: 1, 1: -1. / 3, 2: -0.113701246, 3: 0.024940678, 4: -0.039896059, 5: 0.0645210}
nu_13_n1 = {0: 1./2, 1: 1. / 6, 2: 0.120897626, 3: 0.0584361287, 4: 0.056891652, 5: 0.00379868}
nu_13_n1_minus = {0: 2., 1: -2. / 3, 2: -0.261368281, 3: 0.0145750797, 4: -0.091312521, 5: 0.118121}
eta_13_n1 = {0: 0., 1: 0., 2: 0.0339661470, 3: 0.0466287623, 4: 0.030925471, 5: 0.0256843}

#n=0
gamma_13_n0 = {0: 1, 1: 1. / 4, 2: 0.143242270, 3: 0.018272597, 4: 0.035251118, 5: -0.0634415}
gamma_13_n0_minus = {0: 1, 1: -1. / 4, 2: -0.08742270, 3: 0.037723538, 4: -0.028548147, 5: 0.0754631}
nu_13_n0 = {0: 1./2, 1: 1. / 8, 2: 0.0787857831, 3: 0.0211750671, 4: 0.028101050, 5: -0.0222040}
nu_13_n0_minus = {0: 2., 1: -1. / 2, 2: -0.190143132, 3: 0.0416216976, 4: -0.071673308, 5: 0.136330}
eta_13_n0 = {0: 0., 1: 0., 2: 0.0286589366, 3: 0.0409908542, 4: 0.027138940, 5: 0.0236106}

#n=-1
gamma_13_nm1 = {0: 1, 1: 1. / 7, 2: 0.060380873, 3: -0.023532210, 4: 0.012034268, 5: -0.0638772}
gamma_13_nm1_minus = {0: 1, 1: -1. / 7, 2: -0.039972710, 3: 0.03786436, 4: -0.018392201, 5: 0.0649966}
nu_13_nm1 = {0: 1./2, 1: 1. / 14, 2: 0.0348693698, 3: -0.00424514372, 4: 0.011608435, 5: -0.0268913}
nu_13_nm1_minus = {0: 2., 1: -2. / 7, 2: -0.0986611527, 3: 0.0510003794, 4: -0.049264800, 5: 0.116842}
eta_13_nm1 = {0: 0., 1: 0., 2: 0.0187160402, 3: 0.0274103364, 4: 0.017144702, 5: 0.0159901}


#b = 0
#gStarBorel = borel_transform(gStar, b=0)
#print gStarBorel

N = 5
print "\ngStar\n"
for M in range(0, N):
    for L in range(1, N - M + 1):
    #        print M, L,
        print "%10.4f" % (resummation_pade(L, M, gStar_05)),
    print

print "\ngamma^-1\n"
for M in range(0, N + 1):
    for L in range(0, N - M + 1):
    #        print M, L,
        print "%10.4f" % (1 / resummation_pade(L, M, gamma_minus_05)),
    print

print "\nnu^-1\n"
for M in range(0, N + 1):
    for L in range(0, N - M + 1):
    #        print M, L,
        print "%10.4f" % (1 / resummation_pade(L, M, nu_minus_05)),
    print

tau = sympy.var('tau')

print 2013
print "n=1"
print "gamma"
print "DS", dict2poly(gamma_13_n1, tau).subs(tau,1)
print "DS-1", 1/dict2poly(gamma_13_n1_minus, tau).subs(tau,1)

print "Pade"
for M in range(0, N + 1):
    for L in range(0, N - M + 1):
    #        print M, L,
        print "%10.4f" % (resummation_pade(L, M, gamma_13_n1)),
    print

print "Pade-Borel"
#for L, M  in [(1,4), (3,2), (4,1)]:
#    print (L,M), resummation_pade_borel(L, M, gamma_13_n1)

for M in range(0, N + 1):
    for L in range(0, N - M + 1):
    #        print M, L,
        #FIXME : unknown exception
        try:
            res = resummation_pade_borel(L, M, gamma_13_n1)
        except:
            res = "    Except"
        if res is None:
            print "      None",
        elif isinstance(res, str):
            print res,
        else:
            print "%10.4f" % (res),
    print

print "Pade-Borel-1"
print (2, 3), 1/resummation_pade_borel(2, 3, gamma_13_n1_minus)
print (3, 2), 1/resummation_pade_borel(3, 2, gamma_13_n1_minus)
for M in range(0, N + 1):
    for L in range(0, N - M + 1):
    #        print M, L,
        #FIXME : unknown exception
        try:
            res = resummation_pade_borel(L, M, gamma_13_n1_minus)
        except:
            res = "    Except"
        if res is None:
            print "      None",
        elif isinstance(res, str):
            print res,
        else:
            print "%10.4f" % (1/res),
    print


print
print "nu"
print "DS", dict2poly(nu_13_n1, tau).subs(tau,1)
print "DS-1", 1/dict2poly(nu_13_n1_minus, tau).subs(tau,1)