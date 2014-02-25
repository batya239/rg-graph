#!/usr/bin/python
# -*- coding: utf8
import graphine

__author__ = 'mkompan'

from graph_state_builder_static import gs_builder
import swiginac
from rggraphenv.symbolic_functions import safe_integer_numerators_strong, e, zeta, var, Pi, series, tgamma

#from ch import H
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


# def renormalization_constants(diagrams_dict, structures_dict):
def renormalization_constants(diagrams_dict):
    Z1 = swiginac.numeric('1')
    Z3 = swiginac.numeric('1')
    g = var('g')
    for gs_string in sorted(diagrams_dict.keys()):
        gs = gs_builder.graph_state_from_str(gs_string)
        graph = graphine.Graph(gs)
        print gs, symmetry_coefficient(gs)
        if graph.externalEdgesCount() == 2:

            Z1 += symmetry_coefficient(gs) \
                  * eval(safe_integer_numerators_strong(diagrams_dict[gs_string])) \
                  * (g) ** graph.getLoopsCount()
                  # * eval(safe_integer_numerators_strong(structures_dict[gs_string])) \

        elif graph.externalEdgesCount() == 3:
            Z3 -= symmetry_coefficient(gs) \
                  * eval(safe_integer_numerators_strong(diagrams_dict[gs_string])) \
                  * (g) ** graph.getLoopsCount()
                  # * eval(safe_integer_numerators_strong(structures_dict[gs_string])) \
        else:
            raise NotImplementedError("ext legs count: %s" % graph.externalEdgesCount())
    return Z1, Z3



def calculate_gstar(beta_n, loops_count):
    a = var('a')
    g = var('g')
    gstar = e*a
    for i in range(1, loops_count+1):
        print
        print i
        beta1 = series((beta_n/g), g, 0,  i+1, remove_order=True).expand()
        eq = series(beta1.subs(g == gstar), e, 0, i+1, remove_order=True)
        gstar = gstar.subs(a == -eq.subs(a == 0).expand().normal()/eq.coeff(a))+e**(i+1)*a

        print beta1
        print eq
        print gstar

    gstar_ = series(gstar.subs(a == 0), e, 0, loops_count+1)
    return gstar_




if __name__ == "__main__":
    n = var('n')
    loops2 = 3
    loops3 = 3
    from phi3_3loop_res import ms

    # from On_structures_6loop import on
    # from ri import ri

    g = var('g')
    Z1, Z3 = renormalization_constants(ms)
    Z1 = series(Z1, g, 0, loops2 + 1).expand().collect(g)
    Z3 = series(Z3, g, 0, loops3 + 1).expand().collect(g)

    print Z1.evalf()
    print Z3.evalf()
#    Zg = series(Z3 / Z1 ** (swiginac.numeric(3)/2), g, 0, loops3 + 1)
    Zu = series(Z3**2 / Z1 ** (swiginac.numeric(3)), g, 0, loops3 + 1)
    print Zu
    log_diff_Zu = g * swiginac.log(Zu).diff(g)
    gamma_g = series(-2*e * log_diff_Zu / (1 + log_diff_Zu), g, 0, loops3 + 1).expand()
    beta = series(-2*e * g / (1 + log_diff_Zu), g, 0, loops3 + 2).expand()
    gamma_f = series(-( 2*e + gamma_g) * g * swiginac.log(Z1).diff(g) / 2, g, 0, loops2 + 1).expand()

    print
    print "\ngamma_g = ", gamma_g
    print "\nbeta = ", beta
    print "\ngamma_f = ", gamma_f


    gstar = calculate_gstar(beta, loops3)
    print
    print "gstar = ", gstar
    print



    eta = series(2*gamma_f.subs(g == gstar), e, 0, loops2+1, remove_order=True)

    print "eta (d=6-2*e)"
    print eta.subs(e == e/2).expand()
    print eta.subs(e == e/2).evalf()


