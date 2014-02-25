#!/usr/bin/python
# -*- coding: utf8
import graphine

__author__ = 'mkompan'

from graph_state_builder_static import gs_builder
import swiginac
from rggraphenv.symbolic_functions import safe_integer_numerators_strong, e, zeta, var, Pi, series, tgamma

from ch import H
psi = swiginac.psi


def symmetry_coefficient(gs):
    external_edge_fields = dict()
    edges_count = dict()
    bubbles = dict()
    for edge in gs.edges:
        n1, n2 = edge.nodes
        if n1 == n2:
            if edge not in bubbles:
                bubbles[edge] = 1
            else:
                bubbles[edge] += 1
        if edge not in edges_count:
            edges_count[edge] = 1
        else:
            edges_count[edge] += 1

        if -1 in edge.nodes:
            if edge.fields is None:
                field = None
            else:
                field_ = list(edge.fields.pair)
                field_.remove('0')
                field = field_[0]
            if field not in external_edge_fields:
                external_edge_fields[field] = 1
            else:
                external_edge_fields[field] += 1

    c = swiginac.numeric('1')

    for n in external_edge_fields.values():
        c = c * swiginac.factorial(swiginac.numeric(str(n)))

    for n in edges_count.values():
        c = c / swiginac.factorial(swiginac.numeric(str(n)))

    trace = reduce(lambda x, y: x + y, [0] + bubbles.values())
    c /= 2 ** trace

    return c / len(gs.sortings)


def renormalization_constants(diagrams_dict, structures_dict):
    Z1 = swiginac.numeric('1')
    Z3 = swiginac.numeric('1')
    g = var('g')
    for i in range(1, 94):
        exec('r%s = var("r%s")' % (i, i))
    for gs_string in sorted(diagrams_dict.keys()):
        gs = gs_builder.graph_state_from_str(gs_string)
        graph = graphine.Graph(gs)
        if graph.externalEdgesCount() == 2:

            Z1 += symmetry_coefficient(gs) \
                  * eval(safe_integer_numerators_strong(diagrams_dict[gs_string])) \
                  * eval(safe_integer_numerators_strong(structures_dict[gs_string])) \
                  * (-g) ** graph.getLoopsCount()
        elif graph.externalEdgesCount() == 4:
            Z3 -= symmetry_coefficient(gs) \
                  * eval(safe_integer_numerators_strong(diagrams_dict[gs_string])) \
                  * eval(safe_integer_numerators_strong(structures_dict[gs_string])) \
                  * (-g) ** graph.getLoopsCount()
        else:
            raise NotImplementedError("ext legs count: %s" % graph.externalEdgesCount())
    return Z1, Z3


def substitute_r(expr, ri):
    n = var('n')
    res = expr
    for i in range(1, 94):
        res = res.subs(var('r%s' % i) == eval(safe_integer_numerators_strong(ri['r%s' % i])))
    return res


def calculate_gstar(beta_n, loops_count):
    a = var('a')
    g = var('g')
    gstar = e*a
    for i in range(1, loops_count+1):
        beta1 = series((beta_n/g), g, 0,  i+1, remove_order=True).expand()
        eq = series(beta1.subs(g == gstar), e, 0, i+1, remove_order=True)
        gstar = gstar.subs(a == -eq.subs(a == 0).expand().normal()/eq.coeff(a))+e**(i+1)*a

    gstar_ = series(gstar.subs(a == 0), e, 0, loops_count+1)
    return gstar_


def BB(z, d=4-2*e):
    return psi(z)+psi(d/2-z)


def CC(z, d=4-2*e):
    return swiginac.psi(1, z) - swiginac.psi(1, d/2 - z)


def DD(z, d=4-2*e):
    return swiginac.psi(2, z) + swiginac.psi(2, d/2 - z)


def I(e):
    I1 = var('I1')
    I2 = var('I2')
    return I1*e+I2*e**2


if __name__ == "__main__":
    n = var('n')
    loops2 = 5
    loops4 = 5
    from MS5loop import ms
    from On_structures_6loop import on
    from ri import ri

    g = var('g')
    Z1, Z3 = renormalization_constants(ms, on)
    Z1 = series(Z1.expand().collect(g), g, 0, loops2 + 1)
    Z3 = series(Z3.expand().collect(g), g, 0, loops4 + 1)
