#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'

import phi4.symbolic_functions as sf
from phi4.symbolic_functions import G, e, l

d0 = G(1, 1) * G(2 - l, 1) * G(3 - 2 * l, 1)
s_d0_1 = 1 / e * G(1, 1) * G(2 - l, 1)
s_d0_2 = 0.5 * (1 / e - 1 / e / e) * G(1, 1)
d0_r1 = d0 - s_d0_1 - s_d0_2
d0_r = d0_r1 - sf.series(d0_r1, e, 0, 0, remove_order=True)
R = sf.series(d0_r, e, 0, 1, remove_order=True).evalf()
print "R", R

IR = 1 / e
print "IR", IR

import r
import graphine
import common
import symbolic_functions
from rggraphenv import storage
from rggraphenv import theory

storage.initStorage(theory.PHI4, symbolic_functions.to_internal_code, graphStorageUseFunctions=True)
r.DEBUG = True
KR1 = r.KR1(graphine.Graph.fromStr("e12-233-e34-4--", initEdgesColor=True),
            common.MSKOperation(),
            common.defaultSubgraphUVFilter)
KR1 = KR1.subs(symbolic_functions.p == 1).evalf()
print "KR1", KR1

KR_STAR = (KR1 + R * IR).simplify_indexed()
print "ACTUAL", KR_STAR

from swiginac import zeta
EXPECTED = (11./6-zeta(3))/2/e-13./3./2/2/e**2+10./3/2/2/2/e**3-4./3/2/2/2/2/e**4
EXPECTED = EXPECTED.evalf().simplify_indexed()
print "EXPECTED", EXPECTED
storage.closeStorage(revert=True)



