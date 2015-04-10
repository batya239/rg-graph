__author__ = 'dima'

import collections
import itertools
from rggraphutil import zeroDict


class IntegralRepresentation(object):
    def __init__(self, integrand, loop_momentas, scalar_products, stretchers, graph_representator):
        self.integrand = integrand
        self.loop_momentas = loop_momentas
        self.stretchers = stretchers
        self.scalar_products = scalar_products
        self.graph_representator = graph_representator

    def __hash__(self):
        return 1

    def __eq__(self, other):
        return are_equal(self, other)


def are_equal(ir1, ir2):
    loop_momentas1 = list(ir1.loop_momentas)
    loop_momentas2 = list(ir2.loop_momentas)

    scalar_products1 = map(lambda sp: sp.fake_variable, ir1.scalar_products)
    scalar_products2 = map(lambda sp: sp.fake_variable, ir2.scalar_products)

    stretchers1 = map(lambda st: st.var, ir1.stretchers)
    stretchers2 = map(lambda st: st.var, ir2.stretchers)

    if len(loop_momentas1) != len(loop_momentas2):
        return False
    if len(stretchers1) != len(stretchers2):
        return False

    for perm_loop_momentas in itertools.permutations(loop_momentas1, len(loop_momentas1)):
        q = ir1.integrand
        rule = list()
        for i, lm in enumerate(perm_loop_momentas):
            lm_s = loop_momentas2[i]
            rule.append(lm == lm_s)
        q = q.subs(rule)

        for perm_stretchers in itertools.permutations(stretchers1, len(stretchers1)):
            q1 = q
            rule1 = list()
            for j, s in enumerate(perm_stretchers):
                s_s = stretchers2[j]
                rule1.append(s == s_s)
            q1 = q1.subs(rule1)

            for perm_scalar_products in itertools.permutations(scalar_products1, len(scalar_products1)):
                q2 = q1
                rule2 = list()
                for k, sp in enumerate(perm_scalar_products):
                    s_sp = scalar_products2[k]
                    rule2.append(sp == s_sp)
                q2 = q2.subs(rule2)

                if q2.is_equal(ir2.integrand):
                    return True
    return False