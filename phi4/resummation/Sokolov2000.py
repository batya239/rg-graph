#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

""" Данные из работы Орлова и Соколова 2000 года:
@article{Orlov2000,
  title={Critical thermodynamics of two-dimensional systems in the five-loop renormalization-group approximation},
  author={Orlov, EV and Sokolov, AI},
  journal={Physics of the Solid State},
  volume={42},
  number={11},
  pages={2151--2158},
  year={2000},
  publisher={Springer}
}
"""

from sympy import symbols, poly

n, g = symbols('n g')


def beta_half(k):
    _beta = -g + g ** 2 - g ** 3 / (n + 8) ** 2 * (10.33501055 * n + 47.67505273) \
            + g ** 4 / (n + 8) ** 3 * (5.000275928 * n ** 2 + 149.1518586 * n + 524.3766023) \
            - g ** 5 / (n + 8) ** 4 * (0.088842906 * n ** 3 + 179.6975910 * n ** 2 + 2611.154798 * n + 7591.108694) \
            + g ** 6 / (n + 8) ** 5 * (
        -0.00407946 * n ** 4 + 80.3096 * n ** 3 + 5253.56 * n ** 2 + 53218.6 * n + 133972)
    beta_k = poly(_beta.subs(n, k).expand()).all_coeffs()
    beta_k.reverse()
    return beta_k


def eta(k):
    _eta = g ** 2 / (n + 8) ** 2 * (n + 2) * 0.9170859698 - g ** 3 / (n + 8) ** 2 * (n + 2) * 0.05460897758 \
           + g ** 4 / (n + 8) ** 4 * (-0.0926844583 * n ** 3 + 4.05641051 * n ** 2 + 29.2511668 * n + 41.5352155) \
           - g ** 5 / (n + 8) ** 5 * (0.0709196 * n ** 4 + 1.05240 * n ** 3 + 57.7615 * n ** 2 + 325.329 * n + 426.896)
    eta_k = poly(_eta.subs(n, k).expand()).all_coeffs()
    eta_k.reverse()
    return eta_k


if __name__ == "__main__":
    print "for n = 1"
    print "β(g)/2 =", beta_half(1)
    print "η(g)/2 =", eta(1)

