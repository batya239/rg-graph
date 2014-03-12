__author__ = 'gleb'


from pole_extractor import diagram_calculator
from pole_extractor import numcalc
from pole_extractor import utils


Z1_0 = numcalc.NumEpsExpansion(exp={0: [1.0, 0.0]}, precise=True)
Z3_0 = numcalc.NumEpsExpansion(exp={0: [1.0, 0.0]}, precise=True)

# one loop:
g2_1 = utils.get_diagrams(2, 1)
g3_1 = utils.get_diagrams(3, 1)

Z1_1 = numcalc.NumEpsExpansion(exp={}, precise=True)
for g, c in g2_1:
    Z1_1 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=True).cut(0) * c
gamma1_1 = Z1_1[-1] * (-2.0)

Z3_1 = numcalc.NumEpsExpansion(exp={}, precise=True)
for g, c in g3_1:
    Z3_1 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=False).cut(0) * (-c)
gamma3_1 = Z3_1[-1] * (-2.0)

# two loops:
g2_2 = utils.get_diagrams(2, 2)
g3_2 = utils.get_diagrams(3, 2)

Z1_2 = numcalc.NumEpsExpansion(exp={}, precise=True)
for g, c in g2_2:
    Z1_2 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=True).cut(0) * c
gamma1_2 = Z1_2[-1] * (-4.0)

Z3_2 = numcalc.NumEpsExpansion(exp={}, precise=True)
for g, c in g3_2:
    Z3_2 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=False).cut(0) * (-c)
gamma3_2 = Z3_2[-1] * (-4.0)

# three loops:
g2_3 = utils.get_diagrams(2, 3)
g3_3 = utils.get_diagrams(3, 3)

Z1_3 = numcalc.NumEpsExpansion(exp={}, precise=True)
for g, c in g2_3:
    Z1_3 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=True).cut(0) * c
gamma1_3 = Z1_3[-1] * (-6.0)

Z3_3 = numcalc.NumEpsExpansion(exp={}, precise=True)
for g, c in g3_3:
    Z3_3 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=False).cut(0) * (-c)
gamma3_3 = Z3_3[-1] * (-6.0)

# four loops:
""" IS COEFFICIENT -24.0 CORRECT!!!! """
#g2_4 = utils.get_diagrams(2, 4)
g3_4 = utils.get_diagrams(3, 4)

#Z1_4 = numcalc.NumEpsExpansion(exp={}, precise=True)
#for g, c in g2_4:
#    Z1_4 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=True).cut(0) * c
#gamma1_4 = Z1_4[-1] * (-24.0)

Z3_4 = numcalc.NumEpsExpansion(exp={}, precise=True)
for g, c in g3_4:
    Z3_4 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=False).cut(0) * (-c)
gamma3_4 = Z3_4[-1] * (-24.0)

print 'Z1 = ' + str(Z1_0) + ' + u * (' + str(Z1_1) + ') + u^2 * (' + str(Z1_2) + ') + u^3 * (' + str(Z1_3) + ')'
print 'Z3 = ' + str(Z3_0) + ' + u * (' + str(Z3_1) + ') + u^2 * (' + str(Z3_2) + ') + u^3 * (' + str(Z3_3) + ')'
print '### Z2 = Z3, Z4 = 1 - Z3, Z0 = Z3 - 1 + u * eps^(-1)[0.5] ###\n'

print 'gamma1 = u^(1)' + str(gamma1_1) + ' + u^(2)' + str(gamma1_2) + ' + u^(3)' + str(gamma1_3)
print 'gamma3 = u^(1)' + str(gamma3_1) + ' + u^(2)' + str(gamma3_2) + ' + u^(3)' + str(gamma3_3)
print '### gamma1 = 2 * gamma_phi, gamma3 = gamma_g + 3 gamma_phi ###\n'

print 'gamma_phi = u^(1)' + str(gamma1_1 * 0.5) + ' + u^(2)' + str(gamma1_2 * 0.5) + ' + u^(3)' + str(gamma1_3 * 0.5)
print 'gamma_g = u^(1)' + str(gamma3_1 + gamma1_1 * (-1.5)) + ' + u^(2)' + str(gamma3_2 + gamma1_2 * (-1.5)) + \
      ' + u^(3)' + str(gamma3_3 + gamma1_3 * (-1.5))
print 'beta_u = u^(1)[-2eps] + u^(2)' + str(gamma3_1 * (-2.0) + gamma1_1 * 3.0) + \
      '+ u^(3)' + str(gamma3_2 * (-2.0) + gamma1_2 * 3.0) + ' + u^(4)' + str(gamma3_3 * (-2.0) + gamma1_3 * 3.0)