#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'


from rggraphutil import VariableAwareNumber
from rggraphenv import symbolic_functions
import swiginac


ZERO_WEIGHT = VariableAwareNumber("l", 0, 0)
UNIT_WEIGHT = VariableAwareNumber("l", 1, 0)
DOUBLE_WEIGHT = VariableAwareNumber("l", 2, 0)

SPACE_DIM_PHI4 = 4
DIM_PHI4 = swiginac.numeric(str(SPACE_DIM_PHI4)) - swiginac.numeric("2") * symbolic_functions.e
EDGE_WEIGHT = -2

MARKER_0 = "0"
MARKER_1 = "1"