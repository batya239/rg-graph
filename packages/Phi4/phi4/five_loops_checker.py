#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

#
#
# class checks 5-loops diagrams (primary recall checking, precision only with 4 loops reduction)
#
#
import logging
import graphine
import graph_state
import r
import common
import graph_util
import time
import numerators_util
import itertools
from rggraphenv import symbolic_functions, storage, theory, graph_calculator


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


class ResultChecker(object):
    EPS = 10E-5
    LOG = logging.getLogger("ResultChecker")
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(logging.StreamHandler())

    TWO_TAILS_OPERATION = ("KR1", r.KR1), ("KR_STAR", r.KRStar_quadratic_divergence)
    FOUR_TAILS_OPERATION = ("KR1", r.KR1), ("KR_STAR", r.KRStar)

    CALCULATED_OPERATIONS = dict({2: TWO_TAILS_OPERATION, 4: FOUR_TAILS_OPERATION})

    DESCRIPTION = "5 loops checking"

    def __init__(self, name, *graph_calculators_to_use):
        self._name = name
        storage.initStorage(theory.PHI4, symbolic_functions.to_internal_code, graphStorageUseFunctions=True)
        for c in graph_calculators_to_use:
            graph_calculator.addCalculator(c)

    def start(self, skip_2_tails=False, skip_4_tails=False):
        ResultChecker.LOG.info("start checking \"%s\"" % self._name)
        ms = time.time()

        two_tails_expected = list()
        for state_str, value in MS.iteritems():
            state_str = str(graph_state.GraphState.fromStrOldStyle(state_str))[:-2]
            graph = graph_util.graph_from_str(state_str, do_init_color=True)
            if graph.externalEdgesCount() == 2:
                two_tails_expected.append((graph, value))
                continue
            if skip_4_tails:
                continue
            ResultChecker.LOG.info("PERFORM %s", graph)
            momentum_passed_graphs = graphine.momentum.arbitrarilyPassMomentumWithPreferable(graph, common.defaultGraphHasNotIRDivergence)
            operations = ResultChecker.CALCULATED_OPERATIONS[graph.externalEdgesCount()]
            calculated_count, not_calculated_count, errors_count = 0, 0, 0
            for graphs, oper in zip(momentum_passed_graphs, operations):
                operation_name = oper[0]
                operation_fun = oper[1]
                for g in graphs:
                    try:
                        ResultChecker.LOG.info("TRY %s", g)
                        kr1 = operation_fun(g,
                                            common.MS_K_OPERATION,
                                            common.DEFAULT_SUBGRAPH_UV_FILTER,
                                            description=ResultChecker.DESCRIPTION,
                                            use_graph_calculator=True)
                        if kr1 is not None:
                            if symbolic_functions.check_series_equal_numerically(kr1, value, symbolic_functions.e, ResultChecker.EPS):
                                ResultChecker.LOG.info("%s OK %s" % (operation_name, g))
                                calculated_count += 1
                            else:
                                ResultChecker.LOG.error("%s WRONG RESULT %s ACTUAL=(%s), EXPECTED=(%s)" % (operation_name, g, kr1, value))
                                errors_count += 1
                        else:
                            raise AssertionError()
                    except common.CannotBeCalculatedError:
                        ResultChecker.LOG.warning("CAN'T CALCULATE WITH %s %s" % (operation_name, g))
                        not_calculated_count += 1
            ResultChecker.LOG.info("DONE %s %s calculated_count: %s, not_calculated_count: %s, errors_count: %s" %
                                   (graph, "OK" if calculated_count > 0 else "NOT OK", calculated_count, not_calculated_count, errors_count))

        if not skip_2_tails:
            two_tails_expected.sort(cmp=lambda p1, p2: cmp(p1[0].getLoopsCount(), p2[0].getLoopsCount()))
            for graph, value in two_tails_expected:
                ResultChecker.kr_star_p2_checking(graph, value)

        ResultChecker.LOG.info("checker \"%s\" finished in %s" % (self._name, time.time() - ms))

    @staticmethod
    def kr_star_p2_checking(graph, expected_result):
        """
        used only for checking -- for any subgraph
        """
        diff = diff_util.diff_p2(graph)
        result = 0
        for c, g in diff:
            momentum_passed_graphs = graphine.momentum.arbitrarilyPassMomentumWithPreferable(g, common.defaultGraphHasNotIRDivergence)
            kr1_results = list()
            for graphs, oper in zip(momentum_passed_graphs, ResultChecker.FOUR_TAILS_OPERATION):
                operation_name = oper[0]
                operation_fun = oper[1]
                for g in graphs:
                    try:
                        ResultChecker.LOG.info("TRY %s", g)
                        kr1 = operation_fun(g,
                                            common.MS_K_OPERATION,
                                            common.DEFAULT_SUBGRAPH_UV_FILTER,
                                            description=ResultChecker.DESCRIPTION,
                                            use_graph_calculator=True)
                        if kr1 is not None:
                            kr1_results.append(kr1)
                        else:
                            raise AssertionError()
                    except common.CannotBeCalculatedError:
                        ResultChecker.LOG.warning("CAN'T CALCULATE WITH %s %s" % (operation_name, g))
            if len(kr1_results):
                all_equal = True
                for res1, res2 in pairwise(kr1_results):
                    if not symbolic_functions.check_series_equal_numerically(res1, res2, symbolic_functions.e, ResultChecker.EPS):
                        all_equal = False
                if not all_equal:
                    ResultChecker.LOG.error("KR1 OR KR STAR WRONG RESULT %s" % g)
                    return
            else:
                ResultChecker.LOG.warning("CAN'T CALCULATE %s" % graph)
                return
            result += k_operation.calculate(c * kr1_results[0])
        if symbolic_functions.check_series_equal_numerically(expected_result, result, symbolic_functions.e, ResultChecker.EPS):
            ResultChecker.LOG.info("OK %s", graph)
        else:
            ResultChecker.LOG.error("P2 WRONG RESULT %s ACTUAL=(%s), EXPECTED=(%s)" % (graph, result, expected_result))

    @staticmethod
    def dispose():
        storage.closeStorage(revert=True, doCommit=False, commitMessage="5loops checking 4 tails")
        graph_calculator.dispose()


