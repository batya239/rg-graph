#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import Gfunc
import sympy

e = Gfunc.e
l = Gfunc.lambd
G = Gfunc.G

R1 = dict()
g = dict()
R = dict()
IR = dict()

z3, z4, z5, z6, z7 = sympy.var('z3 z4 z5 z6 z7')


def K(expr):
    e = sympy.var('e')
    return expr.series(e, 0, 0).removeO()


print "\n     ee11-ee-"
# ee11-ee-
## e11-e-
g['e11-e-'] = G(1, 1)
R1['e11-e-'] = g['e11-e-']
R['e11-e-'] = R1['e11-e-'] - K(R1['e11-e-'])
IR['11--'] = g['e11-e-']

print "KR1['ee11-ee-'] = ", K(R1['e11-e-'])

print "\n     e111-e-"
# e111-e-
## e111-e-
gamma = 'e111-e-'
g[gamma] = G(1, 1) * G(e, 1)
R1[gamma] = g[gamma]
R[gamma] = R1[gamma] - K(R1[gamma])

print "KR1['%s'] = " % gamma, K(R1[gamma])

print "\n     ee11-22-ee-"
# ee11-22-ee-
## e11-22-e-
gamma = 'e11-22-e-'
g[gamma] = G(1, 1) * G(1, 1)
R1[gamma] = g[gamma] - 2 * g['e11-e-'] * K(R1['e11-e-'])
R[gamma] = R1[gamma] - K(R1[gamma])
IR['11--'] = g['e11-e-']

print "KR1['%s'] = " % gamma, K(R1[gamma])

print "\n     ee12-e22-e-"
#ee12-e22-e-
##e112-2-e-
gamma = 'e112-2-e-'
g[gamma] = (G(1, 1) * G(1 + e, 1))
R1[gamma] = (g[gamma] - K(R1['e11-e-']) * g['e11-e-'])
R[gamma] = R1[gamma] - K(R1[gamma])

print "KR1['%s'] = " % gamma, K(R1[gamma])

## e112-e2--

gamma = 'e112-e2--'
g[gamma] = (G(1, 1) * G(e, 2))
tempR1 = g[gamma] - R['e11-e-'] * IR['11--']
print "KR1['%s'] = " % gamma, K(tempR1)
IR['112-2--'] = K(R1['e112-2-e-'] +R1['e11-e-']*IR['11--'])
print "IR['112-2--'] = ", IR['112-2--']


# e112-22-e-
## e112-22-e-
gamma = 'e112-22-e-'
print "\n     %s" % gamma
g[gamma] = (G(1, 1) * G(1, 1) * G(2 * e, 1))
R1[gamma] = (g[gamma] - 2 * K(R1['e11-e-']) * g['e111-e-'])
R[gamma] = R1[gamma] - K(R1[gamma])

print "KR1['%s'] = " % gamma, K(R1[gamma])

# ee11-22-33-ee-
gamma = 'e11-22-33-e-'
print "\n     %s" % gamma
g[gamma] = (G(1, 1) * G(1, 1) * G(1, 1))
R1[gamma] = (g[gamma] - 3 * K(R1['e11-e-']) * g['e11-22-e-'] -
             2 * K(R1['e11-22-e-']) * g['e11-e-'] +
             K(R1['e11-e-']) ** 2 * g['e11-e-'])
R[gamma] = R1[gamma] - K(R1[gamma])

print "KR1['%s'] = " % gamma, K(R1[gamma])

# ee11-23-e33-e-
gamma = 'e11-23-e33--'
print "\n     %s" % gamma
g[gamma] = (g['e11-e-'] * g['e112-2-e-'])
R1[gamma] = (g[gamma] - K(R1['e11-e-']) * g['e112-2-e-'] -
             K(R1['e11-e-']) * g['e11-22-e-'] -
             K(R1['e112-2-e-']) * g['e11-e-'] +
             K(R1['e11-e-']) ** 2 * g['e11-e-'])
R[gamma] = R1[gamma] - K(R1[gamma])

print "KR1['%s'] = " % gamma, K(R1[gamma])
print "KR1['%s'] = " % gamma, -K((R1['e11-e-']) * K(R1['e112-2-e-']))

# ee12-ee3-333--
gamma = 'e12-e3-333--'
print "\n     %s" % gamma
g[gamma] = (G(1, 1) * G(1 - l, 1) * G(3 - 2 * l, 1))
R1[gamma] = (g[gamma] - K(R1['e111-e-']) * g['e11-e-'])
R[gamma] = R1[gamma] - K(R1[gamma])

print "KR1['%s'] = " % gamma, K(R1[gamma])

gamma = 'e12-e333-3--'
print "\n     %s" % gamma
g[gamma] = (G(1, 1) * G(1 - l, 1) * G(3 - 2 * l, 1))
R1[gamma] = (g[gamma] - K(R1['e111-e-']) * g['e11-e-'])  # no IR subgraph here!!
R[gamma] = R1[gamma] - K(R1[gamma])

print "KR1['%s'] = " % gamma, K(R1[gamma])


# e123-e23-e3-e-
g['e12-23-3-e-'] = (6 * z3 + e * (9 * z4 - 12 * z3)
                    + e ** 2 * (42 * z5 - 18 * z4)
                    + e ** 3 * (90 * z6 - 84 * z5 - 18 * z3 ** 2))

gamma = 'e123-e23-3--'
print "\n     %s" % gamma
g[gamma] = (G(1 + 2 * e, 1) * g['e12-23-3-e-'])
R1[gamma] = g[gamma]
R[gamma] = R1[gamma] - K(R1[gamma])

print "KR1['%s'] = " % gamma, K(R1[gamma])

# ee12-e33-e33--
gamma = 'e112-33-e3--'
print "\n     %s" % gamma
g[gamma] = (G(1, 1) ** 2 * G(1 + 2 * e, 1))
R1[gamma] = g[gamma] - 2 * K(R1['e11-e-']) * g['e112-2-e-'] - K(R1['e11-22-e-']) * g['e11-e-']
R[gamma] = R1[gamma] - K(R1[gamma])

print "KR1['%s'] = " % gamma, K(R1[gamma])

gamma = 'e112-33-3-e-'
print "\n     %s" % gamma
g[gamma] = (G(1, 1) ** 2 * G(2 * e, 2))
R1[gamma] = g[gamma] - 2 * K(R1['e11-e-']) * g['e112-e2--'] - R['e11-22-e-'] * IR['11--']
R[gamma] = R1[gamma] - K(R1[gamma])

print "KR1['%s'] = " % gamma, K(R1[gamma])

gamma = 'e112-e33-3--'
print "\n     %s" % gamma
g[gamma] = (G(1, 1) ** 2 * G(2 + e, e))
R1[gamma] = g[gamma] - K(R1['e11-e-']) * g['e112-e2--'] - R['e11-e-'] * IR['112-2--']
R[gamma] = R1[gamma] - K(R1[gamma])

print "KR1['%s'] = " % gamma, K(R1[gamma])

# e112-e3-e33-e-
