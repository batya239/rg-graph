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

symbolic_functions.UNKNOWN = symbolic_functions.var('UNKNOWN')
THREE_LOOP_REDUCTOR_D6 = None
THREE_LOOP_REDUCTOR_D6 = reductor.Reductor("loop3",
                               "loop3D6",
                               [graphine.Graph.fromStr("e12|34|35|4|5|e|"),
                                graphine.Graph.fromStr("e12|34|34|5|5|e|"),
                                graphine.Graph.fromStr("e12|23|4|45|5|e|")],
                               3,
                               {graphine.Graph.fromStr("e12|34|34|5|5|e|"):
                                    # symbolic_functions.evaluate(
                                    #     "UNKNOWN"),
                                    symbolic_functions.evaluate(
                                        "(-1/36)*e**(-2)"
                                        "+(-7/72+1/18*zeta(3))*e**(-1)"
                                        "+(-283/1296+1/1080*Pi**4+1/18*zeta(3))"
                                        "+(-1121/7776+1/1080*Pi**4-7/81*zeta(3)-4/9*zeta(5))*e"
                                        "+(89729/46656+7/9*zeta(3)**2-1/756*Pi**6-7/4860*Pi**4-781/972*zeta(3)-4/9*zeta(5))*e**2"
                                        "+(4337443/279936+7/9*zeta(3)**2-1/756*Pi**6-781/58320*Pi**4-20549/5832*zeta(3)-1373/162*zeta(5)+7/270*Pi**4*zeta(3)-67/6*zeta(7))*e**3"
                                        "+Order(e**4)", strong_to_internal_code=True),
                                graphine.Graph.fromStr("e11|22|33|e|"): G(1, 1) ** 3,
                                graphine.Graph.fromStr("e112|22|e|"): G(1, 1) * G(1, 1) * G(2 - 2 * l, 1),
                                graphine.Graph.fromStr("e11|222|e|"): G(1, 1) * G(1, 1) * G(1 - l, 1),
                                graphine.Graph.fromStr("e1111|e|"): G(1, 1) * G(1 - l, 1) * G(1 - 2 * l, 1),
                                graphine.Graph.fromStr("e12|223|3|e|"):
                                    symbolic_functions.evaluate(
                                        "1/1296*e**(-3)"
                                        "+7/15552*e**(-2)"
                                        "+(-1039/933120)*e**(-1)"
                                        "+(-766657/55987200+7/648*zeta(3))"
                                        "+(-285489611/3359232000+49/7776*zeta(3)+7/38880*Pi**4)*e"
                                        "+(-88537120453/201553920000+35459/466560*zeta(3)+49/466560*Pi**4+7/24*zeta(5))*e**2"
                                        "+(-25186269201119/12093235200000+12981377/27993600*zeta(3)-113/648*zeta(3)**2+35459/27993600*Pi**4+13/17496*Pi**6+49/288*zeta(5))*e**3"
                                        "+(-6814992416469337/725594112000000+3983656471/1679616000*zeta(3)-791/7776*zeta(3)**2+12981377/1679616000*Pi**4+245/54*zeta(7)-113/19440*zeta(3)*Pi**4+91/209952*Pi**6+58897/51840*zeta(5))*e**4"
                                        "+Order(e**5)", strong_to_internal_code=True)},"p","k")



TWO_LOOP_REDUCTOR_D6 = reductor.Reductor("loop2",
                             # "loop2",
                             "loop2D6",
                             [graphine.Graph.fromStr("e12|23|3|e|")],
                             2,
                             {graphine.Graph.fromStr("e111|e|"): G(1, 1) * G(1 - l, 1),
                              graphine.Graph.fromStr("e11|22|e|"): G(1, 1) ** 2}, "p", "k")


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
        return result.evaluate(substitute_sectors=True, _d=6-2*symbolic_functions.e, series_n=5, remove_o=True), \
            reduction_util.calculate_graph_p_factor(graph)

    def is_applicable(self, graph):
        return reductor.is_applicable(graph)

    def dispose(self):
        pass



# reduction_calculator_2loop = ReductionGraphCalculator(2)
# reduction_calculator_3loop = ReductionGraphCalculator(3)
reduction_calculator_23loop = ReductionGraphCalculator(2, 3)
