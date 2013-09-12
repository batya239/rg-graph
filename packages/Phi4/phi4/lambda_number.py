#!/usr/bin/python
# -*- coding: utf8
import graph_state

import rggraphutil.variable_aware_number as v_number

VAR_NAME = "l"


def lambdaNumber(number):
    aTuple = number if not isinstance(number, graph_state.Rainbow) else number.colors
    return v_number.VariableAwareNumber.create(VAR_NAME, aTuple)


def toRainbow(number):
    return number.a, number.b


def fromRainbow(edge):
    return lambdaNumber(edge.colors)


def pureLambda(value):
    return lambdaNumber((0, value))


def pureConst(value):
    return lambdaNumber((value, 0))