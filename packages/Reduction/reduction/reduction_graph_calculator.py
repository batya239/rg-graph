#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from rggraphenv import abstract_graph_calculator
from two_and_three_loops import TWO_LOOP_REDUCTOR, THREE_LOOP_REDUCTOR
from four_loops import FOUR_LOOP_REDUCTOR


class ReductionGraphCalculator(abstract_graph_calculator.AbstractGraphCalculator):
    def get_label(self):
        return "reduction calculator for 2-4 loops"

    def init(self):
        reductor.initialize(TWO_LOOP_REDUCTOR, THREE_LOOP_REDUCTOR, FOUR_LOOP_REDUCTOR)

    def calculate(self, graph):
        result = reductor.calculate(graph)
        if result is None:
            return None
        return result.evaluate(substitute_sectors=True, _d=symbolic_functions.D, series_n=5, remove_o=True), \
            reduction_util.calculate_graph_p_factor(graph)

    def is_applicable(self, graph):
        return reductor.is_applicable(graph)

    def dispose(self):
        pass


class ScalarProductReductionGraphCalculator(abstract_graph_calculator.AbstractGraphCalculator):
    def __init__(self, scalar_product_extractor):
        self._scalar_product_extractor = scalar_product_extractor

    def get_label(self):
        return "graphs with scalars products reduction calculator for 2-4 loops"

    def init(self):
        reductor.initialize(TWO_LOOP_REDUCTOR, THREE_LOOP_REDUCTOR, FOUR_LOOP_REDUCTOR)

    def calculate(self, graph):
        result = reductor.calculate(graph, self._scalar_product_extractor)
        if result is None:
            return None
        return result.evaluate(substitute_sectors=True, _d=symbolic_functions.D, series_n=5, remove_o=True), \
            reduction_util.calculate_graph_p_factor(graph)

    def is_applicable(self, graph):
        return reductor.is_applicable(graph)

    def dispose(self):
        pass