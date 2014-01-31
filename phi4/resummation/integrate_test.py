#!/usr/bin/python
# -*- coding: utf8
import sys

__author__ = 'mkompan'


import integrate
import numpy
import time
integrate.MAX_TRAPEZOIDAL_POINTS = 10000

def print_timer():
    global start
    print "time = ", time.time()-start
    start = time.time()

def f(x):
    return x**2


start = time.time()
print integrate.montecarlo(f, 0, 1, 200000000)
print_timer()
sys.exit(0)
print integrate.trapezoidal(f, 0,1,20000)
print_timer()
sys.exit(0)
