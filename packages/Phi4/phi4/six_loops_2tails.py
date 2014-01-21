#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import logging
import graph_state
import graphine
import graph_util
import common
import r
import itertools
import time
import numerators_util
from rggraphenv import symbolic_functions, graph_calculator, storage, theory


class SixLoops2Tails(object):
    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s")
    LOG = logging.getLogger("SixLoops2Tails")
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(logging.StreamHandler())
    LOG.addHandler(logging.FileHandler("log.txt"))

    DESCRIPTION = "6 loops 2 tails"

    def __init__(self, operation, calculator=None):
        self._operation = operation
        self._calculator = calculator
        if calculator is not None:
            graph_calculator.addCalculator(calculator)

    def start(self, graph_states_to_calculate):
        SixLoops2Tails.LOG.info("start calculation using %s graph_calculator, %s operation"
                                           % (self._calculator, self._operation.__name__))
        ms = time.time()
        not_calculated = list()
        for gs in graph_states_to_calculate:
            gs = str(graph_state.GraphState.fromStrOldStyle(gs))[:-2]
            graph = graph_util.graph_from_str(gs, do_init_color=True)
            try:
                SixLoops2Tails.LOG.info("start evaluate %s" % gs)
                res = self._operation(graph,
                                      common.MS_K_OPERATION,
                                      common.DEFAULT_SUBGRAPH_UV_FILTER,
                                      description=SixLoops2Tails.DESCRIPTION,
                                      use_graph_calculator=True)
                SixLoops2Tails.LOG.info("kr1[%s] = %s" % (gs, res))
            except common.CannotBeCalculatedError:
                SixLoops2Tails.LOG.warning("can't calculate %s used %s graph_calculator, %s operation"
                                           % (gs, self._calculator, self._operation.__name__))
                not_calculated.append(gs)
            except StandardError as e:
                SixLoops2Tails.LOG.error("error while calculate %s used %s graph_calculator, %s operation"
                                         % (gs, self._calculator, self._operation.__name__))
                SixLoops2Tails.LOG.exception(e)
                not_calculated.append(gs)
        SixLoops2Tails.LOG.info("calculation with %s graph_calculator, %s operation done in %s, calculated %s graphs"
                                % (self._calculator, self._operation.__name__, (time.time() - ms), (len(graph_states_to_calculate) - len(not_calculated))))
        return not_calculated

    # noinspection PyMethodMayBeStatic
    def dispose(self):
        graph_calculator.dispose()


def main():
    try:
        storage.initStorage(theory.PHI4, symbolic_functions.to_internal_code, graphStorageUseFunctions=True)
        reductions_loops = (None, (2,), (2, 3), (2, 3, 4))
        operations = (r.KR1, r.KRStar_quadratic_divergence)

        current_graphs = SIX_LOOPS
        for config in itertools.product(operations, reductions_loops):
            if config[1] is None:
                calculator = None
            else:
                calculator = numerators_util.create_calculator(*config[1])
            operation = config[0]
            master = SixLoops2Tails(operation, calculator)
            current_graphs = master.start(current_graphs)
    finally:
        storage.closeStorage(revert=True, doCommit=False, commitMessage="6 loops 2 tails")

SIX_LOOPS = (
    "e112-23-34-45-55-e-::",
    "e112-34-355-45-e5--::",
    "e123-e23-34-5-555--::",
    "e123-e23-44-55-55--::",
    "e112-23-34-e5-555--::",
    "e123-e24-34-55-55--::",
    "e123-e45-334-5-55--::",
    "e112-33-e44-55-55--::",
    "e123-245-45-445--e-::",
    "e123-e45-444-555---::",
    "e112-34-e33-5-555--::",
    "e112-34-e34-55-55--::",
    "e112-34-345-45-5-e-::",
    "e112-34-334-5-55-e-::",
    "e112-e3-444-555-5--::",
    "e123-e24-55-445-5--::",
    "e112-23-45-445-5-e-::",
    "e123-234-45-45-5-e-::",
    "e112-23-44-555-e5--::",
    "e123-224-5-445-5-e-::",
    "e112-e3-345-45-55--::",
    "e112-33-445-45-5-e-::",
    "e123-e45-345-45-5--::",
    "e112-34-345-e5-55--::",
    "e112-23-44-e55-55--::",
    "e123-e23-45-45-55--::",
    "e112-34-335-e-555--::",
    "e112-23-34-55-e55--::",
    "e123-e45-445-455---::",
    "e123-234-45-55-e5--::",
    "e112-33-445-e5-55--::",
    "e112-34-e35-45-55--::",
    "e112-23-45-e45-55--::",
    "e112-33-e34-5-555--::",
    "e123-e24-33-5-555--::",
    "e112-23-e4-455-55--::",
    "e112-33-e45-45-55--::",
    "e112-e3-445-455-5--::",
    "e123-e24-35-45-55--::",
    "e112-34-355-e4-55--::",
    "e123-e45-344-55-5--::",
    "e112-34-e55-445-5--::",
    "e112-33-444-55-5-e-::",
    "e123-224-4-555-e5--::",
    "e112-33-344-5-55-e-::",
    "e112-e3-334-5-555--::",
    "e112-23-44-455-5-e-::",
    "e112-34-335-4-55-e-::",
    "e112-34-335-5-e55--::",
    "e112-e3-344-55-55--::"
)

if __name__ == "__main__":
    main()
