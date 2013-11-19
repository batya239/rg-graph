#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import reductor
import sector

result = reductor.THREE_LOOP_REDUCTOR.evaluate_sector(sector.Sector(0, 0, 0, 3, 1, 1, 1, 0, 1))

print "d=5"
print result.subs(sector.d == 6)
print "d=10"
print result.subs(sector.d == 10)
print "d=15"
print result.subs(sector.d == 15)
