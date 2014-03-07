#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import graph_state
import itertools
import graphine
import collections
import swiginac
import scalar_product
from rggraphenv import symbolic_functions


def subs_external_propagators_is_zero(graph):
    new_edges = list()
    for e in graph.allEdges():
        new_edges.append(e.copy(flow=e.flow.subs_external_momenta_is_zero(),
                                propagator=e.propagator.subs_external_momenta_is_zero()))
    return graphine.Graph(new_edges)


Stretcher = collections.namedtuple("Stretcher", ["is_all_propagator", "indices", "var_index", "divergence_index"])

StretchVariable = collections.namedtuple("StretchVariable", ["var", "divergence"])


class MomentumFlow(object):
    STRETCHER_INDEX = -1

    @staticmethod
    def get_next_stretcher_index():
        MomentumFlow.STRETCHER_INDEX += 1
        return MomentumFlow.STRETCHER_INDEX

    def __init__(self, external_momentas, loop_momentas, stretchers=None):
        if stretchers:
            self._stretchers = tuple(stretchers)
        else:
            self._stretchers = tuple()
        self._external_momentas = tuple(external_momentas)
        self._loop_momentas = tuple(loop_momentas)
        self._expr = None
        self._unsubs_expr = None

    @property
    def stretcher_var(self):
        return self._stretcher_var

    @property
    def stretchers(self):
        return self._stretchers

    @property
    def loop_momentas(self):
        return self._loop_momentas

    @property
    def external_momentas(self):
        return self._external_momentas

    def stretch(self, stretched_indices, stretcher_var_index):
        assert stretched_indices
        return self.stretch(Stretcher(stretched_indices, stretcher_var_index))

    def stretch(self, stretcher):
        return MomentumFlow(self.external_momentas, self.loop_momentas, self.stretchers + (stretcher,))

    def subs_external_momenta_is_zero(self):
        return MomentumFlow((0,) * len(self._external_momentas), self._loop_momentas)

    def is_zero_external_momenta(self):
        return len(filter(lambda m: m != 0, self._external_momentas)) == 0

    def is_external(self):
        for m in self.loop_momentas:
            if m != 0:
                return False
        return True

    def generate_expression(self, stretch_indices=None):
        if self._expr is None:
            result = symbolic_functions.CLN_ZERO
            for index, coefficient in enumerate(self.external_momentas):
                if coefficient != 0:
                    result += coefficient * symbolic_functions.var("q%s" % index)
            for index, coefficient in enumerate(self.loop_momentas):
                if coefficient != 0:
                    v = symbolic_functions.var("k%s" % index)
                    for stretcher in self._stretchers:
                        if not stretcher.is_all_propagator and index in stretcher.indices:
                            v *= symbolic_functions.var("a%s" % stretcher.var_index)
                    result += coefficient * v
            self._expr = result

        all_propagator_stretchers = symbolic_functions.CLN_ONE
        for stretcher in self._stretchers:
            if stretcher.is_all_propagator:
                if stretch_indices is not None and stretcher.var_index not in stretch_indices:
                    continue
                all_propagator_stretchers *= symbolic_functions.var("a%s" % stretcher.var_index)

        return self._expr, all_propagator_stretchers ** 2

    def generate_unsubstituted_expression(self, stretch_indices=None):
        assert self.is_zero_external_momenta()
        if self._unsubs_expr is None:
            result = list()
            for index, coefficient in enumerate(self.loop_momentas):
                if coefficient != 0:
                    v = symbolic_functions.var("k%s" % index)
                    for stretcher in self._stretchers:
                        if not stretcher.is_all_propagator and index in stretcher.indices:
                            v *= symbolic_functions.var("a%s" % stretcher.var_index)
                    result.append((index, coefficient * v))
            self._unsubs_expr = result

        all_propagator_stretchers = symbolic_functions.CLN_ONE
        for stretcher in self._stretchers:
            if stretcher.is_all_propagator:
                if stretch_indices is not None and stretcher.var_index not in stretch_indices:
                    continue
                all_propagator_stretchers *= symbolic_functions.var("a%s" % stretcher.var_index)

        return self._unsubs_expr, all_propagator_stretchers ** 2

    def get_external_momentas(self):
        external_momentas = set()
        for index, coefficient in enumerate(self.external_momentas):
            if coefficient != 0:
                external_momentas.add(symbolic_functions.var("k%s" % index))
        return external_momentas

    def get_loop_momentas(self):
        loop_momentas = set()
        for index, coefficient in enumerate(self.loop_momentas):
            if coefficient != 0:
                loop_momentas.add(symbolic_functions.var("k%s" % index))
        return loop_momentas

    def get_stretch_vars(self):
        stretch_vars = set()
        for s in self.stretchers:
            stretch_vars.add(StretchVariable(symbolic_functions.var("a%s" % s.var_index), s.divergence_index))
        return stretch_vars

    def get_internal_momentas_indices(self):
        internal_momentas = set()
        for index, coefficient in enumerate(self.loop_momentas):
            if coefficient != 0:
                internal_momentas.add(index)
        return internal_momentas

    def get_not_all_propagators_stretchers_indices(self):
        indices = set()
        for s in self._stretchers:
            if not s.is_all_propagator:
                indices.add(s.var_index)
        return indices

    @staticmethod
    def empty(external_lines_count, loops_count):
        return MomentumFlow((0,) * (external_lines_count - 1), (0,) * loops_count)

    @staticmethod
    def single_external(index, external_lines_count, loops_count):
        external_momentas = [0] * (external_lines_count - 1)
        external_momentas[index] = 1
        return MomentumFlow(external_momentas, (0,) * loops_count)

    @staticmethod
    def single_internal(index, external_lines_count, loops_count):
        internal_momentas = [0] * loops_count
        internal_momentas[index] = 1
        return MomentumFlow((0,) * (external_lines_count - 1), internal_momentas)

    def size(self):
        s = 0
        for v in self._loop_momentas:
            if v != 0:
                s += 1
        return s

    def __hash__(self):
        return hash(self.loop_momentas) + \
               31 * hash(self.external_momentas) + \
               31 ** 2 * hash(self.stretchers)

    def __eq__(self, other):
        if other is None:
            return False
        return self.external_momentas == other.external_momentas and self.loop_momentas == other.loop_momentas and set(self.stretchers) == set(other.stretchers)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if not other:
            return self
        assert not len(self.stretchers)
        return self._do_add_or_sub(other, lambda (c1, c2): c1 + c2)

    __radd__ = __add__

    def __sub__(self, other):
        assert not len(self.stretchers)
        return self._do_add_or_sub(other, lambda (c1, c2): c1 - c2)

    def _do_add_or_sub(self, other, operation):
        assert isinstance(other, MomentumFlow)
        new_external_momentas = map(operation, zip(self.external_momentas, other.external_momentas))
        new_loop_momentas = map(operation, zip(self.loop_momentas, other.loop_momentas))
        return MomentumFlow(new_external_momentas, new_loop_momentas)

    def __neg__(self):
        new_external_momentas = map(lambda c: - c, self.external_momentas)
        new_loop_momentas = map(lambda c: - c, self.loop_momentas)
        return MomentumFlow(new_external_momentas, new_loop_momentas, self.stretchers)

    def __str__(self):
        return str("(%s, %s)" % self.generate_expression())

    __repr__ = __str__


