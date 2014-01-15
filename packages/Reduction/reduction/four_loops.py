#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import reductor
import graphine
from rggraphenv import symbolic_functions


masters = dict()

#
# masters integrals: Baikov, Chetyrkin arxiv 1004.1153
#

#1row
#M61
masters["e12|34|35|6|67|67||e|"] = "(-10*zeta(5)/e+50*zeta(5)-10*zeta(3)**2-25*zeta(6)+e*(90*zeta(5)+50*zeta(3)**2+125*zeta(6)-30*zeta(3)*zeta(4)+19*zeta(7)/2))+O(e**2)"
#M62
masters["e12|34|56|56|57||7|e|"] = "(-10*zeta(5)/e+130*zeta(5)-10*zeta(3)**2-25*zeta(6)-70*zeta(7))+O(e)"
#M63
masters["e12|34|35|6|56|7|7|e|"] = "(-5*zeta(5)/e+45*zeta(5)-41*zeta(3)**2-25*zeta(6)/2+161*zeta(7)/2)+O(e)"
#M51
masters["e12|34|345|6|6|e6||"] = "(-5*zeta(5)/e+45*zeta(5)-17*zeta(3)**2-25*zeta(6)/2+e*(-195*zeta(5)+153*zeta(3)**2+225*zeta(6)/2-51*zeta(3)*zeta(4)-85*zeta(7)/2))+O(e**2)"

#row2
#M41
masters["e12|334|34|5|5|e|"] = "(20*zeta(5)/e-80*zeta(5)-22*zeta(3)**2+50*zeta(6)+e*(80*zeta(5)+88*zeta(3)**2-200*zeta(6)-66*zeta(3)*zeta(4)+4685*zeta(7)/8))+O(e**2)"
#M42
masters["e112|34|34|5|5|e|"] = "(20*zeta(5)/e-80*zeta(5)+8*zeta(3)**2+50*zeta(6)+e*(80*zeta(5)-32*zeta(3)**2-200*zeta(6)+24*zeta(3)*zeta(4)+520*zeta(7)))+O(e**2)"
#M44
masters["e12|23|34|45|5|e|"] = "(441*zeta(7)/8)+O(e)"
#M45
masters["e12|234|34|5|5|e|"] = "(36*zeta(3)**2+e*(108*zeta(3)*zeta(4)-378*zeta(7)))+O(e**2)"

#row3
#M34
masters["e12|233|34|4|e|"] = "(1/e**4/12+1/e**3/4+7/e**2/12-17/e/12+25*zeta(3)/6/e-377/12+25*zeta(3)/2+25*zeta(4)/4" \
                             "+e*(-3401/12+463*zeta(3)/6+75*zeta(4)/4+465*zeta(5)/2)" \
                             "+e**2*(-24497/12+3031*zeta(3)/6+463*zeta(4)/4+1395*zeta(5)/2-1247*zeta(3)**2/6+3425*zeta(6)/6)" \
                             "+e**3*(-158273/12+19663*zeta(3)/6+3031*zeta(4)/4+6807*zeta(5)/2" \
                             "-1247*zeta(3)**2/2+3425*zeta(6)/2-1247*zeta(3)*zeta(4)/2+12503*zeta(7)/2))+O(e**4)"
#M35
masters["e12|234|34|e4||"] = "(zeta(3)/2/e/e+(3*zeta(3)/2+3*zeta(4)/4)/e+19*zeta(3)/2+9*zeta(4)/4-23*zeta(5)/2" \
                             "+e*(103*zeta(3)/2+57*zeta(4)/4-69*zeta(5)/2+29*zeta(3)**2/2-30*zeta(6))" \
                             "+e**2*(547*zeta(3)/2+309*zeta(4)/4-437*zeta(5)/2+87*zeta(3)**2/2-90*zeta(6)+87*zeta(3)*zeta(4)/2-1105*zeta(7)/4))+O(e**3)"
#M36
masters["e123|234|4|4|e|"] = "(5*zeta(5)/e-5*zeta(5)-7*zeta(3)**2+25*zeta(6)/2+e*(35*zeta(5)+7*zeta(3)**2-25*zeta(6)/2-21*zeta(3)*zeta(4)+127*zeta(7)/2))+O(e**2)"
#M52
masters["e11|23|45|45|6|6|e|"] = "(20*zeta(5)/e-80*zeta(5)+68*zeta(3)**2+50*zeta(6)+e*(80*zeta(5)-272*zeta(3)**2-200*zeta(6)+204*zeta(3)*zeta(4)+450*zeta(7)))+O(e**2)"

#row4
#M43
masters["e123|e45|45|45|||"] = "(-5*zeta(5)/e+45*zeta(5)-17*zeta(3)**2-25*zeta(6)/2+e*(-195*zeta(5)+153*zeta(3)**2+225*zeta(6)/2-51*zeta(3)*zeta(4)-225*zeta(7)/2))+O(e**2)"
#M32
masters["e11|23|334|4|e|"] = "(1/3/e**4+1/3/e**3+1/3/e**2+(-7/3+14*zeta(3)/3)/e-67/3+14*zeta(3)/3+7*zeta(4)" \
                             "+e*(-403/3+86*zeta(3)/3+7*zeta(4)+126*zeta(5))" \
                             "+e**2*(-2071/3+478*zeta(3)/3+43*zeta(4)+126*zeta(5)-226*zeta(3)**2/3+910*zeta(6)/3)" \
                             "+e**3*(-9823/3+2446*zeta(3)/3+239*zeta(4)+534*zeta(5)-226*zeta(3)**2/3+910*zeta(6)/3-226*zeta(3)*zeta(4)+1960*zeta(7)))+O(e**4)"
