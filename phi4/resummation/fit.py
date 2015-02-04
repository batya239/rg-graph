#!/usr/bin/python

__author__ = 'kirienko'

import numpy
import numpy as np
from scipy.optimize import curve_fit

from matplotlib import pyplot as plt

def fit_function(x, a, b, c, x_0):
    c = 0.2
    print "a = %f, b = %f, c = %f, x_0 = %f" %(a,b,c, x_0)
    return -a * np.exp( b * (x + x_0)) + c


xn = numpy.array([2., 3., 4., 5., 6.])

## gStar = 1.88, b = 2 :
yn = numpy.array([0.0352112221332348, 0.0683704891587855, 0.0961859612147154, 0.117221076107934, 0.134028757600961])

## gStar = 1.75, b = 3.5 :
#yn = np.array([0.0253157644796685,0.0275588371775547,0.0234783671009914, 0.0183011773880176, 0.0142419335344348])

#print xn, yn

popt, pcov = curve_fit(fit_function, xn, yn)

print fit_function(xn[0], *popt)

font = {'family' : 'serif',
            #'color'  : 'darkred',
            'weight' : 'normal',
            'size'   : 16,
            }
#x = numpy.arange(2,7,0.1) ## <-- for pic_eta_d2_with_raw.pdf
x = numpy.arange(2,20,0.1) ## <-- for pic_eta_b_2.pdf
A = numpy.array([-0.0, 0.0,0.104021325279375,-0.0108396290953125, 0.10685478584648438,-0.22544785060546876,0.8152851661376953])
#S = [sum(A[2:i]) for i in range(2,7)] ## <-- for pic_eta_d2_with_raw.pdf
plt.figure()
#plt.plot(xn,S, 'ro--', label = "$-$ non-resumed points") ## <-- for pic_eta_d2_with_raw.pdf
plt.plot(xn, yn, 'ko', label="$\\eta = \\eta(n)$ $-$ resumed points")
a,b,c,x_0 = popt
plt.plot(x, fit_function(x, *popt), '-', label="$\\eta(x) = %.3f\,e^{%.3f\,(x\,%.3f)} + %.2f$"%(a,b,x_0,0.20))
plt.legend(loc = 'lower right')
#plt.legend(loc = 'upper left')
plt.grid(True)
plt.xticks()
plt.xlabel('Number of loops')
plt.title("$\\eta = \\eta(n)$, $D = 2$, $N = 1$", fontdict = font)
plt.plot(1,0)
#plt.plot(7,0)
plt.show()
