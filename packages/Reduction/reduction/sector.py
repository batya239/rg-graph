#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'

import rggraphutil
import itertools
import swiginac
import copy
import reduction_util
import graphine
import graph_state
import re
import lazy_value
from rggraphenv import symbolic_functions


import time
import rggraphutil


CLN_ONE = swiginac.numeric("1")
CLN_ZERO = swiginac.numeric("0")


class Sector(object):
    SECTOR_TO_KEY = dict()

    def __init__(self, *propagators_weights):
        if len(propagators_weights) == 1 and isinstance(propagators_weights[0], (list, tuple)):
            self._propagators_weights = tuple(propagators_weights[0])
        else:
            self._propagators_weights = propagators_weights

        self._propagators_weights = tuple(map(lambda w: w.to_int() if isinstance(w, swiginac.numeric) else w, self._propagators_weights))
        self._as_graph = None

    @property
    def propagators_weights(self):
        return self._propagators_weights

    def as_sector_linear_combinations(self):
        return SectorLinearCombination.singleton(self, CLN_ONE)

    def as_rule_key(self):
        key = Sector.SECTOR_TO_KEY.get(self, None)
        if key is None:
            propagators_condition = list()
            for w in self._propagators_weights:
                propagators_condition.append(SectorRuleKey.PROPAGATOR_CONDITION_POSITIVE if w > 0 else SectorRuleKey.PROPAGATOR_CONDITION_NOT_POSITIVE)
            key = SectorRuleKey(propagators_condition)
            Sector.SECTOR_TO_KEY[self] = key
        return key

    def as_litered_representation(self, env_name):
        return "j[" + env_name + "".join(map(lambda i: ", " + str(i), self._propagators_weights)) + "]"

    def __neg__(self):
        return SectorLinearCombination.singleton(self, -1)

    def __str__(self):
        return "Sector" + str(self._propagators_weights).replace(" ", "")

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        return self.as_sector_linear_combinations() + other

    def __sub__(self, other):
        return self.as_sector_linear_combinations() - other

    def __rsub__(self, other):
        return (- self) + other

    def __pow__(self, power, modulo=None):
        assert power == -1
        return Sector(map(lambda p: p * power, self._propagators_weights))

    __radd__ = __add__

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            assert isinstance(other, int)
            return SectorLinearCombination.singleton(self, swiginac.numeric(str(other)))
        elif isinstance(other, swiginac.refcounted):
            return SectorLinearCombination.singleton(self, other)
        elif isinstance(other, Sector):
            return Sector(map(lambda (x, y): x + y, itertools.izip(self.propagators_weights, other.propagators_weights)))
        raise NotImplementedError()

    __rmul__ = __mul__

    def __div__(self, other):
        if isinstance(other, (float, int)):
            assert isinstance(other, int)
            return SectorLinearCombination.singleton(self, CLN_ONE / swiginac.numeric(str(other)))
        elif isinstance(other, swiginac.refcounted):
            return SectorLinearCombination.singleton(self, CLN_ONE / other)
        elif isinstance(other, SectorLinearCombination):
            #assert isinstance(other.additional_part, int) and other.additional_part == 0
            sector_to_coefficients = rggraphutil.zeroDict()
            for s, c in other.sectors_to_coefficient.items():
                #assert isinstance(c, int)
                sector_to_coefficients[self / s] = c
            combination = SectorLinearCombination(sector_to_coefficients)
            return combination
        elif isinstance(other, Sector):
            return Sector(map(lambda (x, y): x - y, itertools.izip(self.propagators_weights, other.propagators_weights)))
        raise NotImplementedError(type(other))

    def __eq__(self, other):
        return self.propagators_weights == other.propagators_weights

    def __hash__(self):
        return hash(self.propagators_weights)

    @staticmethod
    def create_from_topologies_and_graph(graph, topologies, all_propagators_count):
        return reduction_util.find_topology_for_graph(graph,
                                                      topologies,
                                                      lambda _s, _g: Sector.create_from_shrunk_topology(_s, _g, all_propagators_count))

    @staticmethod
    def create_from_shrunk_topology(topology_graph, weights_graph, all_propagators_count):
        id_to_weight = dict()
        for e1, e2 in itertools.izip(topology_graph.allEdges(nickel_ordering=True),
                                     weights_graph.allEdges(nickel_ordering=True)):
            if not e1.is_external() and e2.weight:
                id_to_weight[e1.colors[0]] = e2.weight.a
        propagators_weights = list()
        for i in xrange(all_propagators_count):
            weight = id_to_weight.get(i, None)
            if weight is None:
                propagators_weights.append(0)
            else:
                propagators_weights.append(weight)
        return Sector(propagators_weights)


