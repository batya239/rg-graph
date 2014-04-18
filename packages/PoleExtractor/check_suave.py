__author__ = 'gleb'

from pole_extractor import utils, diagram_calculator

"""
112|3|34|5|55||

Calculated sector:
8 * ((0, (1, 3, 4, 6, 7, 8)), (1, (3, 4, 6, 7, 8)), (6, (4, 7, 8)), (7, (8,)))
With integrand:
((u1)^(-2+eps*3))*((u3))*((u6)^(-2+eps*2))*((1+u1*u4*u6+u1*u6+u1*u3+u1*u6*u7+u8*u1*u6*u7+u1)^(3-eps*4))*
((u8*u3+1+u1*u4*u6+u8*u4+u4*u6+u3*u4+u8+u4+u3+u8*u1*u3*u4+u8*u4*u6+u8*u3*u4+u8*u1*u3+
u1*u3+u8*u1*u4*u6*u7+u8*u4*u6*u7+u8*u1*u3*u7+u1*u3*u4+u8*u3*u7+u8*u7+u8*u1*u4*u6)^(-3+eps))*((0.5)*(u7)^(-2+eps))
With expansion length: 1727
With result:
eps^(-3)[0.004008+/-0.000006] + eps^(-2)[0.01663+/-0.00010] + eps^(-1)[-0.1301+/-0.0008] + eps^(0)[0.278+/-0.008] + O[eps]^1
"""

for d, c in utils.get_diagrams(0, 4):
    d1 = diagram_calculator.calculate_diagram(label=d, theory=3, max_eps=-1,
                                              zero_momenta=True, force_update=False, num_alg='Suave')
    d2 = diagram_calculator.get_expansion(d, rprime=False, momentum_derivative=False)
    print '### NEW ###\n' + str(d1) + '\n' + str(d2) + '\n' + str(d1.cut(0) == d2.cut(0)) + '\n### OLD ###'