#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import reductor
import graphine
from rggraphenv import symbolic_functions


masters = dict()

#O(e)
masters["e12|34|56|56|57||7|e|"] = "Am1/e+A0+A1*e+O(e**2)"
masters["e12|34|35|6|56|7|7|e|"] = "Am1/e+A0+A1*e+O(e**2)"
masters["e12|23|34|45|5|e|"] = "A0+A1*e+O(e**2)"

#O(e**2)
masters["e12|34|35|6|67|67||e|"] = "Am1/e+A0+A1*e+A2*e**2+O(e**3)"
masters["e12|234|34|5|5|e|"] = "A0+A1*e+A2*e**2+O(e**3)"
masters["e123|234|4|4|e|"] = "Am1/e+A0+A1*e+A2*e**2+O(e**3)"
masters["e11|23|45|45|6|6|e|"] = "Am1/e+A0+A1*e+A2*e**2+O(e**3)"
masters["e12|34|345|6|6|e6||"] = "Am1/e+A0+A1*e+A2*e**2+O(e**3)"
masters["e12|334|34|5|5|e|"] = "Am1/e+A0+A1*e+A2*e**2+O(e**3)"
masters["e112|34|34|5|5|e|"] = "Am1/e+A0+A1*e+A2*e**2+O(e**3)"
masters["e123|e45|45|45|||"] = "Am1/e+A0+A1*e+A2*e**2+O(e**3)"

#O(e**3)
masters["e12|234|34|e4||"] = "Am2/e/e+Am1/e+A0+A1*e+A2*e**2+A3*e**3+O(e**4)"

#O(e**4)
masters["e12|334|334||e|"] = "Am4/e/e/e/e+Am3/e/e/e+Am2/e/e+Am1/e+A0+A1*e+A2*e**2+A3*e**3+A4*e**4+O(e**5)"
masters["e11|23|334|4|e|"] = "Am4/e/e/e/e+Am3/e/e/e+Am2/e/e+Am1/e+A0+A1*e+A2*e**2+A3*e**3+A4*e**4+O(e**5)"
masters["e12|233|34|4|e|"] = "Am4/e/e/e/e+Am3/e/e/e+Am2/e/e+Am1/e+A0+A1*e+A2*e**2+A3*e**3+A4*e**4+O(e**5)"

#O(e**5)
masters["e112|223|3|e|"] = "Am3/e/e/e+Am2/e/e+Am1/e+A0+A1*e+A2*e**2+A3*e**3+A4*e**4+A5*e**5+O(e**6)"
masters["e112|23|33|e|"] = "Am3/e/e/e+Am2/e/e+Am1/e+A0+A1*e+A2*e**2+A3*e**3+A4*e**4+A5*e**5+O(e**6)"
masters["e123|e23|33||"] = "Am3/e/e/e+Am2/e/e+Am1/e+A0+A1*e+A2*e**2+A3*e**3+A4*e**4+A5*e**5+O(e**6)"
masters["e12|2223|3|e|"] = "Am3/e/e/e+Am2/e/e+Am1/e+A0+A1*e+A2*e**2+A3*e**3+A4*e**4+A5*e**5+O(e**6)"


#analytical
masters["e11|22|333|e|"] = "G(1,1)**3*G(1-l,1)"
masters["e11|223|33|e|"] = "G(1,1)**3*G(2-2*l,1)"
masters["e112|33|e33||"] = "G(1,1)**3*G(3-3*l,1)"
masters["e11|2222|e|"] = "G(1,1)**3*G(1-l,1-l)"
masters["e111|222|e|"] = "(G(1,1)*G(1-l,1))**2"
masters["e1112|22|e|"] = "G(1,1)**2*G(1-l,1)*G(2-3*l,1)"
masters["e1122|e22||"] = "G(1,1)**2*G(1,2-2*l)*G(1,2-3*l)"
masters["e11111|e|"] = "G(1,1)*G(1-l,1)*G(1-2*l,1)*G(1-3*l,1)"
masters["e11|22|33|44|e|"] = "G(1,1)**4"

topology = list()
topology.append("e12|34|35|6|67|67||e|")
topology.append("e12|34|56|56|57||7|e|")
topology.append("e12|34|35|6|56|7|7|e|")

symbolic_functions.Am4 = symbolic_functions.var("Am4")
symbolic_functions.Am3 = symbolic_functions.var("Am3")
symbolic_functions.Am2 = symbolic_functions.var("Am2")
symbolic_functions.Am1 = symbolic_functions.var("Am1")
symbolic_functions.A0 = symbolic_functions.var("A0")
symbolic_functions.A1 = symbolic_functions.var("A1")
symbolic_functions.A2 = symbolic_functions.var("A2")
symbolic_functions.A3 = symbolic_functions.var("A3")
symbolic_functions.A4 = symbolic_functions.var("A4")
symbolic_functions.A5 = symbolic_functions.var("A5")


FOUR_LOOP_REDUCTOR = reductor.Reductor("p4a",
                                       "loop4d",
                                       map(lambda g: graphine.Graph.fromStr(g), topology),
                                       4,
                                       dict(map(lambda (g, v): (graphine.Graph.fromStr(g), symbolic_functions.evaluate(v, strong_to_internal_code=True)), masters.iteritems())), "q", "l")

FOUR_LOOP_REDUCTOR.initIfNeed()