#!/usr/bin/python
# -*- coding: utf8
import unittest
import graph_state
import common
import mincer_adapter
import sympy
import rggraphutil.env.graph_calculator as graph_calculator
import gfunctions.r as r_prime
import rggraphutil.symbolic_functions as symbolic_functions
import graphine.momentum as momentum
import graphine
import base_test_case


__author__ = 'daddy-bear'


class RPrime5LoopsTestCase(base_test_case.GraphStorageAwareTestCase):
    def test5Loops(self):
        graph_calculator.addCalculator(mincer_adapter.MincerGraphCalculator())
        for gs, res in MS.items():
            self._compareRPrime(gs, res, True)

    def _compareRPrime(self, graphStateAsString, expected, useGraphCalculator=False):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr(graphStateAsString)))

        if len(g.edges(g.externalVertex)) == 2:
            withMomentumPassing = g,
        else:
            withMomentumPassing = [x for x in momentum.xPassExternalMomentum(g, common.defaultGraphHasNotIRDivergenceFilter)]
        calculated = False
        for graph in withMomentumPassing:
            print graph
            if calculated:
                break
            try:
                actual = r_prime.KR1(graph, common.MSKOperation(), common.defaultSubgraphUVFilter,
                                     useGraphCalculator=useGraphCalculator)
                sub = expected - actual
                booleanExpression = expected == actual or abs((sub * symbolic_functions._e ** 5).evalf(
                    subs={symbolic_functions._e: 1, symbolic_functions._p: 1})) < 1e-5
                self.assertTrue(booleanExpression, "\nactual = " + str(actual) + "\nexpected = " + str(expected) + "\nsub = " + str(sub))
                if booleanExpression:
                    calculated = True
            except common.CannotBeCalculatedError:
                pass
                print "can't calculate", graph
            except:
                pass
        print "OK " + graphStateAsString if calculated else "FAIL " + graphStateAsString


def main():
    unittest.main()


