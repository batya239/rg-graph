#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import dynamic_diagram_generator
import time

t = time.time()
for g in dynamic_diagram_generator.generate("e12|e3|45|45|5||", possible_fields=["aA"], possible_external_fields="Aa", possible_vertices=["aaA", "aAA"]):
    print g
print time.time() - t