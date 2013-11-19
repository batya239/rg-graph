#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'

import rggraphutil
import itertools
import swiginac
import copy
from rggraphenv import symbolic_functions, cas_variable_resolver


class Sector(object):
    SECTOR_TO_KEY = dict()

    def __init__(self, *propagators_weights):
        if len(propagators_weights) == 1 and isinstance(propagators_weights[0], (list, tuple)):
            self._propagators_weights = tuple(propagators_weights[0])
        else:
            self._propagators_weights = propagators_weights
        self._as_graph = None

    @property
    def propagators_weights(self):
        return self._propagators_weights

    def as_sector_linear_combinations(self):
        return SectorLinearCombination.singleton(self, 1)

    def as_rule_key(self):
        key = Sector.SECTOR_TO_KEY.get(self, None)
        if key is None:
            propagators_condition = list()
            for w in self._propagators_weights:
                propagators_condition.append(SectorRuleKey.PROPAGATOR_CONDITION_POSITIVE if w > 0 else SectorRuleKey.PROPAGATOR_CONDITION_NOT_POSITIVE)
            key = SectorRuleKey(propagators_condition)
            Sector.SECTOR_TO_KEY[self] = key
        return key

    def __neg__(self):
        return SectorLinearCombination.singleton(self, -1)

    def __str__(self):
        return "Sector" + str(self._propagators_weights)

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        return self.as_sector_linear_combinations() + other

    def __sub__(self, other):
        return self.as_sector_linear_combinations() - other

    __radd__ = __add__

    __rsub__ = __sub__

    def __mul__(self, other):
        if isinstance(other, (float, int, swiginac.refcounted)):
            return SectorLinearCombination.singleton(self, other)
        raise NotImplementedError()

    __rmul__ = __mul__

    def __div__(self, other):
        if isinstance(other, (float, int, swiginac.refcounted)):
            return SectorLinearCombination.singleton(self, 1. / other)
        raise NotImplementedError()

    def __eq__(self, other):
        return self.propagators_weights == other.propagators_weights

    def __hash__(self):
        return hash(self.propagators_weights)

    @staticmethod
    def create_from_topologies_and_graph(graph, topologies, all_propagators_count):
        target_graph_name = graph.getPresentableStr()
        for topology in topologies:
            internal_edges = topology.internalEdges()
            n = len(internal_edges) - len(graph.internalEdges())
            if n < 0:
                continue
            elif n == 0:
                if topology.getPresentableStr() == target_graph_name:
                    return Sector._create_from_graph(topology, graph, all_propagators_count)

            for lines in itertools.combinations(internal_edges, n):
                shrunk = topology.batchShrinkToPoint([[x] for x in lines])
                gs_as_str = shrunk.getPresentableStr()
                if target_graph_name == gs_as_str:
                    return Sector._create_from_graph(shrunk, graph, all_propagators_count)
        return None

    @staticmethod
    def _create_from_graph(topology_graph, weights_graph, all_propagators_count):
        id_to_weight = dict()
        for e1, e2 in itertools.izip(topology_graph.allEdges(nickel_ordering=True),
                                     weights_graph.allEdges(nickel_ordering=True)):
            if e1.colors:
                id_to_weight[e1.colors[0]] = e2.colors[0]
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
        to_remove = list()
        for k, v in some_dict.items():
            if isinstance(v, swiginac.numeric) and v.to_double() == 0:
                to_remove.append(k)
        for k in to_remove:
            del some_dict[k]
        return some_dict

    def __init__(self, sectors_to_coefficient, additional_part=0):
        self._additional_part = additional_part
        self._sectors_to_coefficient = SectorLinearCombination._filter_zeros(sectors_to_coefficient)

    @property
    def additional_part(self):
        return self._additional_part

    def get_value(self, masters):
        value = self._additional_part
        for s, c in self._sectors_to_coefficient.items():
            value += masters[s] * c
        return value

    def print_not_evaled_result(self, _d=6):
        string = ""
        for s, c in self._sectors_to_coefficient.items():
           string += "+(" + str(c.subs(d == _d).evalf().simplify_indexed()) + ")*" + str(s)
        print "result d=" + str(_d) + "\n" + string

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

    @staticmethod
    def singleton(sector, coefficient):
        sectors_to_coefficient = rggraphutil.zeroDict()
        sectors_to_coefficient[sector] = coefficient
        return SectorLinearCombination(sectors_to_coefficient)

    def remove_sector(self, sector):
        new_sectors_to_coefficient = copy.copy(self._sectors_to_coefficient)
        del new_sectors_to_coefficient[sector]
        return SectorLinearCombination(new_sectors_to_coefficient, self._additional_part)

    def replace_sector_to_sector_linear_combination(self, sector, sector_linear_combination):
        sectors_to_coefficient = copy.copy(self.sectors_to_coefficient)
        c = sectors_to_coefficient[sector]
        if c == 0:
            raise AssertionError()
        del sectors_to_coefficient[sector]
        for s, _c in sector_linear_combination.sectors_to_coefficient.items():
            sectors_to_coefficient[s] += c * _c

        return SectorLinearCombination(sectors_to_coefficient,
                                       self._additional_part + sector_linear_combination.additional_part * c)

    @property
    def sectors_to_coefficient(self):
        return self._sectors_to_coefficient

    def as_sector_linear_combinations(self):
        return self

    def __neg__(self):
        new_sectors_to_coefficients = rggraphutil.zeroDict()
        for s, c in self._sectors_to_coefficient.items():
            new_sectors_to_coefficients[s] = -c
        return SectorLinearCombination(new_sectors_to_coefficients, - self._additional_part)

    def __add__(self, other):
        return self._do_add(other, 1)

    def __sub__(self, other):
        return self._do_add(other, -1)

    __radd__ = __add__

    __rsub__ = __sub__

    def __mul__(self, other):
        return self._do_mul_or_div(other, True)

    __rmul__ = __mul__

    def __div__(self, other):
        return self._do_mul_or_div(other, False)

    def __str__(self):
        return str(self.additional_part) + "".join(
            map(lambda i: "+%s*%s" % (i[0], i[1]), self.sectors_to_coefficient.items()))

    def _do_add(self, other, operation_sign):
        sectors_to_coefficient = copy.copy(self.sectors_to_coefficient)
        if isinstance(other, Sector):
            sectors_to_coefficient[other] += operation_sign
            return SectorLinearCombination(sectors_to_coefficient, self.additional_part)
        elif isinstance(other, SectorLinearCombination):
            for s, c in other.sectors_to_coefficient.items():
                sectors_to_coefficient[s] += operation_sign * c
            return SectorLinearCombination(sectors_to_coefficient, self.additional_part + other.additional_part)
        elif isinstance(other, (int, float, swiginac.refcounted)):
            return SectorLinearCombination(self.sectors_to_coefficient, additional_part=self.additional_part + other)
        else:
            raise NotImplementedError(other)

    def _do_mul_or_div(self, other, do_mul):
        if isinstance(other, (int, float, swiginac.refcounted)):
            sectors_to_coefficient = rggraphutil.zeroDict()
            for s, c in self.sectors_to_coefficient.items():
                sectors_to_coefficient[s] = c * other if do_mul else (
                    float(c) / other if isinstance(c, int) else c / other)
            additional_part = self.additional_part * other if do_mul else (float(self.additional_part) / other
                                                                           if isinstance(self.additional_part, int)
                                                                           else self.additional_part / other)
            return SectorLinearCombination(sectors_to_coefficient, additional_part)
        raise NotImplementedError()


