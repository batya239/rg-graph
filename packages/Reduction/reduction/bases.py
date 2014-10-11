#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

from rggraphenv import symbolic_functions

k1, k2, k3, k4, p = symbolic_functions.var("k1 k2 k3 k4 p")

BASIS_4 = [k4 + p, -k2 + k4, k2 - k3 + k4, k1 - k2 + k3 - k4, -k1 + k4, -k1 + k4, 
           k1 - k2, k2 - k3, k3 - k4, k1 + p, k2 + p, k3 + p, k3, k4, k1]

BASIS_3 = [k1, k3, k3, k2 + k3, k1 - k3, k1 - k2 - k3, k1 + p, k3 + p,  -k2 + p]

BASIS_2 = [k1, k1 + p, k1 - k2, k2, k2 + p]