zeta = sympy.special.zeta_functions.zeta
e = 2 * symbolic_functions._e
MS = {
    'ee12-e34-e34-44--': (-(1 - 2 * zeta(3)) / e - 5. / 3 / e ** 2 + 8. / 3 / e ** 3 - 4. / 3 / e ** 4),

    'e111-e-': (-0.5 / e),
    'ee11-ee-': (2. / e),
    'ee11-22-ee-': (-4. / e ** 2),
    'ee12-e22-e-': (1. / e - 2. / e / e),
    'e112-22-e-': (-1. / 6 / e + 2. / 3 / e / e),

    'ee11-22-33-ee-': (8. / e ** 3),
    'ee11-23-e33-e-': (-2 / e ** 2 + 4. / e ** 3),
    'ee12-ee3-333--': (-3. / 4 / e + 2. / 3 / e ** 2),
    'e123-e23-e3-e-': (4. * zeta(3) / e),
    'ee12-e33-e33--': (-2. / 3 / e - 4. / 3 / e ** 2 + 8. / 3 / e ** 3),
    'e112-e3-e33-e-': (-2. / 3 / e - 4. / 3 / e ** 2 + 8. / 3 / e ** 3),
    'ee12-e23-33-e-': (4. / 3 / e - 2. / e ** 2 + 4. / 3 / e ** 3),
    'ee12-223-3-ee-': (2. / 3 / e - 8. / 3 / e ** 2 + 8. / 3 / e ** 3),

    'ee11-22-33-44-ee-': (-16. / e ** 4),
    'ee11-22-34-e44-e-': (4. / e ** 3 - 8. / e ** 4),
    'e112-e2-34-e44-e-': (-1. / e ** 2 + 4. / e ** 3 - 4. / e ** 4),
    'ee11-23-e44-e44--': (4. / 3 / e ** 2 + 8. / 3 / e ** 3 - 16. / 3 / e ** 4),
    'ee11-23-ee4-444--': (3. / 2 / e ** 2 - 4. / 3 / e ** 3),
    'ee11-23-e34-44-e-': (-8. / 3. / e ** 2 + 4. / e ** 3 - 8. / 3 / e ** 4),
    'ee11-23-334-4-ee-': (-4. / 3. / e ** 2 + 16. / 3 / e ** 3 - 16. / 3 / e ** 4),
    'e123-e24-34-e4-e-': (10 * zeta(5) / e),

    'e112-34-e34-e4-e-': ((3 * zeta(3) - 1.5 * zeta(4)) / e ** 1 - 2 * zeta(3) / e ** 2),
    'e112-e3-e34-44-e-': (-2. / 3 / e ** 1 - 5. / 6 / e ** 2 + 8. / 3 / e ** 3 - 2. / e ** 4),
    'e112-e3-e44-e44--': ((0.5 - zeta(3)) / e + 1. / e ** 2 + 2. / e ** 3 - 4. / e ** 4),
    'ee12-ee3-344-44--': (-7. / 12 / e + 1. / e ** 2 - 2. / 3 / e ** 3),
    'ee12-e23-e4-444--': (-121. / 96 / e + 11. / 8 / e ** 2 - 1. / 2 / e ** 3),
    #_DO_TEST_MOMENTUM_PASSINGS
    'ee12-e33-e44-44--': ((0.5 - zeta(3)) / e + 1. / e ** 2 + 2. / e ** 3 - 4. / e ** 4),
    'ee12-e33-444-e4--': (37. / 96 / e + 5. / 8 / e ** 2 - 5. / 6 / e ** 3),
    'ee12-e33-344-4-e-': (-2. / 3 / e - 5. / 6 / e ** 2 + 8. / 3 / e ** 3 - 2. / e ** 4),
    'ee12-e23-44-e44--': (-(5. / 6 - zeta(3)) / e - 1. / 3 / e ** 2 + 2. / e ** 3 - 4. / 3 / e ** 4),
    'ee12-e34-334-4-e-': ((5. / 2 - 2 * zeta(3)) / e - 19. / 6 / e ** 2 + 2. / e ** 3 - 2. / 3 / e ** 4),
    'ee12-e23-34-44-e-': (5. / 2 / e - 19. / 6 / e ** 2 + 2. / e ** 3 - 2. / 3 / e ** 4),

    'e112-33-e33--': (5. / 16 / e + 1. / 4 / e ** 2 - 1. / e ** 3),
    'e112-e3-333--': (5. / 16 / e - 1. / 8 / e ** 2),
    'e123-e23-33--': (-13. / 48 / e + 7. / 12 / e ** 2 - 1. / 3 / e ** 3),

    'ee12-e34-335-e-555--': ((103. / 160) / e + 37. / 240 / e / e - 19. / 20 / e / e / e + 7. / 15 / e / e / e / e),
    'ee12-333-445-5-e5-e-': (-(11. / 192) / e + 33. / 80 / e / e - 11. / 12 / e / e / e + 3. / 5 / e / e / e / e),
    'ee12-e33-e34-5-555--': (151. / 192 / e + 197. / 240 / e / e - 103. / 60 / e / e / e + 11. / 15 / e / e / e / e),
    'ee12-e33-444-55-5-e-': (
         (2. / 5 * zeta(3) - 151. / 480) / e - 53. / 120 / e / e - 23. / 30 / e / e / e + 6. / 5 / e / e / e / e),
    'ee12-e34-555-e44-5--': (-(11. / 192) / e + 33. / 80 / e / e - 11. / 12 / e / e / e + 3. / 5 / e / e / e / e),
    'e123-e23-e4-e5-555--': ((3. / 5 * zeta(4) - 27. / 10 * zeta(3)) / e + 4. / 5 * zeta(3) / e / e),
    'ee12-333-444-5-5-ee-': (-(5. / 96) / e - 3. / 10 / e / e + 4. / 15 / e / e / e),
    'ee12-ee3-334-5-555--': ((857. / 960) / e - 13. / 20 / e / e + 2. / 15 / e / e / e),
    'ee12-e23-34-e5-555--': (-(2387. / 960) / e + 41. / 15 / e / e - 13. / 10 / e / e / e + 4. / 15 / e / e / e / e),
    'e112-e3-e34-e5-555--': (151. / 192 / e + 197. / 240 / e / e - 103. / 60 / e / e / e + 11. / 15 / e / e / e / e),
    'ee11-23-e34-e5-555--': ( 121. / 48 / e / e - 11. / 4 / e / e / e + 1. / e / e / e / e),
    'e112-e3-e44-555-e5--': (
         (2. / 5 * zeta(3) - 151. / 480) / e - 53. / 120 / e / e - 23. / 30 / e / e / e + 6. / 5 / e / e / e / e),
    'ee11-23-e44-555-e5--': (-37. / 48 / e / e - 5. / 4 / e / e / e + 5. / 3 / e / e / e / e),
    'ee12-ee3-444-555-5--': (-(5. / 96) / e - 3. / 10 / e / e + 4. / 15 / e / e / e),
    #TEST PERF
    'ee12-e23-34-45-55-e-': (
         (28. / 5) / e - (19. / 3) / e / e + 11. / 3 / e / e / e - 4. / 3 / e / e / e / e + 4. / 15 / e / e / e / e / e),
    #TEST PERFORMANCE
    'e112-e3-e44-455-5-e-': ((3. / 10 * zeta(4) - zeta(3) + 3. / 5) / e + (2. / 5 * zeta(
         3) + 3. / 5) / e / e + 4. / 5 / e / e / e - 4. / e / e / e / e + 16. / 5 / e / e / e / e / e),
    'e112-e3-e34-45-55-e-': (-(28. / 15) / e - (
                                                    19. / 15) / e / e + 56. / 15 / e / e / e - 44. / 15 / e / e / e / e + 16. / 15 / e / e / e / e / e),
    #TEST PERF
    'ee11-23-e44-e55-55--': ((2. * zeta(3) - 1) / e / e - 2. / e / e / e - 4. / e / e / e / e + 8. / e / e / e / e / e),
    'ee11-22-34-e55-e55--': (-8. / 3 / e / e / e - 16. / 3 / e / e / e / e + 32. / 3 / e / e / e / e / e),
    'ee11-22-34-e45-55-e-': (16. / 3 / e / e / e - 8. / e / e / e / e + 16. / 3 / e / e / e / e / e),
    'ee11-23-e44-455-5-e-': ((4. / 3) / e / e + 5. / 3 / e / e / e - 16. / 3 / e / e / e / e + 4. / e / e / e / e / e),
    'ee12-e23-e4-455-55--': (
         -(1. / 5 * zeta(3) + 841. / 480) / e + (49. / 24) / e / e - 13. / 10 / e / e / e + 2. / 5 / e / e / e / e),
    'ee12-ee3-345-45-55--': (
         -(4. / 5 * zeta(3) + 193. / 480) / e + (19. / 15) / e / e - 14. / 15 / e / e / e + 4. / 15 / e / e / e / e),
    'ee11-23-ee4-455-55--': ((7. / 6) / e / e + (-2.) / e / e / e + 4. / 3 / e / e / e / e),
    'ee12-ee3-344-55-55--': (
         -(3. / 10 * zeta(3) - 81. / 160) / e + (1. / 5) / e / e - 6. / 5 / e / e / e + 4. / 5 / e / e / e / e),
    'ee11-23-e45-e45-55--': (
         -(4. * zeta(3) - 2) / e / e + 10. / 3 / e / e / e - 16. / 3 / e / e / e / e + 8. / 3 / e / e / e / e / e),
    'e112-e3-e45-e45-55--': (-(3. / 10 * zeta(4) + zeta(3) - 29. / 15) / e - (2. / 5 * zeta(
         3) - 1. / 3) / e / e + 32. / 15 / e / e / e - 4. / e / e / e / e + 32. / 15 / e / e / e / e / e),
    'e112-e2-34-e45-55-e-': (
         -4. / 3 / e / e + 14. / 3 / e / e / e - 16. / 3 / e / e / e / e + 8. / 3 / e / e / e / e / e),
    'ee12-e33-445-e5-55--': (
         (1. / 5 * zeta(3) + 293. / 480) / e + 1. / 40 / e / e - 11. / 10 / e / e / e + 14. / 15 / e / e / e / e),
    'ee11-22-33-44-55-ee-': (32. / e / e / e / e / e),
    #PERFORMANCE
    'e112-e3-e44-e55-55--': ((6. / 5 * zeta(4) - 4. / 5 * zeta(3) - 2. / 5) / e + (8. / 5 * zeta(
         3) - 4. / 5) / e / e - 8. / 5 / e / e / e - 16. / 5 / e / e / e / e + 32. / 5 / e / e / e / e / e),
    'ee11-22-33-45-e55-e-': (-8. / e / e / e / e + 16. / e / e / e / e / e),
    'ee11-22-34-445-5-ee-': (8. / 3 / e / e / e - 32. / 3 / e / e / e / e + 32. / 3 / e / e / e / e / e),
    'e112-e2-33-45-e55-e-': (2. / e / e / e - 8. / e / e / e / e + 8. / e / e / e / e / e),
    'ee12-223-3-45-e55-e-': (-(2. / 3) / e / e + 4. / e / e / e - 8. / e / e / e / e + 16. / 3 / e / e / e / e / e),

    #WTF
    'e112-33-e44-44--': (
         (2. / 5 * zeta(3) - 13. / 40) / e - (1. / 2) / e / e - 2. / 5 / e / e / e + 8. / 5 / e / e / e / e),
    'e112-33-444-e4--': ((-149. / 480) / e - (17. / 60) / e / e + 7. / 30 / e / e / e),
    'e112-e3-344-44--': ((209. / 480) / e - (3. / 10) / e / e + 1. / 10 / e / e / e),
}

if __name__ == "__main__":
    main()
