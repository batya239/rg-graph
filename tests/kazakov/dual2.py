
import time
import sympy
import sys
import graph_state
import drawG4planar

__author__ = 'mkompan'

from graph_state_builder_dual import gs_builder as gs_builder_dual
from graph_state_builder_loops import gs_builder, Rainbow
import graphine
import dual_lib




dualgraphs_origin = dict()
dualgraphs_factor = dict()
for gs_string in open(sys.argv[1]).readlines():
    gs = gs_builder.graph_state_from_str("%s:" % gs_string.rstrip())
    print gs

    g = graphine.Graph(gs)



    start = time.time()
    try:
        coloured_graph = dual_lib.graph_with_momenta(g)
        dual = dual_lib.dual_graph(coloured_graph)
    except:
        print "Failed to construct dual graph"
        sys.exit(1)
    finally:
        print time.time()-start

    pairs = dual_lib.generate_pairings(dual)
    if len(pairs) == 0:
        print "no pairings"
        sys.exit(1)

    print g, "dual:", dual
    print "pairs", pairs
    print time.time()-start
    print
    for pairing in pairs:
        for orientation in [('s','t'), ('t','s')]:
            new_nodes = dict()
            for node in dual.vertices:
                if isinstance(node.n_num, str):
                    new_nodes[node] = gs_builder_dual.new_node(dual.create_vertex_index(), n_num=node.n_num+orientation[int(node.n_num[1])%2])
                else:
                    new_nodes[node] = node
            new_edges = list()
            for edge in dual.edges():
                new_edges.append(gs_builder_dual.new_edge(map(lambda x: new_nodes[x], edge.nodes), colors=0))
                # gs_builder_dual.new_edge(map(lambda x: new_nodes[x],edge.node), colors=(1,))
            coef = list()
            pairing_count = dict()
            for nodes in pairing:
                nodes = tuple(sorted(nodes))
                if nodes not in pairing_count:
                    pairing_count[nodes]=0
                pairing_count[nodes]+=1

            for nodes in pairing_count:
                st0 = dual_lib.extract_st(new_nodes[nodes[0]].n_num)
                st1 = dual_lib.extract_st(new_nodes[nodes[1]].n_num)
                if st0 == st1 and st1 in ('s', 't'):
                    coef += [st0]*pairing_count[nodes]
                else:
                    new_edges.append(gs_builder_dual.new_edge(map(lambda x: new_nodes[x], nodes), colors=pairing_count[nodes]))
            gs = graphine.Graph(graph_state.GraphState(new_edges))
            print gs
            gs_no_marks = dual_lib.remove_loop_marks(gs)
            if gs_no_marks not in dualgraphs_factor:
                dualgraphs_origin[gs_no_marks] = list()
                dualgraphs_factor[gs_no_marks] = list()
            # dualgraphs[gs]+=1

            dualgraphs_origin[gs_no_marks].append((coloured_graph, gs))
            dualgraphs_factor[gs_no_marks].append(sorted(coef))
        print


print
for gs in sorted(dualgraphs_factor.keys(), key=str):
    print gs
    print len(dualgraphs_factor[gs]), len(gs.to_graph_state().sortings),  dualgraphs_factor[gs]
    print "\tcoef =", sympy.Number(4)/len(gs.to_graph_state().sortings), "\t uv =", dual_lib.dual_uv_index(gs)
    print set(dualgraphs_origin[gs])
    if len(list(set(dualgraphs_origin[gs]))) != 1:
        print "Warning: origin len >1"
    graph, dual = list(set(dualgraphs_origin[gs]))[0]
    draw_attempts = 10
    index = drawG4planar._FIGURE_INDEX.next()
    print "index =", index
    while draw_attempts>0:
        draw_attempts -= 1
        try:
            drawG4planar.draw_planar_g4_dual(graph,
                                             dual,
                                             caption="%s\n$s^{%s}t^{%s}$ $%s$"%(graph.to_graph_state().topology_str(),
                                                                  dualgraphs_factor[gs][0].count('s'),
                                                                  dualgraphs_factor[gs][0].count('t'),
                                                                  sympy.Number(4)/len(gs.to_graph_state().sortings)),
                                             filename=str(gs),
                                             index=index)
            break
        except:
            continue
    print
print len(dualgraphs_factor)