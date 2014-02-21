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
    return a * numpy.exp(- b * (x - x_0)) + c
    #return a * x**2 + b * x + c


xn = numpy.array([2., 3., 4., 5., 6.])
yn = numpy.array([0.0875435181543787, 0.104928186172341, 0.138263261439161, 0.143926977222503, 0.165293404479870])
#yn = numpy.array([0.0875435181543787, 0.114928186172341, 0.138263261439161, 0.153926977222503, 0.165293404479870])
yn = numpy.array([0.0352112221332348, 0.0683704891587855, 0.0961859612147154, 0.117221076107934, 0.134028757600961])


print xn, yn

popt, pcov = curve_fit(fit_function, xn, yn)

print popt

#print fit_function(2, 5.6, 28.4, 0)
#print fit_function(xn[0], *popt)


x = numpy.arange(2,20,0.1)
plt.figure()
plt.plot(xn, yn, 'ko', label="Original Noised Data")
plt.plot(x, fit_function(x, *popt), 'r-', label="Fitted Curve")
plt.legend(loc = 'upper left')
plt.show()