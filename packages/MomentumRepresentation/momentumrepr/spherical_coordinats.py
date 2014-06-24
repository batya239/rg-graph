#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import swiginac
import copy
import rggraphutil
import collections
import scalar_product
import inject
import configure_mr
import swiginac
from rggraphenv import symbolic_functions

#
#
# Based on LA mail
#


cos = swiginac.cos
sin = swiginac.sin

SubstitutedScalarProduct = collections.namedtuple("SubstitutedScalarProduct", ["expression", "variables", "fake_variable", "order"])


def sphere_square(dimension):
    d2 = dimension / symbolic_functions.CLN_TWO
    return symbolic_functions.CLN_TWO * swiginac.Pi ** d2 / swiginac.tgamma(d2)


class ScalarProductEnumerator(object):
    FAKE_VARIABLE_INDEX = -1

    @staticmethod
    def next_fake_variable_index():
        ScalarProductEnumerator.FAKE_VARIABLE_INDEX += 1
        return ScalarProductEnumerator.FAKE_VARIABLE_INDEX

    def __init__(self, loops_count, dimension):
        self._dimension = dimension
        self._loops_count = loops_count
        self._scalar_products = list()
        self._used_variables = list()
        self._omegas = list()
        self._next_omega_index = 1
        self.initialize()

    @staticmethod
    def enumerate(scalar_products_expression, loops_count):
        assert scalar_products_expression is not None

        if isinstance(scalar_products_expression, (list, tuple, set)):
            if None in scalar_products_expression:
                scalar_products_expression.remove(None)
            pairs = scalar_products_expression
        else:
            pairs = scalar_products_expression.momentum_pairs()
        pairs = filter(lambda p: len(p) == 2, pairs)

        dimension = configure_mr.Configure.dimension()

        mapped_pairs = rggraphutil.emptySetDict()
        for p in pairs:
            for e in p:
                mapped_pairs[e].add(p)
        mapped_pairs = mapped_pairs.items()
        mapped_pairs = sorted(mapped_pairs, key=lambda p: - len(p[1]))

        #
        # mapping flow indices to internal indices (minimal cos sin count in formulas)
        #
        index_mapping = dict()
        for order, index in enumerate(mapped_pairs):
            index_mapping[index[0]] = order

        enumerator = ScalarProductEnumerator(loops_count, dimension)

        substitutor = dict()
        #
        # mapped pairs -- momentum index to primitive scalar product
        #
        processed_pairs = set()
        for order, (index, pairs) in enumerate(mapped_pairs):
            for p in pairs:
                if p in processed_pairs:
                    continue
                processed_pairs.add(p)
                other_index = None
                for i in p:
                    if i != index:
                        other_index = i
                used_vars = enumerator.used_variables[order][index_mapping[other_index]]

                fake_var = "sp%s" % ScalarProductEnumerator.next_fake_variable_index()
                fake_var = symbolic_functions.var(fake_var)

                substitutor[p] = SubstitutedScalarProduct(expression=enumerator.scalar_products[order][index_mapping[other_index]],
                                                          variables=used_vars,
                                                          fake_variable=fake_var,
                                                          order=order + 1)
        return substitutor


    @property
    def omegas(self):
        return self._omegas

    @property
    def scalar_products(self):
        return self._scalar_products

    @property
    def used_variables(self):
        return self._used_variables

    def initialize(self):
        for i in xrange(self._loops_count):
            current_scalar_products = [None] * self._loops_count
            current_used_variables = [None] * self._loops_count
            current_omegas = [None] * self._loops_count
            self._used_variables.append(current_used_variables)
            self._omegas.append(current_omegas)
            self._scalar_products.append(current_scalar_products)
            for j in xrange(i + 1, self._loops_count):
                used_vars_i_j = list()
                omega_i_j = self.next_omega()
                used_vars_i_j.append(omega_i_j)
                current_omegas[j] = omega_i_j
                current_expression = cos(omega_i_j)
                for k in xrange(i - 1, -1, -1):
                    assert i != j
                    sin_part = symbolic_functions.CLN_ONE
                    cos_part = symbolic_functions.CLN_ONE
                    for l in (i, j):
                        omega = self._omegas[k][l]
                        used_vars_i_j.append(omega)
                        sin_part *= sin(omega)
                        cos_part *= cos(omega)
                    current_expression = cos_part + sin_part * current_expression
                current_scalar_products[j] = current_expression
                current_used_variables[j] = set(used_vars_i_j)

    def next_omega(self):
        omega = symbolic_functions.var("w%s" % self._next_omega_index)
        self._next_omega_index += 1
        return omega