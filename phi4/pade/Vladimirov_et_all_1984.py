#!/usr/bin/python
# -*- coding: utf8

""" Численные данные из статьи
@article{vladimirov1979calculation,
  title={Calculation of critical exponents by quantum field theory methods},
  author={Vladimirov, AA and Kazakov, D and Tarasov, OV},
  journal={Sov. Phys. JETP},
  volume={50},
  pages={521},
  year={1979}
}
http://www.jetp.ac.ru/cgi-bin/dn/e_050_03_0521.pdf
"""

__author__ = 'kirienko'

from sympy import symbols, zeta, poly

n, eps, eta = symbols('n eps eta')
z3 = float(zeta(3))

## d = 2
eta = (n+2)/(2*(n+8)**2)*(2*eps)**2 * \
      (1 + 2*eps/(4*(n+8)**2) * (-n*n+56*n+272) + (2*eps)**2/(16*(n+8)**4) * \
       (-5*n**4-230*n**3+1124*n**2+17920*n+46144-384*z3*(n+8)*(5*n+22)) )

eta_n1 = poly(eta.subs(n,1).expand()).all_coeffs()
eta_n1.reverse()

print eta_n1