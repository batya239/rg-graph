#!/usr/bin/python
# -*- coding: utf8
import rggraphutil.variable_aware_number as v_number


VAR_NAME = "eps"


def epsNumber(number):
    return v_number.VariableAwareNumber.create(VAR_NAME, number)

