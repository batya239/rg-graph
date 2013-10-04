#!/usr/bin/python
# -*- coding: utf8
import graph_state

__author__ = 'dimas'

ONE_LINE_WEIGHT = (1, 0)

SPACE_DIM = 4
edgeUVWeight = -2
EDGE_IR_WEIGHT = -2

NUMERATOR_INPUT = "i"
NUMERATOR_OUTPUT = "o"

LEFT_NUMERATOR = graph_state.Fields.fromStr(NUMERATOR_INPUT + NUMERATOR_OUTPUT)
RIGHT_NUMERATOR = graph_state.Fields.fromStr(NUMERATOR_OUTPUT + NUMERATOR_INPUT)
EMPTY_NUMERATOR = graph_state.Fields.fromStr("00")


def chooseOppositeFields(fields):
    if fields == LEFT_NUMERATOR:
        return RIGHT_NUMERATOR
    elif fields == RIGHT_NUMERATOR:
        return LEFT_NUMERATOR
    else:
        return EMPTY_NUMERATOR