def main():
    checkers_configuration = ("no calculators checker", []),#, \
                             #("with 2 loops reduction checker", [numerators_util.create_calculator(2)]), \
                             #("with 2, 3 loops reduction checker", [numerators_util.create_calculator(2, 3)]), \
                             #("with 2-4 loops reduction checker", [numerators_util.create_calculator(2, 3, 34)])

    for conf in checkers_configuration:
        checker = ResultChecker(conf[0], *conf[1])
        try:
            checker.start()
        finally:
            checker.dispose()


zeta = symbolic_functions.zeta
e = 2 * symbolic_functions.e

MS = {
    'e111-e-':(-0.5/e),
    'ee11-ee-':(2./e),
    'ee11-22-ee-':(-4./e**2),
    'ee12-e22-e-':(1./e-2./e/e),
    'e112-22-e-':(-1./6/e+2./3/e/e),

    'ee11-22-33-ee-':(8./e**3),
    'ee11-23-e33-e-':(-2/e**2+4./e**3),
    'ee12-ee3-333--':(-3./4/e+2./3/e**2),
    'e123-e23-e3-e-':(4.*zeta(3)/e),
    'ee12-e33-e33--':(-2./3/e-4./3/e**2+8./3/e**3),
    'e112-e3-e33-e-':(-2./3/e-4./3/e**2+8./3/e**3),
    'ee12-e23-33-e-':(4./3/e-2./e**2+4./3/e**3),
    'ee12-223-3-ee-':(2./3/e-8./3/e**2+8./3/e**3),

    'ee11-22-33-44-ee-':(-16./e**4),
    'ee11-22-34-e44-e-':(4./e**3-8./e**4),
    'e112-e2-34-e44-e-':(-1./e**2+4./e**3-4./e**4),
    'ee11-23-e44-e44--':(4./3/e**2+8./3/e**3-16./3/e**4),
    'ee11-23-ee4-444--':(3./2/e**2-4./3/e**3),
    'ee11-23-e34-44-e-':(-8./3./e**2+4./e**3-8./3/e**4),
    'ee11-23-334-4-ee-':(-4./3./e**2+16./3/e**3-16./3/e**4),
    'ee12-233-34-4-ee-':((11./6-zeta(3))/e-13./3./e**2+10./3/e**3-4./3/e**4),
    'ee12-223-4-e44-e-':(-0.5/e**1+1./6/e**2+10./3/e**3-10./3/e**4),
    #4x 4l-10
    'e123-e24-34-e4-e-':(10*zeta(5)/e),

    'e112-34-e34-e4-e-':((3*zeta(3)-1.5*zeta(4))/e**1-2*zeta(3)/e**2),
    'e112-e3-e34-44-e-':(-2./3/e**1-5./6/e**2+8./3/e**3-2./e**4),
    'e112-e3-e44-e44--':((0.5-zeta(3))/e+1./e**2+2./e**3-4./e**4),
    'ee12-334-334--ee-':(-(2-2*zeta(3))/e+4./3/e**2+8./3/e**3-8./3./e**4),
    'ee12-ee3-344-44--':(-7./12/e+1./e**2-2./3/e**3),
    'ee12-e23-e4-444--':(-121./96/e+11./8/e**2-1./2/e**3),
    'ee12-e34-e34-44--':(-(1-2*zeta(3))/e-5./3/e**2+8./3/e**3-4./3/e**4),
    'ee12-e33-e44-44--':((0.5-zeta(3))/e+1./e**2+2./e**3-4./e**4),
    'ee12-e33-444-e4--':(37./96/e+5./8/e**2-5./6/e**3),
    'ee12-233-44-e4-e-':(-(5./6 -zeta(3))/e-1./3/e**2+2./e**3-4./3/e**4),

    'ee12-234-34-e4-e-':((3*zeta(3)+1.5*zeta(4))/e-6.*zeta(3)/e**2),
    'ee12-334-344-e-e-':(-5./6/e-1./3/e**2+2./e**3-4./3/e**4),
    'ee12-e33-344-4-e-':(-2./3/e-5./6/e**2+8./3/e**3-2./e**4),
    'ee12-e23-44-e44--':(-(5./6-zeta(3))/e-1./3/e**2+2./e**3-4./3/e**4),
    'ee12-e34-334-4-e-':((5./2-2*zeta(3))/e-19./6/e**2+2./e**3-2./3/e**4),
    'ee12-e23-34-44-e-':(5./2/e-19./6/e**2+2./e**3-2./3/e**4),
    #2x 4l

    'e112-33-e33--':(5./16/e+1./4/e**2-1./e**3),
    'e112-e3-333--':(5./16/e-1./8/e**2),
    'e123-e23-33--':(-13./48/e+7./12/e**2-1./3/e**3),
    'e112-23-33-e-':(-2./3/e+2./3/e**2-2./3/e**3),

    #4x 5l
    'e123-e45-e45-e45-5--':(72./5*zeta(3)**2/e),
    'e123-e23-45-45-e5-e-':(72./5*zeta(3)**2/e),
    'e123-e24-35-45-e5-e-':(441./20*zeta(7)/e),
    'ee12-e23-44-555-e5--':(-(2./5*zeta(3)-103./160)/e+37./240/e/e-19./20/e/e/e+7./15/e/e/e/e),
    'ee12-e34-335-e-555--':((103./160)/e+37./240/e/e-19./20/e/e/e+7./15/e/e/e/e),
    'ee12-333-445-5-e5-e-':(-(11./192)/e+33./80/e/e-11./12/e/e/e+3./5/e/e/e/e),
    'ee11-22-34-ee5-555--':(-3./e/e/e+8./3/e/e/e/e),
    'ee11-23-444-455--ee-':(-3./e/e/e+8./3/e/e/e/e),
    'ee12-333-345--e55-e-':(3./4/e/e-13./6/e/e/e+4./3/e/e/e/e),
    #10
    'ee12-e33-e34-5-555--':(151./192/e + 197./240/e/e - 103./60/e/e/e + 11./15/e/e/e/e),
    'e112-e3-e44-555-e5--':((2./5*zeta(3)-151./480)/e-53./120/e/e-23./30/e/e/e + 6./5/e/e/e/e),
    'ee12-e34-555-e44-5--':(-(11./192)/e+33./80/e/e-11./12/e/e/e+3./5/e/e/e/e),
    'e123-e23-e4-e5-555--':((3./5*zeta(4)-27./10*zeta(3))/e+4./5*zeta(3)/e/e),
    'ee12-333-444-5-5-ee-':(-(5./96)/e-3./10/e/e+4./15/e/e/e),
    'ee12-ee3-334-5-555--':((857./960)/e-13./20/e/e+2./15/e/e/e),
    'ee12-e23-34-e5-555--':(-(2387./960)/e+41./15/e/e-13./10/e/e/e+4./15/e/e/e/e),
    'e112-e3-e34-e5-555--':(151./192/e + 197./240/e/e - 103./60/e/e/e + 11./15/e/e/e/e),
    'ee11-23-e34-e5-555--':( 121./48/e/e - 11./4/e/e/e + 1./e/e/e/e),
    'ee12-234-35-ee-555--':( -215./96/e + 25./6/e/e - 7./3/e/e/e + 8./15/e/e/e/e),
    #20
    'ee12-e33-444-55-5-e-':((2./5*zeta(3)-151./480)/e-53./120/e/e-23./30/e/e/e + 6./5/e/e/e/e),
    'ee12-223-4-ee5-555--':((157./320)/e-11./60/e/e-7./5/e/e/e + 16./15/e/e/e/e),
    'ee11-23-e44-555-e5--':(-37./48/e/e-5./4/e/e/e+5./3/e/e/e/e),
    'ee12-ee3-444-555-5--':(-(5./96)/e-3./10/e/e+4./15/e/e/e),
    #24
    'e112-34-e35-45-e5-e-':(-(5*zeta(6)-10*zeta(5)-2./5*zeta(3)**2)/e-4*zeta(5)/e/e),
    'e123-e24-55-e45-e5--':(-(5*zeta(6)-10*zeta(5)+22./5*zeta(3)**2)/e-4*zeta(5)/e/e),
    'ee12-234-35-45-e5-e-':((5*zeta(6)+6*zeta(5)-2./5*zeta(3)**2)/e-16*zeta(5)/e/e),
    'e112-34-345-e5-e5-e-':(-(5*zeta(6)-10*zeta(5)+2*zeta(3)**2)/e-4*zeta(5)/e/e),
    'e123-e45-e45-445--e-':(-(5*zeta(6)-10*zeta(5)+34./5*zeta(3)**2)/e-4*zeta(5)/e/e),
    'ee12-345-345-e4-5-e-':((5*zeta(6)+6*zeta(5)-14./5*zeta(3)**2)/e-16*zeta(5)/e/e),
    #30
    'e112-33-e45-45-e5-e-':((14./5*zeta(5)-9./5*zeta(4)+2./5*zeta(3))/e+(6./5*zeta(4)-12./5*zeta(3))/e/e+8./5*zeta(3)/e/e/e),
    'ee11-23-345-45-e5-e-':(-(3*zeta(4)+6*zeta(3))/e/e+12.*zeta(3)/e/e/e),
    'ee12-234-34-45-5-ee-':(-(16./5*zeta(5)-9./5*zeta(4)-14./5*zeta(3))/e-(24./5*zeta(4)+48./5*zeta(3))/e/e+48./5*zeta(3)/e/e/e),
    'e112-23-45-e45-e5-e-':((7./5*zeta(5)-21./10*zeta(4)+31./5*zeta(3))/e+(3./5*zeta(4)-14./5*zeta(3))/e/e+4./5*zeta(3)/e/e/e),
    'e123-e24-e5-e45-55--':(-(23./5*zeta(5)+21./10*zeta(4)-31./5*zeta(3))/e+(3./5*zeta(4)-14./5*zeta(3))/e/e+4./5*zeta(3)/e/e/e),
    'e112-e3-345-45-e5-e-':(-(7./5*zeta(5)-3./10*zeta(4)+13./5*zeta(3))/e-(3./5*zeta(4)+18./5*zeta(3))/e/e+36./5*zeta(3)/e/e/e),
    'ee12-e34-345-45-5-e-':(-(23./5*zeta(5)-21./10*zeta(4)-5.*zeta(3))/e-(12./5*zeta(4)+36./5*zeta(3))/e/e+24./5*zeta(3)/e/e/e),
    'ee12-334-345-5-e5-e-':(-(24./5*zeta(5)-16./5*zeta(3))/e+(9./5*zeta(4)-6.*zeta(3))/e/e+12./5*zeta(3)/e/e/e),
    'ee12-234-35-e4-55-e-':((6./5*zeta(5)+16./5*zeta(3))/e+(9./5*zeta(4)-6.*zeta(3))/e/e+12./5*zeta(3)/e/e/e),
    'e112-34-e35-e5-e55--':(-(6./5*zeta(5)+9./5*zeta(4)-2./5*zeta(3))/e+(6./5*zeta(4)-12./5*zeta(3))/e/e+8./5*zeta(3)/e/e/e),
    #40
    'e112-34-e34-e5-55-e-':(-(16./5*zeta(5)+9./5*zeta(4)-2./5*zeta(3))/e+(6./5*zeta(4)-12./5*zeta(3))/e/e+8./5*zeta(3)/e/e/e),
    'e112-34-e55-e45-e5--':((14./5*zeta(5)-9./5*zeta(4)+2./5*zeta(3))/e+(6./5*zeta(4)-12./5*zeta(3))/e/e+8./5*zeta(3)/e/e/e),
    'ee12-234-34-e5-55-e-':((16./5*zeta(5)+16./5*zeta(3))/e+(9./5*zeta(4)-6.*zeta(3))/e/e+12./5*zeta(3)/e/e/e),
    'ee12-233-45-45-e5-e-':(-(14./5*zeta(5)-16./5*zeta(3))/e+(9./5*zeta(4)-6.*zeta(3))/e/e+12./5*zeta(3)/e/e/e),
    'e112-34-e35-e4-55-e-':(-(6./5*zeta(5)+9./5*zeta(4)-2./5*zeta(3))/e+(6./5*zeta(4)-12./5*zeta(3))/e/e+8./5*zeta(3)/e/e/e),
    'e112-23-e4-e55-e55--':((3./10*zeta(4)-zeta(3)+3./5)/e+(2./5*zeta(3)+3./5)/e/e+4./5/e/e/e-4./e/e/e/e+16./5/e/e/e/e/e),
    'ee11-23-e34-45-55-e-':(-5./e/e+19./3/e/e/e-4./e/e/e/e+4./3/e/e/e/e/e),
    'ee12-234-35-44-5-ee-':(-(3./10*zeta(4)+3*zeta(3)-73./15)/e+(18./5*zeta(3)-9)/e/e+6./e/e/e-12./5/e/e/e/e+8./15/e/e/e/e/e),
    'ee11-23-e45-445-5-e-':((4.*zeta(3)-5.)/e/e+19./3/e/e/e-4./e/e/e/e+4./3/e/e/e/e/e),
    'e112-e3-e34-55-e55--':(-(3./10*zeta(4)+1./5*zeta(3))/e-(2./5*zeta(3)-19./15)/e/e-44./15/e/e/e/e+32./15/e/e/e/e/e),
    #50
    'ee12-e23-34-55-e55--':((3./10*zeta(4)+9./5*zeta(3)-2./5)/e-(8./5*zeta(3)+4./15)/e/e+26./15/e/e/e-8./5/e/e/e/e+8./15/e/e/e/e/e),
    'ee12-e34-355-e4-55--':((3./2*zeta(4)-3./5*zeta(3)-2./5)/e-(4./15)/e/e+26./15/e/e/e-8./5/e/e/e/e+8./15/e/e/e/e/e),
    'e112-23-e4-e45-55-e-':((8./15)/e-(8./15)/e/e+34./15/e/e/e-16./5/e/e/e/e+8./5/e/e/e/e/e),
    'ee12-e34-355-45-e5--':((3./5*zeta(4)-26./5*zeta(3)+28./5)/e+(4./5*zeta(3)-19./3)/e/e+11./3/e/e/e-4./3/e/e/e/e+4./15/e/e/e/e/e),
    'ee12-e23-34-45-55-e-':((28./5)/e-(19./3)/e/e+11./3/e/e/e-4./3/e/e/e/e+4./15/e/e/e/e/e),
    'e112-e3-e45-445-5-e-':((3./5*zeta(4)-2./5*zeta(3)-28./15)/e+(4./5*zeta(3)-19./15)/e/e+56./15/e/e/e-44./15/e/e/e/e+16./15/e/e/e/e/e),
    'ee12-e33-345-4-55-e-':(-(28./15)/e-(19./15)/e/e+56./15/e/e/e-44./15/e/e/e/e+16./15/e/e/e/e/e),
    'ee12-e23-44-455-5-e-':(-(3./10*zeta(4)-7./5*zeta(3)+4./3)/e-(2./5*zeta(3)+2./15)/e/e+11./5/e/e/e-32./15/e/e/e/e+4./5/e/e/e/e/e),
    'ee12-e34-335-5-e55--':((3./10*zeta(4)-3./5*zeta(3)-4./3)/e+(2./5*zeta(3)-2./15)/e/e+11./5/e/e/e-32./15/e/e/e/e+4./5/e/e/e/e/e),
    'ee12-e33-445-45-5-e-':((3./5*zeta(4)-2./5*zeta(3)-28./15)/e+(4./5*zeta(3)-19./15)/e/e+56./15/e/e/e-44./15/e/e/e/e+16./15/e/e/e/e/e),
    #60
    'e112-e3-e44-455-5-e-':((3./10*zeta(4)-zeta(3)+3./5)/e+(2./5*zeta(3)+3./5)/e/e+4./5/e/e/e-4./e/e/e/e+16./5/e/e/e/e/e),
    'ee12-233-34-5-e55-e-':((3./10*zeta(4)-1./5*zeta(3)-11./15)/e+(2./5*zeta(3)-4./15)/e/e+61./15/e/e/e-64./15/e/e/e/e+28./15/e/e/e/e/e),
    'ee12-223-4-e45-55-e-':((-16./15)/e+(7./15)/e/e+43./15/e/e/e-68./15/e/e/e/e+12./5/e/e/e/e/e),
    'ee12-233-45-e4-55-e-':(-(3./10*zeta(4)-7./5*zeta(3)+4./3)/e-(2./5*zeta(3)+2./15)/e/e+11./5/e/e/e-32./15/e/e/e/e+4./5/e/e/e/e/e),
    'ee12-e34-335-4-55-e-':((9./10*zeta(4)-9./5*zeta(3)-2./5)/e+(-4./5*zeta(3)-4./15)/e/e+26./15/e/e/e-8./5/e/e/e/e+8./15/e/e/e/e/e),
    'ee12-334-355-4-e5-e-':((3./10*zeta(4)-3./5*zeta(3)-4./3)/e+(2./5*zeta(3)-2./15)/e/e+11./5/e/e/e-32./15/e/e/e/e+4./5/e/e/e/e/e),
    'e112-e3-344-55-e5-e-':(-(3./10*zeta(4)+1./5*zeta(3))/e-(2./5*zeta(3)-19./15)/e/e-44./15/e/e/e/e+32./15/e/e/e/e/e),
    'ee12-e34-334-5-55-e-':((3./5*zeta(4)-6./5*zeta(3)-2./5)/e+(4./5*zeta(3)-4./15)/e/e+26./15/e/e/e-8./5/e/e/e/e+8./15/e/e/e/e/e),
    'e112-e3-445-455-e-e-':((19./15)/e/e-(44./15)/e/e/e/e+32./15/e/e/e/e/e),
    'ee12-334-455-e5-e5--':((3./5*zeta(4)+2./5*zeta(3)-4./3)/e+(4./5*zeta(3)-2./15)/e/e+11./5/e/e/e-32./15/e/e/e/e+4./5/e/e/e/e/e),
    #70
    'ee12-334-345-e-55-e-':(-(4./3)/e-(2./15)/e/e+11./5/e/e/e-32./15/e/e/e/e+4./5/e/e/e/e/e),
    'ee12-334-355-e-e55--':(-(3./5*zeta(4)+4./5*zeta(3)-3./5)/e+(6./5*zeta(3)+1./5)/e/e+2./5/e/e/e-12./5/e/e/e/e+8./5/e/e/e/e/e),
    'ee11-23-445-455-e-e-':((5./3)/e/e+(2./3)/e/e/e-4./e/e/e/e+8./3/e/e/e/e/e),
    'ee12-334-344-5-5-ee-':((3./5*zeta(4)+2./5*zeta(3)-16./15)/e+(4./5*zeta(3)+6./5)/e/e+28./15/e/e/e-8./3/e/e/e/e+16./15/e/e/e/e/e),
    'ee12-e23-45-445-5-e-':(-(3./5*zeta(4)+14./5*zeta(3)-28./5)/e+(16./5*zeta(3)-19./3)/e/e+11./3/e/e/e-4./3/e/e/e/e+4./15/e/e/e/e/e),
    'ee12-e34-345-e5-55--':(-(16./5*zeta(3)-28./5)/e-(-4.*zeta(3)+19./3)/e/e+11./3/e/e/e-4./3/e/e/e/e+4./15/e/e/e/e/e),
    'e112-e3-e34-45-55-e-':(-(28./15)/e-(19./15)/e/e+56./15/e/e/e-44./15/e/e/e/e+16./15/e/e/e/e/e),
    'e112-23-e4-455-e5-e-':((8./15)/e-(8./15)/e/e+34./15/e/e/e-16./5/e/e/e/e+8./5/e/e/e/e/e),
    'ee11-23-e44-e55-55--':((2.*zeta(3)-1)/e/e-2./e/e/e-4./e/e/e/e+8./e/e/e/e/e),
    'ee12-334-455-55-ee--':(-(12./5*zeta(4)-6./5*zeta(3)-7./5)/e+(4./5*zeta(3)+4./5)/e/e-8./5/e/e/e-16./5/e/e/e/e+16./5/e/e/e/e/e),
    #80
    'ee11-22-34-e55-e55--':(-8./3/e/e/e-16./3/e/e/e/e+32./3/e/e/e/e/e),
    'ee11-23-445-445--ee-':(-(4.*zeta(3)-4)/e/e-8./3/e/e/e-16./3/e/e/e/e+16./3/e/e/e/e/e),
    'ee12-e23-44-e55-55--':(-(6./5*zeta(4)-2./5*zeta(3)-3./5)/e+(2./5*zeta(3)+1./5)/e/e+2./5/e/e/e-12./5/e/e/e/e+8./5/e/e/e/e/e),
    'ee11-22-34-e45-55-e-':(16./3/e/e/e-8./e/e/e/e+16./3/e/e/e/e/e),
    'ee11-23-344-45-5-ee-':((2*zeta(3)-11./3)/e/e+26./3/e/e/e-20./3/e/e/e/e+8./3/e/e/e/e/e),
    'ee12-e33-e44-55-55--':((6./5*zeta(4)-4./5*zeta(3)-2./5)/e+(8./5*zeta(3)-4./5)/e/e-8./5/e/e/e-16./5/e/e/e/e+32./5/e/e/e/e/e),
    'ee12-233-44-e5-55-e-':(-(6./5*zeta(4)-2./5*zeta(3)-3./5)/e+(2./5*zeta(3)+1./5)/e/e+2./5/e/e/e-12./5/e/e/e/e+8./5/e/e/e/e/e),
    'ee11-23-344-55-e5-e-':(-(2.*zeta(3)-5./3)/e/e+2./3/e/e/e-4./e/e/e/e+8./3/e/e/e/e/e),
    'ee12-233-44-45-5-ee-':((6./5*zeta(4)-16./15)/e-(12./5*zeta(3)-6./5)/e/e+28./15/e/e/e-8./3/e/e/e/e+16./15/e/e/e/e/e),
    'ee12-e33-344-5-55-e-':(-(3./10*zeta(4)+1./5*zeta(3))/e-(2./5*zeta(3)-19./15)/e/e-44./15/e/e/e/e+32./15/e/e/e/e/e),
    #90
    'ee11-23-e44-455-5-e-':((4./3)/e/e+5./3/e/e/e-16./3/e/e/e/e+4./e/e/e/e/e),
    'ee12-334-335--e55-e-':(-(9./10*zeta(4)-1./5*zeta(3)-22./15)/e+(4./5*zeta(3)+4./5)/e/e-22./15/e/e/e-56./15/e/e/e/e+56./15/e/e/e/e/e),
    'ee12-223-4-e55-e55--':(-(3./10*zeta(4)+3./5*zeta(3)-1./3)/e+(8./5*zeta(3)-2./15)/e/e-2./15/e/e/e-24./5/e/e/e/e+24./5/e/e/e/e/e),
    'ee12-334-355-5-ee5--':(-(3./10*zeta(4)-11./5*zeta(3)+14./5)/e-(2./5*zeta(3)-29./15)/e/e+34./15/e/e/e-52./15/e/e/e/e+8./5/e/e/e/e/e),
    'ee11-23-e34-55-e55--':(-(2.*zeta(3)-5./3)/e/e+2./3/e/e/e-4./e/e/e/e+8./3/e/e/e/e/e),
    'ee12-233-45-44-5-ee-':((6./5*zeta(4)-16./15)/e-(12./5*zeta(3)-6./5)/e/e+28./15/e/e/e-8./3/e/e/e/e+16./15/e/e/e/e/e),
    'e112-33-e44-e5-55-e-':((6./5*zeta(4)-4./5*zeta(3)-2./5)/e+(8./5*zeta(3)-4./5)/e/e-8./5/e/e/e-16./5/e/e/e/e+32./5/e/e/e/e/e),
    'ee12-e23-e4-455-55--':(-(1./5*zeta(3)+841./480)/e+(49./24)/e/e-13./10/e/e/e+2./5/e/e/e/e),
    'ee12-ee3-345-45-55--':(-(4./5*zeta(3)+193./480)/e+(19./15)/e/e-14./15/e/e/e+4./15/e/e/e/e),
    'ee11-23-ee4-455-55--':((7./6)/e/e+(-2.)/e/e/e+4./3/e/e/e/e),
    #100
    'ee12-ee3-344-55-55--':(-(3./10*zeta(3)-81./160)/e+(1./5)/e/e-6./5/e/e/e+4./5/e/e/e/e),
    'ee12-e34-355-44-5-e-':(-(3./5*zeta(4)-8./5*zeta(3)+2./3)/e-(4./5*zeta(3)-4./3)/e/e+1./e/e/e-8./3/e/e/e/e+4./3/e/e/e/e/e),
    'ee12-334-455-e4-5-e-':((8./15)/e-(8./15)/e/e+34./15/e/e/e-16./5/e/e/e/e+8./5/e/e/e/e/e),
    'e112-e3-334-5-e55-e-':((8./15)/e+(6./5)/e/e-4./3/e/e/e-64./15/e/e/e/e+64./15/e/e/e/e/e),
    'ee12-e33-445-55-e5--':((3./10*zeta(4)-zeta(3)+3./5)/e+(2./5*zeta(3)+3./5)/e/e+4./5/e/e/e-4./e/e/e/e+16./5/e/e/e/e/e),
    'ee11-23-334-5-e55-e-':((1.)/e/e-1./3/e/e/e-20./3/e/e/e/e+20./3/e/e/e/e/e),
    'ee12-223-4-445-5-ee-':(-2./15/e+(16./15)/e/e+8./5/e/e/e-32./5/e/e/e/e+64./15/e/e/e/e/e),
    'ee12-e34-e34-55-55--':(-(3./5*zeta(4)-28./5*zeta(3)+17./3)/e-(24./5*zeta(3)-24./5)/e/e-4./15/e/e/e-32./15/e/e/e/e+16./15/e/e/e/e/e),
    'ee11-23-e45-e45-55--':(-(4.*zeta(3)-2)/e/e+10./3/e/e/e-16./3/e/e/e/e+8./3/e/e/e/e/e),
    'ee12-345-345-ee-55--':((3./5*zeta(4)+28./5*zeta(3)-101./15)/e-(36./5*zeta(3)-52./15)/e/e+16./5/e/e/e-16./5/e/e/e/e+16./15/e/e/e/e/e),
    #110
    'e112-e2-34-e55-e55--':(2./3/e/e-16./3/e/e/e/e+16./3/e/e/e/e/e),
    'ee12-e34-e35-45-55--':(-(9./10*zeta(4)-9./5*zeta(3)+13./15)/e+(4./5*zeta(3)-58./15)/e/e+22./5/e/e/e-32./15/e/e/e/e+8./15/e/e/e/e/e),
    'e112-e3-e45-e45-55--':(-(3./10*zeta(4)+zeta(3)-29./15)/e-(2./5*zeta(3)-1./3)/e/e+32./15/e/e/e-4./e/e/e/e+32./15/e/e/e/e/e),
    'ee12-e23-45-e45-55--':((3./10*zeta(4)+23./5*zeta(3)-18./5)/e-(18./5*zeta(3)-7./15)/e/e+38./15/e/e/e-28./15/e/e/e/e+8./15/e/e/e/e/e),
    'e112-e2-34-e45-55-e-':(-4./3/e/e+14./3/e/e/e-16./3/e/e/e/e+8./3/e/e/e/e/e),
    'ee12-e33-445-e5-55--':((1./5*zeta(3)+293./480)/e+1./40/e/e-11./10/e/e/e+14./15/e/e/e/e),
    'ee12-ee3-445-455-5--':((4./5*zeta(3)-25./12)/e+32./15/e/e-4./3/e/e/e+8./15/e/e/e/e),
    'ee11-22-33-44-55-ee-':(32./e/e/e/e/e),
    'e112-e3-e44-e55-55--':((6./5*zeta(4)-4./5*zeta(3)-2./5)/e+(8./5*zeta(3)-4./5)/e/e-8./5/e/e/e-16./5/e/e/e/e+32./5/e/e/e/e/e),
    'ee11-22-33-45-e55-e-':(-8./e/e/e/e+16./e/e/e/e/e),
    #120
    'ee11-22-34-445-5-ee-':(8./3/e/e/e-32./3/e/e/e/e+32./3/e/e/e/e/e),
    'ee11-23-334-4-55-ee-':(8./3/e/e/e-32./3/e/e/e/e+32./3/e/e/e/e/e),
    'e112-e2-33-45-e55-e-':(2./e/e/e-8./e/e/e/e+8./e/e/e/e/e),
    'ee12-e33-e45-45-55--':(-(3./10*zeta(4)+zeta(3)-29./15)/e-(2./5*zeta(3)-1./3)/e/e+32./15/e/e/e-4./e/e/e/e+32./15/e/e/e/e/e),
    'ee12-223-3-45-e55-e-':(-(2./3)/e/e+4./e/e/e-8./e/e/e/e+16./3/e/e/e/e/e),



    #2x 5l
    'e112-33-e44-44--':((2./5*zeta(3)-13./40)/e-(1./2)/e/e-2./5/e/e/e+8./5/e/e/e/e),
    'e112-23-e4-444--':((7./64)/e-(23./60)/e/e+11./60/e/e/e),
    'e112-33-444-e4--':((-149./480)/e-(17./60)/e/e+7./30/e/e/e),
    'e112-e3-344-44--':((209./480)/e-(3./10)/e/e+1./10/e/e/e),
    'e112-34-e34-44--':(-(1./10*zeta(3)-13./80)/e+(19./60)/e/e-13./15/e/e/e+8./15/e/e/e/e),
    'e112-23-44-e44--':(-(3./10*zeta(3)-137./480)/e+(11./40)/e/e-9./10/e/e/e+14./15/e/e/e/e),
    'e123-e23-44-44--':(-(6./5*zeta(3)-277./240)/e-(11./60)/e/e-7./15/e/e/e+4./15/e/e/e/e),
    'e123-e24-34-44--':((1./5*zeta(3)-347./480)/e+(39./40)/e/e-1./2/e/e/e+2./15/e/e/e/e),
    'e112-23-34-44-e-':(-(14./15)/e+(22./15)/e/e-16./15/e/e/e+8./15/e/e/e/e),
    #10
    'e112-34-334-4-e-':((3./5*zeta(3)-331./480)/e+(77./120)/e/e-23./30/e/e/e+2./5/e/e/e/e),
    'e123-234-34-4-e-':(-(6./5*zeta(4)+3./5*zeta(3))/e+(12./5*zeta(3))/e/e),
}


if __name__ == "__main__":
    main()