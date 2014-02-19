#!/usr/bin/python
# -*- coding: utf8
import graphine

__author__ = 'mkompan'

from graph_state_builder_static import gs_builder
import swiginac
from rggraphenv.symbolic_functions import safe_integer_numerators, safe_integer_numerators_strong, e, zeta, var, Pi, series


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
        res = res.subs(var('r%s' % i)==eval(safe_integer_numerators_strong(ri['r%s' % i])))
    return res


if __name__ == "__main__":
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
    print "\ngamma_g = ", gamma_g
    print "\nbeta = ", beta
    print "\ngamma_f = ", gamma_f
    print
    print "\ngamma_g = ", substitute_r(gamma_g, ri).expand()
    print "\nbeta = ", substitute_r(beta, ri).expand()
    print "\ngamma_f = ", substitute_r(gamma_f, ri).expand()

    a = var('a')
    gstar = e*a
    n = var('n')
    for i in range(1, loops4+1):
        # print "\n\n\n", i
        beta1 = series((substitute_r(beta, ri)/g), g, 0,  i+1, remove_order=True).expand()
        eq = series(beta1.subs(g==gstar), e, 0, i+1, remove_order=True)
        # print beta1
        # print beta1.subs(g==gstar)
        # print "eq", eq.expand().normal()
        # print "eq", eq.expand().subs(n==1)
        # print eq.coeff(a), eq.subs(a==0).expand().normal()

        gstar = gstar.subs(a==-eq.subs(a==0).expand().normal()/eq.coeff(a))+e**(i+1)*a

        # print gstar
        # print series(gstar,e,0,i+2).normal()
        # print series(gstar,e,0,i+2).subs(n==1)


    print
    gstar_ = series(gstar.subs(a==0),e,0,loops4+1)
    print series(gstar.subs(a==0),e,0,loops4+1).subs(n==1)


    eta = series(2*substitute_r(gamma_f, ri).subs(g==gstar_),e,0, loops2+1)

    print "eta"
    print eta.subs(n==1)
    print eta.subs(n==1).subs(e==e/2).evalf()