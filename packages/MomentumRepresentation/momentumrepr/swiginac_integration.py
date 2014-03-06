#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import swiginac

swiginac.integral.max_integration_level = 3000

def adjust(limit):
    if limit == 1:
        return 0.999
    if limit == 0:
        return 0.001
    return limit


def swiginac_integrate(integrand_series, integrations, scalar_products_functions):
    answer = dict()
    print "start integration..."
    for degree, integrand in integrand_series.items():
        for sp_function in scalar_products_functions:
            integrand = integrand.subs(sp_function[0] == sp_function[1])
        integral = integrand
        for integration in integrations:
            a = adjust(integration.a)
            b = adjust(integration.b)
            integral = swiginac.integral(integration.var, a, b, integral)
        answer[degree] = integral.evalf()
    print "integration done"
    return answer
