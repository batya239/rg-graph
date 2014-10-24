#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'


from rggraphutil import VariableAwareNumber
from rggraphenv.symbolic_functions import cln, e
import swiginac


ZERO_WEIGHT = VariableAwareNumber("l", 0, 0)
UNIT_WEIGHT = VariableAwareNumber("l", 1, 0)
DOUBLE_WEIGHT = VariableAwareNumber("l", 2, 0)
NEGATIVE_WEIGHT_EDGE = VariableAwareNumber("l", -1, 0)

SPACE_DIM_PHI4 = 4
SPACE_DIM_PHI3 = 6
DIM_PHI4 = cln(SPACE_DIM_PHI4) - cln(2) * e
DIM_PHI3 = cln(SPACE_DIM_PHI3) - cln(2) * e
EDGE_WEIGHT = -2

MARKER_0 = 0
MARKER_1 = 1
MARKER_M1 = -1