ZERO_SECTOR_LINEAR_COMBINATION = SectorLinearCombination(rggraphutil.zeroDict())

d = cas_variable_resolver.var("d")


class SectorRuleKey(object):
    PROPAGATOR_CONDITION_POSITIVE = "+"
    PROPAGATOR_CONDITION_NOT_POSITIVE = "0"

    def __init__(self, initial_propagators_condition):
        self._initial_propagators_condition = tuple(initial_propagators_condition)

    def is_applicable(self, sector):
        assert len(self._initial_propagators_condition) == len(sector.propagators_weights), \
            "%d != %d" % (len(self._initial_propagators_condition), len(sector.propagators_weights))
        for condition, weight in itertools.izip(self._initial_propagators_condition, sector.propagators_weights):
            if condition is SectorRuleKey.PROPAGATOR_CONDITION_POSITIVE and weight <= 0 \
            or condition is SectorRuleKey.PROPAGATOR_CONDITION_NOT_POSITIVE and weight > 0:
                return False
        return True

    def __repr__(self):
        return "SectorRuleKey: " + str(self._initial_propagators_condition)

    __str__ = __repr__

    def __hash__(self):
        return hash(self._initial_propagators_condition)

    def __eq__(self, other):
        return self._initial_propagators_condition == other._initial_propagators_condition


class SectorRule(object):
    def __init__(self, additional_condition, apply_formula, expection_condition=None):
        """
        exception_condition -- yet another condition because LiteRed is so crazy
        """
        self._exception_condition = expection_condition
        self._additional_condition = additional_condition
        self._apply_formula = apply_formula

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
        print sector
        evaled = eval(
            self._apply_formula.format(None, *sector.propagators_weights)).as_sector_linear_combinations()
        print evaled
        print self._apply_formula
        print self._additional_condition
        print "\n"
        return evaled

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

    def __add__(self, other):
        return LazySwiginacSum(self._args + other._args)