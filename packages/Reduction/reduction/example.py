#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import reductor
import sector

result = reductor.THREE_LOOP_REDUCTOR.evaluate_sector(sector.Sector(0, 1, -2, 0, 0, 1, 1, 1, 1))
