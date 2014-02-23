#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import graphine
from reduction import reductor, reduction_util
from rggraphenv import symbolic_functions
from rggraphenv import abstract_graph_calculator

G = lambda x,y : symbolic_functions.G(x,y, 6-2*symbolic_functions.e)
# d=6-2e
l = 2 - symbolic_functions.e

THREE_LOOP_REDUCTOR_D6 = reductor.Reductor("loop3",
                               "loop3D6",
                               [graphine.Graph.fromStr("e12|34|35|4|5|e|"),
                                graphine.Graph.fromStr("e12|34|34|5|5|e|"),
                                graphine.Graph.fromStr("e12|23|4|45|5|e|")],
                               3,
                               {graphine.Graph.fromStr("e12|34|34|5|5|e|"):
                                    symbolic_functions.evaluate(
                                        "Order(e**-5)"),
                                graphine.Graph.fromStr("e11|22|33|e|"): G(1, 1) ** 3,
                                graphine.Graph.fromStr("e112|22|e|"): G(1, 1) * G(1, 1) * G(2 - 2 * l, 1),
                                graphine.Graph.fromStr("e11|222|e|"): G(1, 1) * G(1, 1) * G(1 - l, 1),
                                graphine.Graph.fromStr("e1111|e|"): G(1, 1) * G(1 - l, 1) * G(1 - 2 * l, 1),
                                graphine.Graph.fromStr("e12|223|3|e|"):
                                    symbolic_functions.evaluate("1/1296*e**(-3)+7/15552*e**(-2)+313817/62208*e**(-1)"
                                                                "+(15150437/414720+7/648*zeta(3))+(14441330803/74649600"
                                                                "+49/7776*zeta(3)+7/38880*Pi**4)*e+(4071059940119/4478976000"
                                                                "-3450385/31104*zeta(3)+7/24*zeta(5)+49/466560*Pi**4)*e**2"
                                                                "+(1081922417840587/268738560000-113/648*zeta(3)**2"
                                                                "-166621117/207360*zeta(3)+49/288*zeta(5)+13/17496*Pi**6"
                                                                "-690077/373248*Pi**4)*e**3+(278092698777237551/16124313600000"
                                                                "-791/7776*zeta(3)**2-158835899483/37324800*zeta(3)"
                                                                "-150985/128*zeta(5)+91/209952*Pi**6+245/54*zeta(7)"
                                                                "-166621117/12441600*Pi**4-113/19440*zeta(3)*Pi**4)*e**4"
                                                                "+Order(e**5)", strong_to_internal_code=True)})



TWO_LOOP_REDUCTOR_D6 = reductor.Reductor("loop2",
                             "loop2D6",
                             [graphine.Graph.fromStr("e12|23|3|e|")],
                             2,
                             {graphine.Graph.fromStr("e111|e|"): G(1, 1) * G(1 - l, 1),
                              graphine.Graph.fromStr("e11|22|e|"): G(1, 1) ** 2})


class ReductionGraphCalculator(abstract_graph_calculator.AbstractGraphCalculator):
    def __init__(self, *reduction_loops):
        self._reduction_loops = reduction_loops

    def get_label(self):
        return "reduction calculator for 2-4 loops"

    def init(self):
        all_reductors = (TWO_LOOP_REDUCTOR_D6, THREE_LOOP_REDUCTOR_D6)
        if not len(self._reduction_loops):
            reductors = all_reductors
        else:
            reductors = filter(lambda r: r.main_loops_condition in self._reduction_loops, all_reductors)
        reductor.initialize(*reductors)

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



reduction_calculator_2loop = ReductionGraphCalculator(2)
# reduction_calculator_3loop = ReductionGraphCalculator(3)
# reduction_calculator_23loop = ReductionGraphCalculator(2, 3)
