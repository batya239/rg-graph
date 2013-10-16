__author__ = 'gleb'

import pole_extractor.expansion
import pole_extractor.numcalc
import polynomial

a = -5
b = 4
toIndex = 5

p1 = polynomial.poly([(1, [1, ])], degree=(a, b))
p2base = [(1, []), ]
for i in range(1, -a + 1):
    p2base.append((1, [1]*i))
p2 = polynomial.poly(p2base)

polynomial_expansion = pole_extractor.expansion.extract_poles(p1 * p2, toIndex)
integrated_exp = pole_extractor.numcalc.compute_exp_via_CUBA(polynomial_expansion)

analytical_exp = {-1: float(b) ** (-1)}
for k in range(toIndex + 1):
    analytical_exp[k] = 1
    for i in range(a + 1, 0):
        analytical_exp[k] += i ** (-(k + 1))
    analytical_exp[k] *= (-b) ** k

acquired = []
for k in sorted(integrated_exp.keys()):
    print str(k) + ': ' + str(integrated_exp[k][0]) + ' +- ' + str(integrated_exp[k][1]) + ' == ' \
        + str(analytical_exp[k])
    acquired.append(integrated_exp[k][0] - integrated_exp[k][1] <= analytical_exp[k] <= integrated_exp[k][0] + integrated_exp[k][1])

print all(acquired)
if not all(acquired):
    print acquired