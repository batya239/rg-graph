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
masters["e12|34|35|6|67|67||e|"] = "Bm1/e+B0+B1*e+B2*e**2+O(e**3)"
masters["e12|234|34|5|5|e|"] = "B0+B1*e+B2*e**2+O(e**3)"
masters["e123|234|4|4|e|"] = "Bm1/e+B0+B1*e+B2*e**2+O(e**3)"
masters["e11|23|45|45|6|6|e|"] = "Bm1/e+B0+B1*e+B2*e**2+O(e**3)"
masters["e12|34|345|6|6|e6||"] = "Bm1/e+B0+B1*e+B2*e**2+O(e**3)"
masters["e12|334|34|5|5|e|"] = "Bm1/e+B0+B1*e+B2*e**2+O(e**3)"
masters["e112|34|34|5|5|e|"] = "Bm1/e+B0+B1*e+B2*e**2+O(e**3)"
masters["e123|e45|45|45|||"] = "Bm1/e+B0+B1*e+B2*e**2+O(e**3)"

#O(e**3)
masters["e12|234|34|e4||"] = "Cm2/e/e+Cm1/e+C0+C1*e+C2*e**2+C3*e**3+O(e**4)"

#O(e**4)
masters["e12|334|334||e|"] = "Dm4/e/e/e/e+Dm3/e/e/e+Dm2/e/e+Dm1/e+D0+D1*e+D2*e**2+D3*e**3+D4*e**4+O(e**5)"
masters["e11|23|334|4|e|"] = "Dm4/e/e/e/e+Dm3/e/e/e+Dm2/e/e+Dm1/e+D0+D1*e+D2*e**2+D3*e**3+D4*e**4+O(e**5)"
masters["e12|233|34|4|e|"] = "Dm4/e/e/e/e+Dm3/e/e/e+Dm2/e/e+Dm1/e+D0+D1*e+D2*e**2+D3*e**3+D4*e**4+O(e**5)"

#O(e**5)
masters["e112|223|3|e|"] = "Em3/e/e/e+Em2/e/e+Em1/e+E0+E1*e+E2*e**2+E3*e**3+E4*e**4+E5*e**5+O(e**6)"
masters["e112|23|33|e|"] = "Em3/e/e/e+Em2/e/e+Em1/e+E0+E1*e+E2*e**2+E3*e**3+E4*e**4+E5*e**5+O(e**6)"
masters["e123|e23|33||"] = "Em3/e/e/e+Em2/e/e+Em1/e+E0+E1*e+E2*e**2+E3*e**3+E4*e**4+E5*e**5+O(e**6)"
masters["e12|2223|3|e|"] = "Em3/e/e/e+Em2/e/e+Em1/e+E0+E1*e+E2*e**2+E3*e**3+E4*e**4+E5*e**5+O(e**6)"


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

symbolic_functions.Am1 = symbolic_functions.var("Am1")
symbolic_functions.A0 = symbolic_functions.var("A0")
symbolic_functions.A1 = symbolic_functions.var("A1")

symbolic_functions.Bm1 = symbolic_functions.var("Bm1")
symbolic_functions.B0 = symbolic_functions.var("B0")
symbolic_functions.B1 = symbolic_functions.var("B1")
symbolic_functions.B2 = symbolic_functions.var("B2")

symbolic_functions.Cm2 = symbolic_functions.var("Cm2")
symbolic_functions.Cm1 = symbolic_functions.var("Cm1")
symbolic_functions.C0 = symbolic_functions.var("C0")
symbolic_functions.C1 = symbolic_functions.var("C1")
symbolic_functions.C2 = symbolic_functions.var("C2")
symbolic_functions.C3 = symbolic_functions.var("C3")

symbolic_functions.Dm4 = symbolic_functions.var("Dm4")
symbolic_functions.Dm3 = symbolic_functions.var("Dm3")
symbolic_functions.Dm2 = symbolic_functions.var("Dm2")
symbolic_functions.Dm1 = symbolic_functions.var("Dm1")
symbolic_functions.D0 = symbolic_functions.var("D0")
symbolic_functions.D1 = symbolic_functions.var("D1")
symbolic_functions.D2 = symbolic_functions.var("D2")
symbolic_functions.D3 = symbolic_functions.var("D3")
symbolic_functions.D4 = symbolic_functions.var("D4")

symbolic_functions.Em3 = symbolic_functions.var("Em3")
symbolic_functions.Em2 = symbolic_functions.var("Em2")
symbolic_functions.Em1 = symbolic_functions.var("Em1")
symbolic_functions.E0 = symbolic_functions.var("E0")
symbolic_functions.E1 = symbolic_functions.var("E1")
symbolic_functions.E2 = symbolic_functions.var("E2")
symbolic_functions.E3 = symbolic_functions.var("E3")
symbolic_functions.E4 = symbolic_functions.var("E4")
symbolic_functions.E5 = symbolic_functions.var("E5")


FOUR_LOOP_REDUCTOR = reductor.Reductor("p4a",
                                       "loop4d",
                                       map(lambda g: graphine.Graph.from_str(g), topology),
                                       4,
                                       dict(map(lambda (g, v): (graphine.Graph.from_str(g), symbolic_functions.evaluate(v, strong_to_internal_code=True)), masters.iteritems())), "q", "l")