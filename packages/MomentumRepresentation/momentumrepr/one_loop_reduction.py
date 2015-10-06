#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import sympy

x = sympy.Symbol("x", positive=True)
w = sympy.Symbol("w0", positive=True)
e = sympy.Symbol("e", positive=True)

G = sympy.gamma

c4 = sympy.numer(4)
c2 = sympy.numer(2)
c1 = sympy.numer(1)

sqrt = sympy.sqrt
atan = sympy.atan
I = sympy.I
log = sympy.log

def w2():
    return w / c2

def x4():
    return x / c4 + c1

def log_mod():
    return log(w2() ** c2+x4() ** c2) / c2


def P_R0_re():
    return - c1 / c4 * log_mod()

def P_R0_im():
    return c1 / c4 * atan(w2() / x4())

def P_R0():
    return P_R0_re() + I * P_R0_im()


def P_R2_re():
    return - x / c4 + x4() * log_mod() - w2() * atan(w2() / x4())

def P_R2_im():
    return w2() - w2() * log_mod() - x4() * atan(w2()/ x4())

def P_R2():
    return P_R2_re() / c4 + I * P_R2_im() / c4