#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'


import swiginac

e = swiginac.symbol('e')

gamma = swiginac.tgamma
pi = swiginac.Pi

expr = ((4*pi)**(-e + 2)*(4*pi)**(e - 2)*gamma(-e)*gamma(-2*e + 2)*gamma(e + 1)/(2*e*gamma(e)*gamma(-2*e + 1)*gamma(-e + 1))
        + 1/(2*e))*((4*pi)**(-e + 2)*(4*pi)**(e - 2)*gamma(-3*e)*gamma(-2*e + 2)*gamma(3*e + 1)/(2*e*gamma(e)*gamma(-4*e + 1)*gamma(-e + 1)*gamma(2*e + 2)) -
                    (4*pi)**(-e + 2)*(4*pi)**(e - 2)*gamma(3*e)*gamma(-3*e + 1)*gamma(-2*e + 2)/(2*e*gamma(e)*gamma(-4*e + 2)*gamma(-e + 1)*gamma(2*e + 1)))*((4*pi)**(-e + 2)*(4*pi)**(e - 2)*gamma(-2*e)*gamma(-2*e + 2)*gamma(2*e + 1)/(2*e*gamma(e)*gamma(-3*e + 1)*gamma(-e + 1)*gamma(e + 2)) + (4*pi)**(-e + 2)*(4*pi)**(e - 2)*gamma(2*e)*gamma(-2*e + 1)*gamma(-2*e + 2)/(2*e*gamma(e)*gamma(-3*e + 2)*gamma(-e + 1)*gamma(e + 1)))

print expr.series(e==0,-1).expand()