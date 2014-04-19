__author__ = 'gleb'


from pole_extractor import diagram_calculator, numcalc, utils


Z1_0 = numcalc.NumEpsExpansion(exp={0: [1.0, 0.0]}, precise=True)
Z3_0 = numcalc.NumEpsExpansion(exp={0: [1.0, 0.0]}, precise=True)


# one loop:

g2_1 = utils.get_diagrams(2, 1)
g3_1 = utils.get_diagrams(3, 1)

Z1_1 = numcalc.NumEpsExpansion(exp={}, precise=True)
l = len(g2_1)
for i, (g, c) in enumerate(g2_1):
    Z1_1 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=True).cut(0) * c
    print '\rGetting 2-tailed w 1 loop: ' + str(i + 1) + ' of ' + str(l),
gamma1_1 = Z1_1[-1] * (-2.0)

Z3_1 = numcalc.NumEpsExpansion(exp={}, precise=True)
l = len(g3_1)
for i, (g, c) in enumerate(g3_1):
    Z3_1 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=False).cut(0) * (-c)
    print '\rGetting 3-tailed w 1 loop: ' + str(i + 1) + ' of ' + str(l),
gamma3_1 = Z3_1[-1] * (-2.0)


# two loops:

g2_2 = utils.get_diagrams(2, 2)
g3_2 = utils.get_diagrams(3, 2)

Z1_2 = numcalc.NumEpsExpansion(exp={}, precise=True)
l = len(g2_2)
for i, (g, c) in enumerate(g2_2):
    Z1_2 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=True).cut(0) * c
    print '\rGetting 2-tailed w 2 loops: ' + str(i + 1) + ' of ' + str(l),
gamma1_2 = Z1_2[-1] * (-4.0)

Z3_2 = numcalc.NumEpsExpansion(exp={}, precise=True)
l = len(g3_2)
for i, (g, c) in enumerate(g3_2):
    Z3_2 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=False).cut(0) * (-c)
    print '\rGetting 3-tailed w 2 loops: ' + str(i + 1) + ' of ' + str(l),
gamma3_2 = Z3_2[-1] * (-4.0)


# three loops:

g2_3 = utils.get_diagrams(2, 3)
g3_3 = utils.get_diagrams(3, 3)

Z1_3 = numcalc.NumEpsExpansion(exp={}, precise=True)
l = len(g2_3)
for i, (g, c) in enumerate(g2_3):
    Z1_3 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=True).cut(0) * c
    print '\rGetting 2-tailed w 3 loops: ' + str(i + 1) + ' of ' + str(l),
gamma1_3 = Z1_3[-1] * (-6.0)

Z3_3 = numcalc.NumEpsExpansion(exp={}, precise=True)
l = len(g3_3)
for i, (g, c) in enumerate(g3_3):
    Z3_3 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=False).cut(0) * (-c)
    print '\rGetting 3-tailed w 3 loops: ' + str(i + 1) + ' of ' + str(l),
gamma3_3 = Z3_3[-1] * (-6.0)


# four loops:

g2_4 = utils.get_diagrams(2, 4)
g3_4 = utils.get_diagrams(3, 4)

Z1_4 = numcalc.NumEpsExpansion(exp={}, precise=True)
l = len(g2_4)
for i, (g, c) in enumerate(g2_4):
    Z1_4 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=True).cut(0) * c
    print '\rGetting 2-tailed w 4 loops: ' + str(i + 1) + ' of ' + str(l),
gamma1_4 = Z1_4[-1] * (-8.0)

Z3_4 = numcalc.NumEpsExpansion(exp={}, precise=True)
l = len(g3_4)
for i, (g, c) in enumerate(g3_4):
    Z3_4 += diagram_calculator.get_expansion(g, rprime=True, momentum_derivative=False).cut(0) * (-c)
    print '\rGetting 3-tailed w 4 loops: ' + str(i + 1) + ' of ' + str(l),