#M33
masters["e12|334|334||e|"] = "(1/6/e**4+1/3/e**3+1/3/e**2+(-17/3+31*zeta(3)/3)/e-197/3+62*zeta(3)/3+31*zeta(4)/2" \
                             "+e*(-1529/3+386*zeta(3)/3+31*zeta(4)+449*zeta(5))" \
                             "+e**2*(-10205/3+2510*zeta(3)/3+193*zeta(4)+898*zeta(5)-983*zeta(3)**2/3+3290*zeta(6)/3)" \
                             "+e**3*(-62801/3+15974*zeta(3)/3+1255*zeta(4)+4354*zeta(5)" \
                             "-1966*zeta(3)**2/3+6580*zeta(5)/3-983*zeta(3)*zeta(4)+11338*zeta(7)))+O(e**4)"
#M21
masters["e112|223|3|e|"] = "(-5/48/e**3-31/96/e**2-95/192/e+1133/384-19*zeta(3)/12" \
                           "+e*(30097/768-233*zeta(3)/24-19*zeta(4)/8)+e**2*(463349/1536-3385*zeta(3)/48-233*zeta(4)/16-341*zeta(5)/4)" \
                           "+e**3*(6004105/3072-46469*zeta(3)/96-3385*zeta(4)/32-3187*zeta(5)/8+493*zeta(3)**2/6-1255*zeta(6)/6)" \
                           "+e**4*(71426093/6144-590281*zeta(3)/192-46469*zeta(4)/64-33875*zeta(5)/16" \
                           "+4673*zeta(3)**2/12-2915*zeta(6)/3+493*zeta(3)*zeta(4)/2-16619*zeta(7)/8))+O(e**5)"

#row5
#M22
masters["e112|23|33|e|"] = "(-1/4/e**3-3/2/e**2-33/4/e-175/4+10*zeta(3)+e*(-1825/8+113*zeta(3)/2+15*zeta(4))" \
                           "+e**2*(-18867/16+1241*zeta(3)/4+339*zeta(4)/4+185*zeta(5))" \
                           "+e**3*(-194015/32+13425*zeta(3)/8+3723*zeta(4)/8+1028*zeta(5)-204*zeta(3)**2+875*zeta(6)/2)" \
                           "+e**4*(-1987331/64+143605*zeta(3)/16+40275*zeta(4)/16+5588*zeta(5)" \
                           "-1131*zeta(3)**2+9715*zeta(6)/4-612*zeta(3)*zeta(4)+13157*zeta(7)/4))+O(e**5)"
#M26
masters["e123|e23|33||"] = "(-1/8/e**3-13/16/e**2-141/32/e-1393/64+2*zeta(3)+e*(-12997/128+13*zeta(3)+3*zeta(4))" \
                           "+e**2*(-116697/256+123*zeta(3)/2+39*zeta(4)/2+24*zeta(5))" \
                           "+e**3*(-1019645/512+907*zeta(3)/4+369*zeta(4)/4+156*zeta(5)+49*zeta(3)**2/2+55*zeta(6))" \
                           "+e**4*(-8732657/1024+4375*zeta(3)/8+2721*zeta(4)/8+693*zeta(5)+637*zeta(3)**2/4+715*zeta(6)/2+147*zeta(3)*zeta(4)/2+2475*zeta(7)/4))+O(e**5)"
#M27
masters["e12|2223|3|e|"] = "(1/48/e**3+7/96/e**2+11/192/e-605/384+7*zeta(3)/6" \
                           "+e*(-13525/786+49*zeta(3)/12+7*zeta(4)/4)+e**2*(-208037/1536+161*zeta(3)/6+49*zeta(4)/8+221*zeta(5)/4)" \
                           "+e**3*(-2760397/3072+9535*zeta(3)/48+161*zeta(4)/4+1547*zeta(5)/8-145*zeta(3)**2/3+3245*zeta(6)/24)" \
                           "+e**4*(-33789053/6144+8273*zeta(3)/6+9535*zeta(4)/32+14527*zeta(5)/16" \
                           "-1015*zeta(3)**2/6+22715*zeta(6)/48-145*zeta(3)*zeta(4)+11289*zeta(7)/8))+O(e**5)"
#M23
masters["e11|22|333|e|"] = "G(1,1)**3*G(1-l,1)"

#row6
#M24
masters["e11|223|33|e|"] = "G(1,1)**3*G(2-2*l,1)"
#M25
masters["e112|33|e33||"] = "G(1,1)**3*G(3-3*l,1)"
#M11
masters["e11|2222|e|"] = "G(1,1)**2*G(1-l,1)*G(1-2*l,1)"
#M12
masters["e111|222|e|"] = "(G(1,1)*G(1-l,1))**2"

#row7
#M13
masters["e1112|22|e|"] = "G(1,1)**2*G(1-l,1)*G(2-3*l,1)"
#M14
masters["e1122|e22||"] = "G(1,1)**2*G(1,2-2*l)*G(1,2-3*l)"
#M01
masters["e11111|e|"] = "G(1,1)*G(1-l,1)*G(1-2*l,1)*G(1-3*l,1)"
#M31
masters["e11|22|33|44|e|"] = "G(1,1)**4"

topology = list()
topology.append("e12|34|35|6|67|67||e|")
topology.append("e12|34|56|56|57||7|e|")
topology.append("e12|34|35|6|56|7|7|e|")


FOUR_LOOP_REDUCTOR = reductor.Reductor("p4",
                                       "loop4",
                                       map(lambda g: graphine.Graph.fromStr(g), topology),
                                       4,
                                       dict(map(lambda (g, v): (graphine.Graph.fromStr(g), symbolic_functions.evaluate(v)), masters.iteritems())))