class StandartPropagator(object):
    def __init__(self, momentum_flow, has_mass=True):
        assert isinstance(momentum_flow, MomentumFlow)
        self._momentum_flow = momentum_flow
        self._has_mass = has_mass

    @property
    def has_mass(self):
        return self._has_mass

    @property
    def momentum_flow(self):
        return self._momentum_flow

    def to_propagators_sum(self):
        return PropagatorsSum((self, ))

    def get_momentum(self, stretch_indices=None):
        return self.momentum_flow.generate_expression(stretch_indices)

    def energy_expression(self, stretch_indices=None, scalar_products_substitutor=None):
        indices_to_modulus, stretcher = self.momentum_flow.generate_unsubstituted_expression(stretch_indices)

        result = symbolic_functions.CLN_ZERO
        for q1, q2 in itertools.product(indices_to_modulus, repeat=2):
            i1 = q1[0]
            i2 = q2[0]
            m1 = q1[1]
            m2 = q2[1]
            if i1 == i2:
                result += m1 * m2
            else:
                result += m1 * m2 * scalar_products_substitutor[frozenset([i1, i2])].fake_variable
        # result **= 2
        if self._has_mass:
            result += symbolic_functions.CLN_ONE
        return result * stretcher

    def get_scalar_products(self):
        not_null_momentas = list()
        for i, c in enumerate(self._momentum_flow.loop_momentas):
            if c != 0:
                not_null_momentas.append(i)
        return set(map(lambda c: frozenset(c), itertools.combinations(not_null_momentas, 2)))

    def subs_external_momenta_is_zero(self):
        return StandartPropagator(self._momentum_flow.subs_external_momenta_is_zero(), self._has_mass)

    def __str__(self):
        return "P(%s)" % self.momentum_flow

    __repr__ = __str__

    def __add__(self, other):
        if isinstance(other, StandartPropagator):
            return PropagatorsSum((self, other))
        if isinstance(other, PropagatorsSum):
            return PropagatorsSum((self,) + other.propagators)

    def __hash__(self):
        return hash(self.momentum_flow) + 31 * hash(self.has_mass)

    def __neg__(self):
        return StandartPropagator(- self.momentum_flow, has_mass=self.has_mass)

    def __eq__(self, other):
        return self.momentum_flow == other.momentum_flow and self.has_mass == other.has_mass


class PropagatorsSum(object):
    def __init__(self, propagators):
        self._propagators = frozenset(propagators)

    @property
    def propagators(self):
        return self._propagators

    def subs_external_momenta_is_zero(self):
        return PropagatorsSum(map(lambda p: p.subs_external_momenta_is_zero(), self._propagators))

    def __hash__(self):
        return hash(self.propagators)

    def __eq__(self, other):
        return self.propagators == other.propagators