gamma3_4 = Z3_4[-1] * (-8.0)


print '\r',
print 'Z1 = ' + str(Z1_0) + ' + u * (' + str(Z1_1) + ') + u^2 * (' + str(Z1_2) + ') + u^3 * (' + str(Z1_3) #+ \
#      ') + u^4 * (' + str(Z1_4) + ')'
print 'Z3 = ' + str(Z3_0) + ' + u * (' + str(Z3_1) + ') + u^2 * (' + str(Z3_2) + ') + u^3 * (' + str(Z3_3) + \
      ') + u^4 * (' + str(Z3_4) + ')'
print '### Z2 = Z3, Z4 = 1 - Z3, Z0 = Z3 - 1 + u * eps^(-1)[0.5] ###\n'

print 'gamma1 = u^(1)[' + str(gamma1_1) + '] + u^(2)[' + str(gamma1_2) + '] + u^(3)[' + str(gamma1_3) + \
      '] + u^(4)[' + str(gamma1_4) + ']'
print 'gamma3 = u^(1)[' + str(gamma3_1) + '] + u^(2)[' + str(gamma3_2) + '] + u^(3)[' + str(gamma3_3) + \
      '] + u^(4)[' + str(gamma3_4) + ']'
print '### gamma1 = 2 * gamma_phi, gamma3 = gamma_g + 3 gamma_phi ###\n'

print 'gamma_phi = u^(1)[' + str(gamma1_1 * 0.5) + '] + u^(2)[' + str(gamma1_2 * 0.5) + '] + u^(3)[' + \
      str(gamma1_3 * 0.5) + '] + u^(4)[' + str(gamma1_4 * 0.5) + ']'
print 'gamma_g = u^(1)[' + str(gamma3_1 + gamma1_1 * (-1.5)) + '] + u^(2)[' + str(gamma3_2 + gamma1_2 * (-1.5)) + \
      '] + u^(3)[' + str(gamma3_3 + gamma1_3 * (-1.5)) + '] + u^(4)[' + str(gamma3_4 + gamma1_4 * (-1.5)) + ']'

beta_u_2 = gamma3_1 * (-2.0) + gamma1_1 * 3.0
beta_u_3 = gamma3_2 * (-2.0) + gamma1_2 * 3.0
beta_u_4 = gamma3_3 * (-2.0) + gamma1_3 * 3.0
beta_u_5 = gamma3_4 * (-2.0) + gamma1_4 * 3.0

print 'beta_u = u^(1)[-2eps] + u^(2)[' + str(beta_u_2) + ']+ u^(3)[' + str(beta_u_3) + '] + u^(4)[' + str(beta_u_4) + \
      '] + u^(5)[' + str(beta_u_5) + ']'

u_star_1 = 2.0 / beta_u_2
u_star_2 = -4.0 * beta_u_3 / (beta_u_2**3)
u_star_3 = -8.0 * (beta_u_2*beta_u_4 - 2.0*(beta_u_3**2)) / (beta_u_2**5)
u_star_4 = -16.0 * (5.0*(beta_u_3**3) - 5.0*beta_u_2*beta_u_3*beta_u_4 + (beta_u_2**2)*beta_u_5) / (beta_u_2**7)
u_star = numcalc.NumEpsExpansion({1: u_star_1, 2: u_star_2, 3: u_star_3, 4: u_star_4})
ita = u_star * gamma3_1 + (u_star**2) * gamma3_2 + (u_star**3) * gamma3_3 + (u_star**4) * gamma3_4
ita1 = u_star * gamma1_1 + (u_star**2) * gamma1_2 + (u_star**3) * gamma1_3 + (u_star**4) * gamma1_4

print '\n### u* : beta_u(u*) == 0 ###\nu* = ' + str(u_star) + '\ngamma3(u*) = ' + str(ita) + \
      '\ngamma_1(u*) = ' + str(ita1)
