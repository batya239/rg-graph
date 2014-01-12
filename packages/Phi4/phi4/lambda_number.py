#!/usr/bin/python
# -*- coding: utf8
import graph_state
import rggraphutil.variable_aware_number as v_number

VAR_NAME = "l"


def lambda_number(number):
    _tuple = number if not isinstance(number, graph_state.Rainbow) else number.colors
    return v_number.VariableAwareNumber.create(VAR_NAME, _tuple)


def to_rainbow(number):
    return graph_state.Rainbow((number.a, number.b))


def from_rainbow(edge):
    return lambda_number(edge.colors)
