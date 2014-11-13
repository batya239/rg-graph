#!/usr/bin/python
import copy
import itertools
import graphine
import conserv

__author__ = 'mkompan'

def det(edges_dict, nloops, cons):
    res = list()
    for c in itertools.combinations(edges_dict.keys(),nloops):
        c1 = set(c)
        invalid = False
        for con in cons:
            if c1 & con == con:
                invalid = True
                break
        if not invalid:
            res.append(c)
    return res


def conservations_for_chanel(edges_dict, chanel_pairs):
    edges_dict2 = copy.copy(edges_dict)
    edges_dict3 = copy.copy(edges_dict)
    edges_dict2[100] = chanel_pairs[0]
    edges_dict3[100] = chanel_pairs[1]
    cons2 = conserv.Conservations(edges_dict2)
    # print sorted(cons2,key=len)
    cons3 = conserv.Conservations(edges_dict3)
    # print sorted(cons3,key=len)
    return cons2|cons3

def C(edges_dict, nloops, chanel_pairs):
    cons = conservations_for_chanel(edges_dict, chanel_pairs)
    C = det(edges_dict, nloops+1, cons)
    return C


if __name__=="__main__":
    from graph_state_builder import gs_builder

    # gs = gs_builder.graph_state_from_str("e12|e3|45|46|7|e7|e7||:0_0_0|0_0|0_0|1_0|0|0_0|0_1||")
    # gs = gs_builder.graph_state_from_str("e12|e3|e3|e|:0_0_0|0_0|0_0|0|")
    gs = gs_builder.graph_state_from_str("e12|e3|34|5|e5|e|:")
    print gs
    g = graphine.Graph(gs)


    edges_dict = dict()
    for i in range(len(gs.edges)):
        edge = gs.edges[i]
        if not edge.is_external():
            edges_dict[i]=edge.nodes

    print edges_dict
    cons = conserv.Conservations(edges_dict)

    D = det(edges_dict, g.loops_count, cons)

    chanel_pairs = ([0, 5], [1, 6])
    chanel_pairs = ([0, 1], [5, 6])

    chanel_pairs = ([0, 4], [1, 5])
    chanel_pairs = ([0, 4], [0, 4])

    print
    # print sorted(C(edges_dict, g.loops_count, ([0, 5], [1, 6])))
    # print
    C = sorted(C(edges_dict, g.loops_count, chanel_pairs))
    print D
    print C
    # for edge in gs.edges:
    #     print edge.edge_id, edge.e_num if edge.e_num!=0 else ''
    cons_c = conservations_for_chanel(edges_dict, chanel_pairs)
    print sorted(cons_c, key=len)

    from sd_tools_graphine import gen_speer_tree1, xMSNTreeElement2
    tree = gen_speer_tree1(edges_dict.keys(), cons_c, depth=g.loops_count+1, skip_bad_branches=True)

    from polynomial import poly, pole_extractor, sd_lib
    poly_d = poly(map(lambda x: (1,x), D))
    poly_c = poly(map(lambda x: (1,x), C))
    print poly_d
    print poly_c

    for sector, c in xMSNTreeElement2(tree):
    # sectors = [
    #     [[(1,(2,4,5,6,7,9)),],1],
    #     [[(1,(2,4,5,6,7,9)),(5,(6,7,9))],1],
    #     [[(1,(2,4,5,6,7,9)),(5,(6,7,9)),(6,(7,))],1],
    #     ]
    # for sector, c in sectors:
        print sector
        print sd_lib.sectorPoly(poly_d, sector).factorize()
        print sd_lib.sectorPoly(poly_c, sector).factorize()
        print
