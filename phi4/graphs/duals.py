#!/usr/bin/python
# -*- coding: utf8
import swiginac

__author__ = 'mkompan'

from rggraphenv.symbolic_functions import e, G, series, tgamma, Pi, cln, zeta, G1, G2, log, Pi

D = 4 - 2 * e
l = 1 - e


def H(*args):
    if len(args) == 1:
        a = args[0]
        return tgamma(D / 2 - a) / tgamma(a)
    else:
        res = 1
        for a in args:
            res = res * H(a)
        return res

def expand_logs(expr):
    return expr.subs(log(2*Pi)==log(2)+log(Pi)).subs(log(4)==2*log(2)).expand()


def raw_N(L, P, l=1 - e):
    """
    normalization factor for transferring to x-space and back for graph with L loops and P propagators
    """
    return 4 ** (-L * (l + 1)) * Pi ** (-(P - 1) * (l + 1)) * tgamma(l) ** P * tgamma(P - L * (l + 1)) / tgamma(
        (L + 1) * (l + 1) - P)

def raw_N2(L, P, l=1 - e):
    """
    normalization factor for transferring to x-space and back for graph with L loops and P propagators
    and two additional lines with arrows
    """
    return 4 ** (-L * (l + 1)) * Pi ** (-(P - 1) * (l + 1)) * tgamma(l) ** P * tgamma(P+1 - L * (l + 1)) / tgamma(
        (L + 1) * (l + 1) - (P+1)) * (-1)



def N(L, P, l=1 - e):
    """
    normalization factor (in G-scheme) for transferring to x-space and back for graph with L loops and P propagators
    """
    return raw_N(L, P, l=l) / (e * raw_N(1, 2, l=l)) ** L


def N2(L, P, l=1 - e):
    """
    normalization factor for transferring to x-space and back for graph with L loops and P propagators
    and two additional lines with arrows
    (in G-scheme)
    """
    return raw_N2(L, P, l=l) / (e * raw_N(1, 2, l=l)) ** L


print "1-loop"
G11 = raw_N(1, 2)
loop_factor = (e * G11 * (2 * Pi) ** (2 * (l + 1)))

G21 = N(1, 3) * Pi ** (l + 1) * H(l, l, D - l - l)
NN = 4
print series(G21, e, 0, NN).expand()
print series(G(2, 1), e, 0, NN).expand()
print
print series(G(l, l) * loop_factor - (1) * Pi ** (l + 1) * H(l, l, D - l - l), e, 0,
             NN).expand().evalf()
print
print
print

print "eye"
eye = N(2, 4) * (G(l, 2 * l) * loop_factor)

print expand_logs(series(eye, e, 0, NN).expand())
print series(eye - G(1, 1) * G(1 + e, 1), e, 0, NN).expand().evalf()
print
print

t1 = G1(2,1)**2*G(1+2*e,1)
print series(t1,e,0,NN).expand()
t1_1 = N2(3,5)*(G2(2*l,2*l)*loop_factor)
print expand_logs(series(t1_1,e,0,NN).expand())
print "Zero must be here"
print series(t1-t1_1,e,0,NN).evalf()


print
print
X = -(-5*zeta(5)/2)*8
d50_2 = G(1,1+5*e)*N2(5,10)*X*(loop_factor)**4

print series(d50_2,e,0,0).expand(0)

print expand_logs(series(N2(5,10)*loop_factor**4,e,0,3))