#    print Z1
#    print Z3
    Zg = series(Z3 / Z1 ** 2, g, 0, loops4 + 1)
#    print Zg
    log_diff_Zg = g * swiginac.log(Zg).diff(g)
    gamma_g = series(-2 * e * log_diff_Zg / (1 + log_diff_Zg), g, 0, loops4 + 1).expand()
    beta = series(-2 * e * g / (1 + log_diff_Zg), g, 0, loops4 + 2).expand()
    gamma_f = series(-(2 * e + gamma_g) * g * swiginac.log(Z1).diff(g) / 2, g, 0, loops2 + 1).expand()

    print
    print "\ngamma_g = ", substitute_r(gamma_g, ri).expand()
    print "\nbeta = ", substitute_r(beta, ri).expand()
    print "\ngamma_f = ", substitute_r(gamma_f, ri).expand()

    print "\nbeta (n=1)= ", substitute_r(beta, ri).subs(n == 1).evalf().expand()
    print "\n2*gamma_f (n=1)= ", substitute_r(2*gamma_f, ri).subs(n == 1).evalf().expand()

    gstar = calculate_gstar(substitute_r(beta, ri), loops4)
    print
    print "gstar(n) = ", gstar
    print
    print gstar.subs(n == 1)


    eta = series(2*substitute_r(gamma_f, ri).subs(g == gstar), e, 0, loops2+1, remove_order=True)

    print "eta"
    print eta.subs(n == 1).subs(e == e/2).evalf()


    print
    x = var('x')
    eta_n = series(eta.subs(n == 1/x).expand(), x, 0, 4, remove_order=True).expand().collect(x)
    print eta_n

    d = 4-2*e
    eta1 = -4 * H(2-d/2, d/2-2, d/2-1)/tgamma(d/2+1)
#    print eta1
    eta1_ = series(eta1, e, 0, 7,remove_order=True).expand()

    print
    print eta1_
    print eta1_-eta_n.coeff(x,1)



    R0 = psi(d-2)+psi(2-d/2)-psi(2)-psi(d/2-2)

    eta2 = eta1**2*((d**2-3*d+4)/(4-d)*R0+1/d+1/(d-2)+9/(4-d)+4/(4-d)**2-2-d)
    eta2_ = series(eta2, e, 0, 7,remove_order=True).expand()

    print
    print eta2_
    print eta2_-eta_n.coeff(x,2)


    R0 = psi(d-2)+psi(2-d/2)-psi(2)-psi(d/2-2)

    mu = d/2
    a = mu-1
    b = 2-mu
    B = BB(2-mu)-BB(2)
    S0 = BB(2-mu)-BB(1)
    S1 = CC(2-mu)-CC(1)
    S2 = DD(2-mu)-DD(1)
    S3 = CC(mu-1)
    S4 = CC(2-mu)
    eta3 = eta1**3*(3*mu**2*a*(4*mu - 5)*I(e)*S3/2/b**2 + 2*mu**2*a*(2*mu-3)**2*(3*S0*S1-S2-S0**3)/3/b/b/b
                    + swiginac.numeric(1)/2 *(70 + 26*mu+8*mu**2-177/b+67/b/b+58/b/b/b-16/b/b/b/b+9/a+1/a/a+1/mu/mu
                                              + B*(66+14*mu+4*mu*mu-187/b+102/b/b+16/b/b/b+2/a+3/mu)
                                              + B*B*(20-50/b+32/b/b)
                                              + S3*(-45-10*mu+7*mu+127/b-64/b/b-48/b/b/b+32/b/b/b/b)
                                              + S4*(14+8*mu+8*mu**2-30/b)
                                              + B*S3*(-45-13*mu-2*mu**2+136/b - 108/b/b+32/b/b/b) ) )
    eta3_ = series(eta3, e, 0, 7,remove_order=True).expand()

    print
    print eta3_
    print (eta3_-eta_n.coeff(x,3)).collect(e)
    print (eta3_-eta_n.coeff(x,3)).collect(e).subs(e==e/2).expand()