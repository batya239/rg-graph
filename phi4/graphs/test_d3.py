#!/usr/bin/python


import polynomial
def sector_poly(poly, sec):
    """
    This functions performs sector decomposition of polynomial poly
    according to sector nomenclature sec, i.e. returns polynomial after
    variable transformations corresponding to sector sec.
    """
    for dec in sec:
        poly = poly.stretch(dec[0], dec[1])
    return poly

def sector_diagram(poly, d_arg, sec, is_primary):
    """
    This functions performs sector decomposition of a whole diagram with
    polynomial poly being an integration element without the delta-function
    and d_arg being the delta-function argument according to sector nomenclature sec,
    i.e. returns polynomials after variable transformations corresponding to sector sec.
    If is_primary == True, first decomposition is considered primary.
    """
    result = [poly, d_arg]
    result = map(lambda x: sector_poly(x, sec), result)
    for dec in sec:
        m = [dec[0]] * len(dec[1])
        J = polynomial.poly([(1, m)], degree = (1, 0))
        result[0] = result[0] * J.toPolyProd()

    if is_primary:
        J = polynomial.poly([(1, [sec[0][0]])], degree=(1, 0))
        result[0] = result[0] * J.toPolyProd()
        result[1] = result[1].set1toVar(sec[0][0])
        result[0] = result[0].simplify()

        for p in result[0].polynomials:
            for m in p.monomials:
                if sec[0][0] in m.vars.keys():
                    result[1].degree.a = -p.degree.a
                    result[1].degree.b = -p.degree.b
                    result[0] = result[0].set1toVar(sec[0][0])
                    result[1] = result[1].toPolyProd()
                    result[0] = result[0] * result[1]
                    result[0] = result[0].simplify()
                    result[1] = None
    else:
        result[0] = result[0].simplify()
        result[1] = result[1].toPolyProd()


    return result



D=map(lambda x:(1,x),[(1,2,3),(1,2,4),(1,3,4),(2,3,4,'a0'),])

P1=polynomial.poly(D,degree=(-1.5,0))
P2=polynomial.poly([(1,[1,1])])

expr=P1*P2

d_arg = polynomial.poly([(1, [1]), \
                 (1, [2]), \
                 (1, [3]), \
                 (1, [4])], degree=(1, 0))
print expr
s123=[(1, [2, 3, 4]), (2, [3, 4]), (3,[4,])]
S123 = map(lambda x: x.simplify(), sector_diagram(expr, d_arg, s123, True)[0].diff('a0'))
print
print S123

s213=[(2, [1, 3, 4]), (1, [3, 4]), (3,[4,])]
#print sector_diagram(expr, d_arg, s213, True)
print
S213 = map(lambda x: x.simplify(), sector_diagram(expr, d_arg, s213, True)[0].diff('a0'))
print S213

sector=[(2, [1, 3, 4]), (3, [1, 4]), (1,[4,])]
#print sector_diagram(expr, d_arg, s213, True)
print
res = map(lambda x: x.simplify(), sector_diagram(expr, d_arg, sector, True)[0].diff('a0'))
print res

sector=[(2, [1, 3, 4]), (3, [1, 4]), (4,[1,])]
#print sector_diagram(expr, d_arg, s213, True)
print
res = map(lambda x: x.simplify(), sector_diagram(expr, d_arg, sector, True)[0].diff('a0'))
print res