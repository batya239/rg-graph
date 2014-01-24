__author__ = 'gleb'


from pole_extractor import diagram_calculator
from pole_extractor import numcalc
import graphine


Z1_0 = numcalc.NumEpsExpansion(exp={0: [1.0, 0.0]}, precise=True)
Z3_0 = numcalc.NumEpsExpansion(exp={0: [1.0, 0.0]}, precise=True)

# one loop:
g2_1 = (('e11-e-', 0.5), )
g3_1 = (('e12-e2-e-', 1.0), )

Z1_1 = numcalc.NumEpsExpansion(exp={}, precise=True)
for l, c in g2_1:
    Z1_1 += diagram_calculator.get_expansion(graphine.Graph.fromStr(l),
                                             rprime=True,
                                             momentum_derivative=True).cut(0) * c
gamma1_1 = Z1_1[-1] * (-2.0)

Z3_1 = numcalc.NumEpsExpansion(exp={}, precise=True)
for l, c in g3_1:
    Z3_1 += diagram_calculator.get_expansion(graphine.Graph.fromStr(l),
                                             rprime=True,
                                             momentum_derivative=False).cut(0) * (-c)
gamma3_1 = Z3_1[-1] * (-2.0)

# two loops:
g2_2 = (('e12-e3-33--', 0.5), ('e12-23-3-e-', 0.5))
g3_2 = (('e12-e3-e4-44--', 1.5), ('e12-e3-34-4-e-', 3.0), ('e12-34-34-e-e-', 0.5))

Z1_2 = numcalc.NumEpsExpansion(exp={}, precise=True)
for l, c in g2_2:
    Z1_2 += diagram_calculator.get_expansion(graphine.Graph.fromStr(l),
                                             rprime=True,
                                             momentum_derivative=True).cut(0) * c
gamma1_2 = Z1_2[-1] * (-4.0)

Z3_2 = numcalc.NumEpsExpansion(exp={}, precise=True)
for l, c in g3_2:
    Z3_2 += diagram_calculator.get_expansion(graphine.Graph.fromStr(l),
                                             rprime=True,
                                             momentum_derivative=False).cut(0) * (-c)
gamma3_2 = Z3_2[-1] * (-4.0)

# three loops:
g2_3 = (('e12-23-4-45-5-e-', 0.5),  ('e12-34-35-e-55--', 0.25), ('e12-e3-44-55-5--', 0.25),
        ('e12-23-4-e5-55--', 1.0),  ('e12-e3-45-45-5--', 0.5),  ('e12-34-35-4-5-e-', 1.0),
        ('e12-34-34-5-5-e-', 0.25), ('e12-e3-34-5-55--', 0.5),  ('e12-33-44-5-5-e-', 0.125))
g3_3 = (('e12-e3-45-46-e-66--', 1.5),  ('e12-e3-34-5-e6-66--', 3.0),  ('e12-e3-45-45-6-6-e-', 1.5),
        ('e12-34-56-e5-e6-6--', 1.0),  ('e12-33-45-6-e6-e6--', 1.5),  ('e12-23-4-e5-56-6-e-', 3.0),
        ('e12-e3-e4-45-6-66--', 1.5),  ('e12-34-35-6-e6-e6--', 1.0),  ('e12-23-4-56-56-e-e-', 1.5),
        ('e12-e3-e4-55-66-6--', 0.75), ('e12-e3-44-56-5-6-e-', 3.0),  ('e12-e3-34-5-56-6-e-', 3.0),
        ('e12-e3-45-46-5-6-e-', 6.0),  ('e12-23-4-e5-e6-66--',  1.5), ('e12-e3-e4-56-56-6--', 1.5),
        ('e12-34-35-6-e5-6-e-', 3.0),  ('e12-e3-44-55-6-6-e-', 0.75))

#Z1_3 = numcalc.NumEpsExpansion(exp={}, precise=True)
#for l, c in g2_3:
#    Z1_3 += diagram_calculator.get_expansion(graphine.Graph.fromStr(l),
#                                             rprime=True,
#                                             momentum_derivative=True).cut(0) * c
#gamma1_3 = Z1_3[-1] * (-6.0)

#Z3_3 = numcalc.NumEpsExpansion(exp={}, precise=True)
#for l, c in g3_3:
#    Z3_3 += diagram_calculator.get_expansion(graphine.Graph.fromStr(l),
#                                             rprime=True,
#                                             momentum_derivative=False).cut(0) * (-c)
#gamma3_3 = Z3_3[-1] * (-6.0)

print 'Z1 = ' + str(Z1_0) + ' + u * (' + str(Z1_1) + ') + u^2 * (' + str(Z1_2) + ')'
print 'Z3 = ' + str(Z3_0) + ' + u * (' + str(Z3_1) + ') + u^2 * (' + str(Z3_2) + ')'
print '### Z2 = Z3, Z4 = 1 - Z3, Z0 = Z3 - 1 + u * eps^(-1)[0.5] ###'

print 'gamma1 = u^(1)' + str(gamma1_1) + ' + u^(2)' + str(gamma1_2)
print 'gamma3 = u^(1)' + str(gamma3_1) + ' + u^(2)' + str(gamma3_2)
print '### gamma1 = 2 * gamma_phi, gamma3 = gamma_g + 3 gamma_phi ###'

print 'gamma_phi = u^(1)' + str(gamma1_1 * 0.5) + ' + u^(2)' + str(gamma1_2 * 0.5)
print 'gamma_g = u^(1)' + str(gamma3_1 + gamma1_1 * (-1.5)) + ' + u^(2)' + str(gamma3_2 + gamma1_2 * (-1.5))
print 'beta_u = u^(1)[-2eps] + u^(2)' + str(gamma3_1 * (-2.0) + gamma1_1 * 3.0) + \
      '+ u^(3)' + str(gamma3_2 * (-2.0) + gamma1_2 * 3.0)