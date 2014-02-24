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
import configure
import numerators_util
import ir_uv
import const
import smtplib
from rggraphenv import symbolic_functions, graph_calculator, storage, theory, g_graph_calculator, StorageSettings, StoragesHolder
from email.mime.text import MIMEText


class SixLoops2Tails(object):
    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s")
    LOG = logging.getLogger("SixLoops2Tails")
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(logging.StreamHandler())
    LOG.addHandler(logging.FileHandler("6LOOPS_log.txt"))

    def __init__(self, do_r_star=False, calculators=tuple(), calculated_mappings=dict()):
        self._calculator = calculators[0].get_label() if len(calculators) else None
        self._calculated_mappings = calculated_mappings
        graph_calculators_to_use = (g_graph_calculator.GLoopCalculator(const.DIM_PHI4),) + tuple(calculators)
        configure.Configure()\
            .with_k_operation(common.MSKOperation())\
            .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_dimension(const.DIM_PHI4)\
            .with_calculators(*graph_calculators_to_use)\
            .with_storage_holder(StorageSettings("phi4", "main method", "6 loops 2 tails").on_shutdown(revert=True)).configure()
        operator = r.ROperation()
        self._operation = operator.kr_star if do_r_star else operator.kr1

    def start(self, graph_states_to_calculate):
        SixLoops2Tails.LOG.info("start calculation using %s graph_calculator, %s operation" % (self._calculator, self._operation.__name__))
        ms = time.time()
        not_calculated = list()
        for gs in graph_states_to_calculate:
            gs = str(graph_state.GraphState.fromStrOldStyle(gs))[:-2]
            graph = graph_util.graph_from_str(gs, do_init_weight=True)
            try:
                SixLoops2Tails.LOG.info("start evaluate %s" % gs)
                res = self._operation(graph)
                SixLoops2Tails.LOG.info("kr1[%s] = %s" % (gs, res))
                self._calculated_mappings[gs] = res
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
        configure.Configure.clear()


def email(calculated_mappings):
    string = "\n\n".join(map(lambda (g, v): str(g) + " = " + str(v), calculated_mappings.items()))
    msg = MIMEText(string)
    me = "epiq.bear@gmail.com"
    they = ["batya239@gmail.com", "mkompan@gmail.com"]
    msg['Subject'] = '6 loops answers'
    msg['From'] = me
    msg['To'] = ", ".join(they)
    s = smtplib.SMTP('smtp.gmail.com', port=465)
    s.sendmail(me, they, msg.as_string())
    s.quit()


def main():
    reductions_loops = (None, (2,), (2, 3), (2, 3, 4))
    operations = (False, True)

    calculated_mappings = dict()
    current_graphs = SIX_LOOPS
    for config in itertools.product(operations, reductions_loops):
        if config[1] is None:
            calculator = tuple()
        else:
            calculator = (numerators_util.create_calculator(*config[1]),)
        operation = config[0]
        master = SixLoops2Tails(operation, calculator, calculated_mappings)
        current_graphs = master.start(current_graphs)
        master.dispose()
    email(calculated_mappings)

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