class SectorLinearCombination(object):
    @staticmethod
    def _filter_zeros(some_dict):
        new_dict = rggraphutil.zeroDict()
        for k, v in some_dict.items():
            if isinstance(v, swiginac.numeric) and v.to_double() == 0:
                continue
            if isinstance(v, (int, float)):
                assert isinstance(v, int)
                if v == 0:
                    continue
                v = swiginac.numeric(str(v))
            new_dict[k] = v
        return new_dict

    @staticmethod
    def check(some_dict):
        new_dict = rggraphutil.zeroDict()
        for k, v in some_dict.items():
            if isinstance(v, lazy_value.Lazy):
                return some_dict
            new_dict[k] = lazy_value.LazyValue.create(v)
        return new_dict

    def __init__(self, sectors_to_coefficient, additional_part=CLN_ZERO, force=False):
        self._additional_part = lazy_value.LazyValue.create(additional_part)
        self._sectors_to_coefficient = SectorLinearCombination.check(sectors_to_coefficient if force else SectorLinearCombination._filter_zeros(sectors_to_coefficient))

    def str_without_masters(self, masters):
        l = sorted(filter(lambda s: s not in masters, self.sectors_to_coefficient.keys()), cmp=reduction_util._compare)
        l.reverse()
        return str(l)

    @property
    def additional_part(self):
        return self._additional_part

    def get_value(self, masters):
        return reduce(lambda s, e: s + masters[e[0]] * e[1].evaluate(), self._sectors_to_coefficient.items(), self._additional_part.evaluate())

    def force_filter_zeros(self):
        new_sectors_to_coefficient = rggraphutil.zeroDict()
        for s, c in self.sectors_to_coefficient.iteritems():
            evaled = c.evaluate()
            if isinstance(evaled, swiginac.numeric) and evaled.to_double() == 0:
                continue
            elif isinstance(evaled, (int, float)) and evaled == 0:
                assert isinstance(evaled, int)
                continue
            new_sectors_to_coefficient[s] = c
        return SectorLinearCombination(new_sectors_to_coefficient, self.additional_part)

    def substitute(self, sectors_to_value):
        new_additional_part = self._additional_part
        new_sectors_to_coefficient = copy.copy(self._sectors_to_coefficient)
        for s, v in sectors_to_value.items():
            c = new_sectors_to_coefficient[s]
            del new_sectors_to_coefficient[s]
            try:
                new_additional_part += c * v
            except TypeError as e:
                raise e
        return SectorLinearCombination(new_sectors_to_coefficient, new_additional_part)

    def __len__(self):
        return len(self._sectors_to_coefficient)

    def normalize(self):
        sectors_to_coefficient = copy.copy(self._sectors_to_coefficient)
        for key, value in sectors_to_coefficient.items():
            sectors_to_coefficient[key] = value.normal() if not isinstance(value, (swiginac.numeric, float, int)) else value
        return SectorLinearCombination(sectors_to_coefficient, self.additional_part)

    @staticmethod
    def singleton(sector, coefficient):
        sectors_to_coefficient = rggraphutil.zeroDict()
        sectors_to_coefficient[sector] = coefficient
        return SectorLinearCombination(sectors_to_coefficient)

    def remove_sector(self, sector):
        if sector not in self._sectors_to_coefficient:
            return self
        new_sectors_to_coefficient = copy.copy(self._sectors_to_coefficient)
        del new_sectors_to_coefficient[sector]
        return SectorLinearCombination(new_sectors_to_coefficient, self._additional_part)

    def replace_sector_to_sector_linear_combination(self, sector, sector_linear_combination):
        sectors_to_coefficient = copy.copy(self.sectors_to_coefficient)
        c = sectors_to_coefficient[sector]
        del sectors_to_coefficient[sector]
        for s, _c in sector_linear_combination.sectors_to_coefficient.items():
            sectors_to_coefficient[s] += c * _c
        return SectorLinearCombination(sectors_to_coefficient,
                                       self._additional_part + sector_linear_combination.additional_part * c, force=True)

    @property
    def sectors_to_coefficient(self):
        return self._sectors_to_coefficient

    @property
    def sectors(self):
        return self.sectors_to_coefficient.keys()

    def as_sector_linear_combinations(self):
        return self

    def __neg__(self):
        new_sectors_to_coefficients = rggraphutil.zeroDict()
        for s, c in self._sectors_to_coefficient.items():
            new_sectors_to_coefficients[s] = -c
        return SectorLinearCombination(new_sectors_to_coefficients, - self._additional_part)

    def __add__(self, other):
        return self._do_add(other, CLN_ONE)

    def __sub__(self, other):
        return self._do_add(other, -CLN_ONE)

    def __rsub__(self, other):
        return (- self) + other

    __radd__ = __add__

    def __mul__(self, other):
        return self._do_mul_or_div(other, True)

    __rmul__ = __mul__

    def __div__(self, other):
        return self._do_mul_or_div(other, False)

    def __pow__(self, power, modulo=None):
        if power == 0:
            return 1
        assert modulo is None
        if isinstance(power, swiginac.numeric):
            power = power.to_int()
        assert isinstance(power, int), type(power)
        #assert self._additional_part == 0
        assert power < 0
        _power = abs(power)
        sectors_to_coefficient = rggraphutil.zeroDict()
        for s, c in self._sectors_to_coefficient.items():
            #assert isinstance(c, int)
            sectors_to_coefficient[s ** (-1)] = c
        inversed = SectorLinearCombination(sectors_to_coefficient)
        return reduce(lambda x, y: x * y, [inversed] * _power, CLN_ONE)

    def __str__(self):
        # l = sorted(self.sectors_to_coefficient.keys(), cmp=reduction_util._compare)
        # l.reverse()
        # return str(l)
        return symbolic_functions.safe_integer_numerators(str(self.additional_part)) + "".join(
            map(lambda i: "+%s*(%s)" % (i[0], symbolic_functions.safe_integer_numerators(str(i[1]))), self.sectors_to_coefficient.items()))

    def _do_add(self, other, operation_sign):
        sectors_to_coefficient = copy.copy(self.sectors_to_coefficient)
        if isinstance(other, Sector):
            sectors_to_coefficient[other] += operation_sign
            return SectorLinearCombination(sectors_to_coefficient, self.additional_part)
        elif isinstance(other, SectorLinearCombination):
            for s, c in other.sectors_to_coefficient.items():
                sectors_to_coefficient[s] += operation_sign * c
            return SectorLinearCombination(sectors_to_coefficient, self.additional_part + other.additional_part)
        elif isinstance(other, (int, float)):
            return SectorLinearCombination(self.sectors_to_coefficient, additional_part=self.additional_part + swiginac.numeric(str(other)))
        elif isinstance(other, (swiginac.refcounted, lazy_value.Lazy)):
            return SectorLinearCombination(self.sectors_to_coefficient, additional_part=self.additional_part + other)
        else:
            raise NotImplementedError(type(other))

    def _do_mul_or_div(self, other, do_mul):
        if isinstance(other, (swiginac.refcounted, lazy_value.Lazy)):
            sectors_to_coefficient = rggraphutil.zeroDict()
            for s, c in self.sectors_to_coefficient.items():
                sectors_to_coefficient[s] = c * other if do_mul else (c / other)
            additional_part = self.additional_part * lazy_value.LazyValue.create(other) if do_mul else self.additional_part / other
            return SectorLinearCombination(sectors_to_coefficient, additional_part)
        if isinstance(other, (int, float)):
            other = swiginac.numeric(str(other))
            sectors_to_coefficient = rggraphutil.zeroDict()
            for s, c in self.sectors_to_coefficient.items():
                sectors_to_coefficient[s] = c * other if do_mul else (c / other)
            additional_part = self.additional_part * lazy_value.LazyValue.create(other) if do_mul else (self.additional_part / other)
            return SectorLinearCombination(sectors_to_coefficient, additional_part)
        if isinstance(other, SectorLinearCombination):
            assert do_mul
            new_sector_to_coefficient = rggraphutil.zeroDict()
            for s1, c1 in self.sectors_to_coefficient.items():
                for s2, c2 in other.sectors_to_coefficient.items():
                    new_sector_to_coefficient[s1 * s2] += c1 * c2
                    if new_sector_to_coefficient[s1 * s2] is 0:
                        del new_sector_to_coefficient[s1 * s2]
            return SectorLinearCombination(new_sector_to_coefficient) + other * self.additional_part + self * other.additional_part
        raise NotImplementedError("other type: %s, operation %s" % (type(other), "*" if do_mul else ":"))


