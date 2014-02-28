#!/usr/bin/python

__author__ = 'kirienko'

import numpy
import numpy as np
from scipy.optimize import curve_fit

from matplotlib import pyplot as plt



# def func(x, a, b, c):
#     return a * np.exp(-b * x) + c
#
# x = np.linspace(0,4,5)
# x1 = np.linspace(0,4,50)
# y = func(x, -2.5, 1.3, 0.5)
# yn = y + 0.2*np.random.normal(size=len(x))
#
# popt, pcov = curve_fit(func, x, yn)
#
# plt.figure()
# plt.plot(x, yn, 'ko', label="Original Noised Data")
# plt.plot(x1, func(x1, *popt), 'r-', label="Fitted Curve")
# plt.legend()
# plt.show()

def fit_function(x, a, b, c, x_0):
    print "a = %f, b = %f, c = %f, x_0 = %f" %(a,b,c, x_0)
    return a * numpy.exp(- b * (x - x_0)) + 0.2
    #return a * x**2 + b * x + c


xn = numpy.array([2., 3., 4., 5., 6.])
yn = numpy.array([0.0352112221332348, 0.0683704891587855, 0.0961859612147154, 0.117221076107934, 0.134028757600961])


print xn, yn

#popt, pcov = curve_fit(fit_function, xn, yn)

#print popt

#print fit_function(2, 5.6, 28.4, 0)
#print fit_function(xn[0], *popt)

font = {'family' : 'serif',
            'color'  : 'darkred',
            'weight' : 'normal',
            'size'   : 16,
            }
x = numpy.arange(2,20,0.1)
A = numpy.array([-0.0, 0.0,0.104021325279375,-0.0108396290953125, 0.10685478584648438,-0.22544785060546876,0.8152851661376953])
S = [sum(A[2:i]) for i in range(2,7)]
plt.figure()
plt.plot(xn,S, 'r--')
plt.plot(xn, yn, 'ko-', label="$\\eta = \\eta(L)$")
#plt.plot(x, fit_function(x, *popt), 'r-', label="$\\eta(x) = a * e^{- b (x - x_0)} + c$")
plt.legend(loc = 'lower right')
plt.grid(True)
#plt.xticks()
plt.xlabel('Number of loops')
plt.title("$\\eta$ as function of number of loops", fontdict = font)
plt.plot(1,0)
plt.plot(7,0)
plt.show()
