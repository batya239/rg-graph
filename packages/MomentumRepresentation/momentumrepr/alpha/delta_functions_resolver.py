#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import collections
from rggraphenv import symbolic_functions

DeltaArgument = collections.namedtuple("DeltaArgument", ["u_base", "u_prod", "v_sum"])


def resolve(delta_arguments):
    removed_us = list()
    denominators = list()
    substitutors = list()

    substituted = set()
    for arg in sorted(delta_arguments, key=lambda arg: -len(arg.u_prod)):
        removed_us.append(arg.u_base)
        denominators.append(arg.u_prod)
        assert arg.u_base not in substituted
        substituted.add(arg.u_base)
        subs = reduce(lambda r, v: r + v.as_var(), arg.v_sum, symbolic_functions.CLN_ZERO) / reduce(lambda r, u: r * u, arg.u_prod, symbolic_functions.CLN_ONE)
        substitutors.append((arg.u_base, subs))
    return removed_us, denominators, substitutors