#!/usr/bin/python
# -*- coding: utf8
import sys

__author__ = 'mkompan'

import sympy
import scipy.integrate as integrate
import math
import matplotlib.pyplot as plt
import numpy as np


import matplotlib as mpl
mpl.rcParams['text.usetex']=True
mpl.rcParams['text.latex.unicode']=True


from collections import namedtuple

results2013 = namedtuple('results2013', ('gamma', 'gamma_minus', 'nu', 'nu_minus', 'eta'))


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
        if isinstance(atom, sympy.Symbol) and tau != atom:
            vars.append(atom)
    series_poly = dict2poly(series_dict, tau)
    eq = (pade_num - pade_denom * series_poly).expand()
    eqs = list()
    for i in range(n + 1):
        eqs.append(eq.coeff(tau, i))
#    print "eq", eq , n
#    print "eqs", eqs
    return sympy.solve_linear_system(eqs2matrix(eqs, vars), *vars)


def solve_pade_sympy_lob(pade_num, pade_denom, series_dict, n, tau, a=0, g_star=None):
    """
    g_star must depend on tau (only for lob in pseudo-esp expansion)
    """
    if g_star is None:
        g_star = tau
    return solve_pade_sympy(pade_num, pade_denom*(1+g_star*a), series_dict, n, tau)


def borel_transform(series_dict, b=0):
    return dict(map(lambda x: (x, series_dict[x] / sympy.gamma(x + b + 1).evalf()), series_dict))


def resummation_pade(L, M, series_dict, series_param_value=1):
    tau = sympy.var('tau')
    padeNum, padeDenom = pade_aproximant(L, M, tau)
    padeFunc = padeNum / padeDenom
    res = solve_pade_sympy(padeNum, padeDenom, series_dict, L + M, tau)
#    print padeNum, padeDenom, res
    padeFunc_ = padeFunc
    for var, value in res.iteritems():
        var_ = sympy.var(str(var))
        padeFunc_ = padeFunc_.subs(var_, value)

    return padeFunc_.subs(tau, series_param_value)

#FIXME : b!=0 !!!!
func_template = """
def func(x,b=0,g=1):
    tau = x/(1-x)
    res = tau**b*math.exp(-tau) * ({pade})/(1-x)**2
    return res
"""


def resummation_pade_borel(L, M, series_dict, a=0, b=0, series_param_value=1):
    tau = sympy.var('tau')
    borel_dict = borel_transform(series_dict, b=b)
    padeNum, padeDenom = pade_aproximant(L, M, tau)
    padeFunc = padeNum / padeDenom
    res = solve_pade_sympy_lob(padeNum, padeDenom, borel_dict, L + M, tau, a=a)
    #    print res
    padeFunc_ = padeFunc
    for var, value in res.iteritems():
        var_ = sympy.var(str(var))
        padeFunc_ = padeFunc_.subs(var_, value)


#    print func_template.format(pade=padeFunc_)
    exec(func_template.format(pade=padeFunc_))
    try:
        output = integrate.quad(func, 0., 1., args=(b, series_param_value), full_output=1, limit=100)
        result = output[0]
        if len(output)==4:
            warn = output[3]
        else:
            warn = None
        return result, warn, func
    except:
        return None, None



def print_pade_minus(series_dict, N, m0=0, l0=0):
    print "Pade"
    print " "*10,
    for i in range(l0, N + 1):
        print "%10d" % (i),
    print
    for M in range(m0, N + 1):
        if l0 < N - M + 1:
            print "%10d" % M,
        for L in range(l0, N - M + 1):
            print "%10.4f" % (1/resummation_pade(L, M, series_dict)),
        print

def format_result(result, inverse=False):
    if inverse:
        return "%9.4f" % (1/result)
    else:
        return "%9.4f" % result

def print_pade_borel(series_dict, N, m0=0, l0=0, inverse=False,name=''):
    if inverse:
        print "Pade-Borel-1"
    else:
        print "Pade-Borel"
    print " "*10,
    for i in range(l0, N + 1):
        print "%10d" % (i),
    print
    warnings = list()
    for M in range(m0, N + 1):
        if l0 < N - M + 1:
            print "%10d" % M,
        for L in range(l0, N - M + 1):
            try:
                res, warn, func = resummation_pade_borel(L, M, series_dict)
            except:
                res = "    Except"
            if res is None:
                print "      None",
            elif isinstance(res, str):
                print res,
            else:
                #if warn is not None and ((L,M) == (2,3) or (L,M) == (3,2)):
                if warn is None: warn = ''
                if L+M == 5:
                    if "probably divergent" in warn:
                        print "%sD" % format_result(res, inverse=inverse),
                        warnings.append((name,(L, M), warn, func))
                    elif "Extremely bad integrand" in warn:
                        print "%sB" % format_result(res, inverse=inverse),
                        warnings.append((name,(L, M), warn, func))
                    else:
                        print "%sW" % format_result(res, inverse=inverse),
                        warnings.append((name,(L, M), warn, func))
                else:
                    print "%s " % format_result(res, inverse=inverse),
        print
    print
    
    ### Picture ###
    if warnings:
        plt.clf()
        for warning in warnings:
            print warning
            t = np.arange(0.0, 1.0, 0.005)
            f = warning[3]
            s = map(f,t)
            plt.plot(t,s)
        title = warnings[0][0]
        if inverse:
            inv='inverse'
        else:    
            inv=''
        plt.title("Pad\\'e-Borel %s"%inv+" integrands, index $%s$ for $%s$" %tuple(title.split("_")))
        plt.legend([list(w[1]) for w in warnings], loc = "lower left")
        plt.grid(True)
        #plt.ylim(-10,10)
        plt.savefig('pic_%s%s.pdf'%(title[1:],inv))
    print


