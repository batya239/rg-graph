#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


from rggraphenv import symbolic_functions
import reductor
import graphine
import graph_state
import reduction_util


G = symbolic_functions.G
l = symbolic_functions.l


THREE_LOOP_REDUCTOR = reductor.Reductor("loop3",
                               "loop3",
                               3,
                               {graphine.Graph.from_str("e12|34|34|5|5|e|"):
                                    symbolic_functions.evaluate(
                                        "_g11()**(-3)*(exp(-3 * Euler * e))/(1-2*e)*(20 * zeta(5)"
                                        "+e *(68 * zeta(3)**2+(10 * Pi**6)/189)"
                                        "+e**2 *((34 * Pi **4 * zeta(3))/15-5 * Pi **2 * zeta(5)+450 *zeta(7))"
                                        "+e**3 *(-9072/5 * Z53-2588*zeta(3)*zeta(5)-17* Pi **2 *zeta(3)**2+(6487*Pi**8)/10500))+Order(e**4)"),
                                graphine.Graph.from_str("e11|22|33|e|"): G(1, 1) ** 3,
                                graphine.Graph.from_str("e112|22|e|"): G(1, 1) * G(1, 1) * G(2 - 2 * l, 1),
                                graphine.Graph.from_str("e11|222|e|"): G(1, 1) * G(1, 1) * G(1 - l, 1),
                                graphine.Graph.from_str("e1111|e|"): G(1, 1) * G(1 - l, 1) * G(1 - 2 * l, 1),
                                graphine.Graph.from_str("e12|223|3|e|"):
                                    symbolic_functions.evaluate("_g11()**(-3)*exp(-3 * Euler * e )*("
                                                                "1/(3 *e **3)+7/(3* e **2)"
                                                                "+e **(-1)*(31/3-(Pi **2)/12)"
                                                                "+(103/3-(7 * Pi **2)/(12)+(7 *zeta(3))/(3))"
                                                                "+e *(235/3-(31 * Pi **2)/12+(49 *zeta(3))/3+(5 * Pi **4)/96)"
                                                                "+e **2 *(19/(3)-(103 *Pi **2)/12+(289 *zeta(3))/3 +(35 *Pi **4)/96-(7 * Pi **2 * zeta(3))/12+(599 *zeta(5))/5)"
                                                                "+e **3 *(-3953/3-(235 *Pi **2)/12+(1729 * zeta(3))/3 +(967 *Pi **4)/480-(49 *Pi **2 * zeta(3))/12+(4193* zeta(5))/5+(108481* Pi **6)/362880-(599 *zeta(3)**2)/6)"
                                                                "+e **4 *(-31889/3-(19 * Pi **2)/12+10213 * zeta(3)/3+5263 * Pi **4/480-289 * Pi **2 * zeta(3)/12+20609 * zeta(5)/5+108481 * Pi **6/51840 -4193* zeta(3)**2/6-1553* Pi **4 *zeta(3)/480-599 *Pi **2* zeta(5)/20+13593*zeta(7)/7)"
                                                                ")+Order(e**5)")}, "p", "k")

TWO_LOOP_REDUCTOR = reductor.Reductor("loop2",
                             "loop2",
                             2,
                             {graphine.Graph.from_str("e111|e|"): G(1, 1) * G(1 - l, 1),
                              graphine.Graph.from_str("e11|22|e|"): G(1, 1) ** 2}, "p", "k")

G_D6 = symbolic_functions.create_G(symbolic_functions.cln(6) - symbolic_functions.cln(2) * symbolic_functions.e)

TWO_LOOP_REDUCTOR_D6 = reductor.Reductor("loop2",
                             "loop2_d6",
                             2,
                             {graphine.Graph.from_str("e111|e|"): G_D6(1, 1) * G_D6(symbolic_functions.e - 1, 1),
                              graphine.Graph.from_str("e11|22|e|"): G_D6(1, 1) ** 2}, "p", "k")