ZERO_SECTOR_LINEAR_COMBINATION = SectorLinearCombination(rggraphutil.zeroDict(), force=True)

d = symbolic_functions.var("d")


class NumeratorsReducingRuleKey(object):
    def __init__(self, ):
        pass

    def is_applicable(self, graph):
        pass


class NumeratorsReducingRule(object):
    def __init__(self, rule):
        pass


class SectorRuleKey(object):
    PROPAGATOR_CONDITION_POSITIVE = "1"
    PROPAGATOR_CONDITION_NOT_POSITIVE = "0"

    def __init__(self, initial_propagators_condition):
        self._initial_propagators_condition = tuple(initial_propagators_condition)

    @property
    def initial_propagators_condition(self):
        return self._initial_propagators_condition

    def is_applicable(self, sector):
        assert len(self._initial_propagators_condition) == len(sector.propagators_weights), \
            "%d != %d" % (len(self._initial_propagators_condition), len(sector.propagators_weights))
        for condition, weight in itertools.izip(self._initial_propagators_condition, sector.propagators_weights):
            if condition is SectorRuleKey.PROPAGATOR_CONDITION_POSITIVE and weight <= 0 \
            or condition is SectorRuleKey.PROPAGATOR_CONDITION_NOT_POSITIVE and weight > 0:
                return False
        return True

    def __cmp__(self, other):
        return cmp(self.initial_propagators_condition, other.initial_propagators_condition)

    def __repr__(self):
        return "SectorRuleKey: " + str(self._initial_propagators_condition)

    __str__ = __repr__

    def __hash__(self):
        return hash(self._initial_propagators_condition)

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return self._initial_propagators_condition == other._initial_propagators_condition


