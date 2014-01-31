#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import numpy
import numpy.random

MAX_TRAPEZOIDAL_POINTS = 10000
MAX_MONTECARLO_POINTS = 10000


def trapezoidal(function, a, b, points):
    if points <= MAX_TRAPEZOIDAL_POINTS:
        step = float(b - a) / points
        x = numpy.arange(a, b, step, dtype=numpy.float)
        fx = function(x)
        fx1 = fx[:-1]
        fx2 = fx[1:]
        integral = ((fx1 + fx2) / 2 * step).sum()
        integral = ((fx1) * step).sum()
        return integral
    else:
        chunk = int(points / MAX_TRAPEZOIDAL_POINTS)
        step = float(b - a) / chunk
        print chunk
        res = 0
        for i in range(chunk):
            print a + i * step, a + (i + 1) * step

            term = trapezoidal(function, a + i * step, a + (i + 1) * step, MAX_TRAPEZOIDAL_POINTS)
            res += term
            print i, term, res
        return res


def montecarlo(function, a, b, points):
    current_points = 0
    res = 0
    sigma = 0
    while current_points < points:
        x = numpy.random.random(MAX_MONTECARLO_POINTS) * (b - a) + a
        fx = function(x)
        res += fx
        #        print fx.sum(), current_points, points
        current_points += MAX_MONTECARLO_POINTS
        sigma += ((fx-res.sum()/current_points)**2).sum()
    return res.sum() / current_points, sigma /current_points


from collections import namedtuple

vegas_bin = namedtuple("vegas_bin", ('start', 'end', 'value', 'sigma', 'points'))


def vegas(function, a_, b_, points):
    a = float(a_)
    b = float(b_)
    bins = [vegas_bin(a, (a + b) / 2, 0, 0, 0), vegas_bin((a + b) / 2, b, 0, 0, 0)]
