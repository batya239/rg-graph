#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import momentum_enumeration
import uv
import graphine
import propagator
import sympy
import one_loop_reduction
from rggraphutil import emptyListDict, Ref
from rggraphenv import symbolic_functions

one_irreducible = graphine.filters.one_irreducible
no_tadpoles = graphine.filters.no_tadpoles


def determine_omega_sign(loop_graph, new_vertices, vertex_transformation, bubbles_as_graph):
    bound_vertices = list(loop_graph.get_bound_vertices())
    assert len(bound_vertices) == 2
    first_vertex = bound_vertices[0]
    last_vertex = bound_vertices[1]

    propagators = list()
    subgraphs = list()

    for sign, e in zip((1, -1), filter(lambda e: not e.is_external(), loop_graph.edges(first_vertex))):

        current_node = e.co_node(first_vertex)
        current_edge = e


        while True:
            print current_edge, sign, e.flow.get_propagator(sign)
            propagators.append(e.flow.get_propagator(sign))

            if current_node in vertex_transformation.mapping.values():
                subgraph = None
                for sg in bubbles_as_graph:
                    node_repr = sg[0][0]
                    if vertex_transformation.mapping[node_repr] == current_node:
                        subgraph = sg
                        break
                subgraphs.append((subgraph, sign))

            if current_node == last_vertex:
                break

            cur_edges = set(loop_graph.edges(current_node)) - {current_edge}
            assert len(cur_edges) == 1, cur_edges
            next_edge = list(cur_edges)[0]
            next_node = next_edge.co_node(current_node)

            current_node = next_node
            current_edge = next_edge

    return propagators, subgraphs


def construct_expression(graph):
    bubbles = list()
    bubbles_as_graph = list()
    graph = momentum_enumeration.choose_minimal_momentum_flow(graph)
    print graph
    graph = propagator.subs_external_propagators_is_zero(graph)
    for sg in graph.x_relevant_sub_graphs(one_irreducible + no_tadpoles + uv.uv_condition):
        if str(sg).startswith("e11|e|:"):
            bubbles.append(tuple(map(lambda e: e.nodes, sg.internal_edges)))
            bubbles_as_graph.append(sg)
        else:
            raise AssertionError("Only bubble subgraphs are accepted")
    if not len(bubbles):
        raise AssertionError("Diagram have no divergences")

    loop_graph, new_vertices, vertex_transformation = graph.batch_shrink_to_point(bubbles_as_graph, with_aux_info=True)

    propagators, subgraphs = determine_omega_sign(loop_graph, new_vertices, vertex_transformation, bubbles)

    free_edges = list()
    bubbles_ = emptyListDict()
    for e in graph:
        if e.is_external():
            continue
        nodes = e.nodes
        bubble_idx = None
        for idx, b in enumerate(bubbles):
            if nodes in b:
                bubble_idx = idx
                break
        if bubble_idx is None:
            free_edges.append(e)
        else:
            bubbles_[bubble_idx].append(e)

    free_part = sympy.numer(1)
    for p in propagators:
        free_part *= p
        free_part = free_part.simplify()
        free_part = sympy.re(free_part) + sympy.I * sympy.im(free_part)
    free_part = free_part.simplify()
    free_part = sympy.numer(1) / free_part
    free_part = sympy.re(free_part) + sympy.I * sympy.im(free_part)

    bubbles_part = map(lambda (es, s): s, subgraphs)

    w = one_loop_reduction.w

    def build_expr(pseudo_expr, do_diff_):
        if isinstance(pseudo_expr, Ref):
            pseudo_expr = pseudo_expr.get()
            expr_ = one_loop_reduction.P_R0() if do_diff_ else one_loop_reduction.P_R2()
            if pseudo_expr == -1:
                expr_ = expr_.subs({w: -w})
            return expr_
        else:
            t = sympy.Symbol("t", positive=True)
            return (pseudo_expr if not do_diff_ else (- pseudo_expr).diff(t)).subs({t : 1})

    def do_diff(main_part, bubbles_part):
        bubbles_part = list(bubbles_part)
        main_part = [main_part]
        all_parts = main_part + bubbles_part

        diff = list()
        for p in all_parts[0:]:
            #TODO [1:]
            current_expr = 1
            for _p in all_parts:
                # expr1 = build_expr(_p, False) # p is _p)
                expr1 = build_expr(_p,  p is _p)
                # print "MATHEMATICA", sympy.printing.mathematica_code(expr1)
                print expr1
                current_expr *= expr1
            print "NEXT"
            expr = current_expr + current_expr.subs({w: -w})
            # print "ALL EXPR", sympy.re(expr)
            print "IM PART", sympy.im(expr).simplify()
            # print "MATHEMATICA", sympy.printing.mathematica_code(current_expr)
            diff.append(sympy.re(expr))
            # break
            # TODO remove
        return reduce(lambda x, y: x + y, diff, 0)

    print "bubbles", bubbles_part

    expression = do_diff(free_part, map(lambda s: Ref(s), bubbles_part))
    expression *= one_loop_reduction.x

    y = sympy.Symbol("y", positive=True)
    z = sympy.Symbol("z", positive=True)
    print expression

    expression = expression.subs({one_loop_reduction.x: (sympy.numer(1)-y)/y, one_loop_reduction.w: (sympy.numer(1)-z)/z})
    expression /= y * y * z * z

    import cuba_integration
    from integration import Integration
    integrations = [Integration(y, 0, 1), Integration(z, 0, 1)]
    value = cuba_integration.cuba_integrate({0: expression}, integrations , list())
    import uncertainties
    print value[0] / 4 / uncertainties.ufloat(sympy.pi.evalf(), 0)
    # print -0.0139663
    # -0.00214505826368+/-1.3601428000924723e-05}
    # {0: -0.002135552138923125+/-4.0706724375e-08})
    # -0.00058760+/-0.00000006


    # 0: -0.00046169307512+/-9.890864118162647e-06} Eto k zelim Pi/2



    # 0.0010029+/-0.0000017 Eto nash otvet
    # -0.0003240+/-0.0000015

    # -0.00065337529872


import configure_mr
configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(200000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-9).\
    with_integration_algorithm("vegas").\
    with_debug(True).configure()
import graph_util_mr
# g = graph_util_mr.from_str("e12|e3|33||:0A_aA_aA|00_Aa|aA_aA||::::")
g = graph_util_mr.from_str("e12|e3|44|55|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA||::::")
# g = graph_util_mr.from_str("e12|3|44|5|6|e7|77||:0A_aA_aA|aA|aA_aA|aA|aA|0a_Aa|aA_aA||::::")
import diff_util_mr
assert len(diff_util_mr.D_i_omega(g)) == 1
g = diff_util_mr.D_i_omega(g)[0]
construct_expression(g)