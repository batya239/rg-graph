#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from rggraphenv import abstract_graph_calculator, symbolic_functions
from two_and_three_loops import TWO_LOOP_REDUCTOR, THREE_LOOP_REDUCTOR
from four_loops import FOUR_LOOP_REDUCTOR
from dummy_reductors import FOUR_LOOP_REDUCTOR as DUMMY_FOUR_LOOP_REDUCTOR
import reductor
import reduction_util


USE_DUMMY = False


class ReductionGraphCalculator(abstract_graph_calculator.AbstractGraphCalculator):
    def __init__(self, *reduction_loops):
        self._reduction_loops = reduction_loops

    def get_label(self):
        return "reduction calculator for %s loops" % str(self._reduction_loops)

    def init(self):
        all_reductors = (TWO_LOOP_REDUCTOR, THREE_LOOP_REDUCTOR, DUMMY_FOUR_LOOP_REDUCTOR if USE_DUMMY else FOUR_LOOP_REDUCTOR)
        if not len(self._reduction_loops):
            reductors = all_reductors
        else:
            reductors = filter(lambda r: r.main_loops_condition in self._reduction_loops, all_reductors)
        reductor.initialize(*reductors)

    def calculate(self, graph):
        result = reductor.calculate(graph)
        if result is None:
            if reductor.DEBUG:
                print "reduction not works for", graph
            return None
        return result.evaluate(substitute_sectors=True, _d=symbolic_functions.d_phi4, series_n=5, remove_o=True), \
            reduction_util.calculate_graph_p_factor(graph)

    def is_applicable(self, graph):
        return reductor.is_applicable(graph)

    def dispose(self):
        pass


class ScalarProductReductionGraphCalculator(abstract_graph_calculator.AbstractGraphCalculator):
    def __init__(self, scalar_product_extractor, reduction_loops=None):
        self._scalar_product_extractor = scalar_product_extractor
        self._reduction_loops = reduction_loops

    def get_label(self):
        return "graphs with scalars products reduction calculator for %s loops" % str(self._reduction_loops)

    def init(self):
        all_reductors = (TWO_LOOP_REDUCTOR, THREE_LOOP_REDUCTOR, DUMMY_FOUR_LOOP_REDUCTOR if USE_DUMMY else FOUR_LOOP_REDUCTOR)
        if self._reduction_loops is None or not len(self._reduction_loops):
            reductors = all_reductors
        else:
            reductors = filter(lambda r: r.main_loops_condition in self._reduction_loops, all_reductors)
        reductor.initialize(*reductors)

    def calculate(self, graph):
        result = reductor.calculate(graph, self._scalar_product_extractor)
        if result is None:
            if reductor.DEBUG:
                print "reduction not works for", graph
            return None
        r = result.evaluate(substitute_sectors=True,
                            _d=symbolic_functions.d_phi4,
                            series_n=5,
                            remove_o=False)
        if reductor.DEBUG:
            print "V(%s)=%s" % (graph, result.evaluate(substitute_sectors=False))
            print "V(%s)=%s, %s" % (graph, r, reduction_util.calculate_graph_p_factor(graph))
        return r, reduction_util.calculate_graph_p_factor(graph)

    def is_applicable(self, graph):
        return reductor.is_applicable(graph)

    def dispose(self):
        pass