def print_pade_borel_minus(series_dict, N, m0=0, l0=0,name=''):
    print_pade_borel(series_dict, N, m0=m0, l0=l0, inverse=True,name=name)


def calculate2013(result, N, a=0, b=0, nMessage=''):
    print "\n\n"+nMessage+"\n\n"
    print "gamma"

    print_pade_borel(result.gamma, N, name=r'\gamma'+'_'+nMessage)

    #print_pade_borel_minus(result.gamma_minus, N, name=r'\gamma'+'_'+nMessage)

    print
    print "nu"
    #print_pade_borel(result.nu, N, name=r'\nu'+'_'+nMessage)
    #print_pade_borel_minus(result.nu_minus, N, name=r'\nu'+'_'+nMessage)

    print
    print "eta"

    #print_pade_borel(result.eta, N, l0=2, name=r'\eta'+'_'+nMessage)



gStar_05 = {1: 1, 2: 0.716173621, 3: 0.095042867, 4: 0.086080396, 5: -0.204139}
gamma_minus_05 = {0: 1, 1: -1. / 3, 2: -0.113701246, 3: 0.024940678, 4: -0.039896059, 5: 0.0645212}
nu_minus_05 = {0: 2, 1: -2. / 3, 2: -0.2613686, 3: 0.0145746, 4: -0.0913127, 5: 0.118121}

#13
#n=1
n1 = results2013({0: 1, 1: 1. / 3, 2: 0.224812357, 3: 0.087897190, 4: 0.086443008, 5: -0.0180209},
                 {0: 1, 1: -1. / 3, 2: -0.113701246, 3: 0.024940678, 4: -0.039896059, 5: 0.0645210},
                 {0: 1./2, 1: 1. / 6, 2: 0.120897626, 3: 0.0584361287, 4: 0.056891652, 5: 0.00379868},
                 {0: 2., 1: -2. / 3, 2: -0.261368281, 3: 0.0145750797, 4: -0.091312521, 5: 0.118121},
                 {0: 0., 1: 0., 2: 0.0339661470, 3: 0.0466287623, 4: 0.030925471, 5: 0.0256843})


#n=0
n0 = results2013({0: 1, 1: 1. / 4, 2: 0.143242270, 3: 0.018272597, 4: 0.035251118, 5: -0.0634415},
                 {0: 1, 1: -1. / 4, 2: -0.080742270, 3: 0.037723538, 4: -0.028548147, 5: 0.0754631},
                 {0: 1./2, 1: 1. / 8, 2: 0.0787857831, 3: 0.0211750671, 4: 0.028101050, 5: -0.0222040},
                 {0: 2., 1: -1. / 2, 2: -0.190143132, 3: 0.0416216976, 4: -0.071673308, 5: 0.136330},
                 {0: 0., 1: 0., 2: 0.0286589366, 3: 0.0409908542, 4: 0.027138940, 5: 0.0236106})

#n=-1
nm1 = results2013({0: 1, 1: 1. / 7, 2: 0.060380873, 3: -0.023532210, 4: 0.012034268, 5: -0.0638772},
                  {0: 1, 1: -1. / 7, 2: -0.039972710, 3: 0.03786436, 4: -0.018392201, 5: 0.0649966},
                  {0: 1./2, 1: 1. / 14, 2: 0.0348693698, 3: -0.00424514372, 4: 0.011608435, 5: -0.0268913},
                  {0: 2., 1: -2. / 7, 2: -0.0986611527, 3: 0.0510003794, 4: -0.049264800, 5: 0.116842},
                  {0: 0., 1: 0., 2: 0.0187160402, 3: 0.0274103364, 4: 0.017144702, 5: 0.0159901})


#b = 0
#gStarBorel = borel_transform(gStar, b=0)
#print gStarBorel




N = 5

#print "\ngStar\n"
#print_pade(gStar_05, N, l0=1)
#
#print "\ngamma^-1\n"
#print_pade_minus(gamma_minus_05, N)
#
#print "\nnu^-1\n"
#print_pade_minus(nu_minus_05, N)


print 2013

#calculate2013(n1, N, nMessage="n=1")

calculate2013(n0, N, nMessage="n=0")

#calculate2013(nm1, N, nMessage="n=-1")