class SectorRule(object):
    def __init__(self, additional_condition, apply_formula, exception=None):
        """
        exception_condition -- yet another condition because LiteRed is so crazy
        """
        self._exception_condition = exception
        self._additional_condition = additional_condition
        self._apply_formula = apply_formula
        self._a_lambda = None
        self._is_symmetry_rule = None

    def complexity(self):
        return len([m for m in re.finditer('Sector', self._apply_formula)])

    def is_symmetry_rule(self):
        if self._is_symmetry_rule is None:
            self._is_symmetry_rule = self._apply_formula.find("Sector") == self._apply_formula.rfind("Sector")
        return self._is_symmetry_rule

    def is_applicable(self, sector):
        if self._additional_condition:
            return self._apply_additional_condition(sector)
        return True

    def _apply_additional_condition(self, sector):
        return eval(self._additional_condition.format(None, *sector.propagators_weights))

    def apply(self, sector):
        if self._exception_condition and eval(self._exception_condition.format(None, *sector.propagators_weights)) == 0:
            raise ValueError("%s: %s" % (self._exception_condition, sector))

        if self._apply_formula is None:
            return ZERO_SECTOR_LINEAR_COMBINATION

        if self._a_lambda is None:
            self.create_lambda(len(sector.propagators_weights))
        evaled = self._a_lambda(*sector.propagators_weights).as_sector_linear_combinations()
        return evaled

    def create_lambda(self, sector_size):
        lambda_prefix = "lambda %s: " % ", ".join(map(lambda i: "n" + str(i), xrange(1, sector_size + 1)))
        lambda_suffix = re.sub('{(\d+)}', 'n\\1', self._apply_formula)
        self._a_lambda = eval(lambda_prefix + lambda_suffix)


    def __str__(self):
        return "SectorRule:\n\t%s\n\t%s" % (self._additional_condition, self._apply_formula)

    __repr__ = __str__


class AdditionalNonEqualityCondition(object):
    def __init__(self, var_index, number):
        self._var_index = var_index
        self._number = number

    def check(self, sector):
        return sector.propagators_weights[self._var_index] != self._number

    def __str__(self):
        return "n%d != %d" % (self._var_index, self._number)


class LazySwiginacSum(object):
    def __init__(self, args):
        self._args = args

    @staticmethod
    def singleton(val):
        return LazySwiginacSum((val, ))

    def evaluate(self):
        return reduce(lambda a, b: a + b, self._args)

    # noinspection PyProtectedMember
    def __add__(self, other):
        return LazySwiginacSum(self._args + other._args)