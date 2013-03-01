#!/usr/bin/python
# -*- coding: utf8

import rggraphutil.variable_aware_number as v_number

VAR_NAME = "lambda"


def lambdaNumber(number):
    return v_number.VariableAwareNumber.create(VAR_NAME, number)


def toRainbow(number):
    return number.a, number.b


def fromRainbow(edge):
    return lambdaNumber(edge.colors)


def pureLambda(value):
    return lambdaNumber((0, value))


def pureConst(value):
    return lambdaNumber((value, 0))