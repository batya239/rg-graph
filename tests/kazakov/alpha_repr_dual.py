#!/usr/bin/python
import copy
import itertools
import os
import graphine
import sys
import conserv
from polynomial import poly, pole_extractor, sd_lib
from polynomial.multiindex import CONST
from rggraphenv.symbolic_functions import tgamma, cln
fact = lambda x: tgamma(x+1)

import comb
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

def check_decomposition(polys):
    for poly_ in polys:
        if CONST in poly_.monomials:
            continue
        elif len(poly_.monomials)==1:
            continue
        else:
            return False
    return True

def sectorAlphaDiagram(expr, sector):
    expr_ = sd_lib.sectorDiagram(expr,sector,remove_delta=False)
    if expr_[1] == None:

        first_var = sector[0][0]
        return map(lambda x: x.set1toVar(first_var).simplify(),expr_[0])
    else:
        raise NotImplementedError, expr_

def simple_diff(det_as_list, var):
    res=list()
    for term in det_as_list:
        if var in term:
            term_=list(term)
            term_.remove(var)
            res.append(term_)
    return res

def simple_set0(det_as_list, var):
    res = list()
    for term in det_as_list:
        if var not in term:
            res.append(term)
    return res


def get_external_vertices(vertices):
    external_vertices = list()
    for v in vertices:

        if v.n_num != 0:
            external_vertices.append(v)
    return external_vertices

def dual_loops_count(g):
    vertices = g.vertices
    external = get_external_vertices(vertices)
    return len(vertices)-len(external)

def find_all_loops(edges_dict):
    loops = list()
    vertices = set(reduce(lambda x,y: x+y, map(lambda x: list(x.nodes), edges_dict.values())))
    external_vertices = get_external_vertices(vertices)
    for v in vertices:
        external = v in external_vertices
        routes = list()
        for edge_id in edges_dict:
            edge = edges_dict[edge_id]
            if v in edge.nodes:
                route = ([edge_id,], [v,edge.co_node(v)])
                routes.append(route)
        # print routes
        # print
        while len(routes) > 0:
            new_routes = list()
            for route in routes:
                edges, vertices = route
                for edge_id in edges_dict:
                    if edge_id in edges:
                        continue
                    edge = edges_dict[edge_id]
                    if vertices[-1] in edge.nodes:
                        v = edge.co_node(vertices[-1])
                        if v in vertices[1:]:
                            continue  # TODO: improve (actually loop)
                        if external:
                            if v in external_vertices:
                                loops.append(edges+[edge_id])
                                continue
                            else:
                                new_routes.append((edges+[edge_id], vertices+[v]))
                                continue
                        else:
                            if v == vertices[0]:
                                loops.append(edges+[edge_id])
                                continue
                            else:
                                new_routes.append((edges+[edge_id], vertices+[v]))
                                continue
            routes = new_routes
            # print loops
    loops = set(map(lambda x: frozenset(x), loops))
    return loops



if __name__=="__main__":
    # from graph_state_builder import gs_builder
    from graph_state_builder_dual import gs_builder

    # half_d = 3
    half_d = 4

    # gs = gs_builder.graph_state_from_str("1|234||||:0|0_0_0||||:s|0|s|t|t")  # box
    # gs = gs_builder.graph_state_from_str("1|234|3|45|||:0|0_0_0|0|0_0|||:s|0|t|0|t|s")  # double box
    # gs = gs_builder.graph_state_from_str("1|234|3|45|||:0|0_0_0|0|0_0|||:t|0|s|0|s|t")  # double box
    # gs = gs_builder.graph_state_from_str("1|234|345|5|5|6||:0|0_0_0|0_0_0|0|0|0||:s|0|0|t|t|0|s")  # triple box
    # gs = gs_builder.graph_state_from_str("1|234|345|5|5|6||:0|0_0_0|0_0_0|0|0|0||:t|0|0|s|s|0|t")  # triple box
    # gs = gs_builder.graph_state_from_str("1|2345|3|45|||:0|0_0_0_1|0|0_0|||:s|0|t|0|t|s")  # double box with one numerator
    # gs = gs_builder.graph_state_from_str("1|2345|3|45|||:0|0_0_0_2|0|0_0|||:s|0|t|0|t|s")  # double box with two numerators
    # gs = gs_builder.graph_state_from_str("1|2345|3|45|||:0|0_0_0_2|0|0_0|||:t|0|s|0|s|t")  # double box with two numerators
    # gs = gs_builder.graph_state_from_str("1|23456|3|45|5|6||:0|0_0_1_0_0|0|0_0|0|0||:s|0|t|0|s|0|t")  # K3 K4
    gs = gs_builder.graph_state_from_str("1|23456|3|45|5|6||:0|0_0_1_0_0|0|0_0|0|0||:t|0|s|0|t|0|s")  # K3 K4
    # gs = gs_builder.graph_state_from_str("1|234|34567|5|6|67|7||:0|0_0_0|0_0_0_0_1|0|0|0_0|0||:s|0|0|t|t|0|0|s")  # L3 L4
    # gs = gs_builder.graph_state_from_str("1|23456|34|45|567|6|||:0|0_0_1_0_0|0_0|0_0|0_0_0|0|||:t|0|s|0|0|0|s|t")  # L5 L6
    # gs = gs_builder.graph_state_from_str("1|234567|3|45|56|6|7||:0|0_0_0_2_0_0|0|0_0|0_0|0|0||:t|0|s|0|0|t|0|s")  # L7 L8
    # gs = gs_builder.graph_state_from_str("1|234567|3|45|56|6|7||:0|0_0_0_2_0_0|0|0_0|0_0|0|0||:s|0|t|0|0|s|0|t")  # L7 L8
    # gs = gs_builder.graph_state_from_str("1|23456|3|4567|57|7|7||:0|0_0_0_0_1|0|0_1_0_0|0_0|0|0||:t|0|s|0|0|s|t|0")  # L9 L10
    # gs = gs_builder.graph_state_from_str("1|23456|3|4567|57|7|7||:0|0_0_0_0_1|0|0_1_0_0|0_0|0|0||:s|0|t|0|0|t|s|0")  # L9 L10
    # gs = gs_builder.graph_state_from_str("12|234|3456|4|567|6|7||:0_0|0_0_0|1_0_0_0|0|1_0_0|0|0||:s|0|0|t|0|t|0|s")  # L11 L12
    # gs = gs_builder.graph_state_from_str("12|234|3456|4|567|6|7||:0_0|0_0_0|1_0_0_0|0|1_0_0|0|0||:t|0|0|s|0|s|0|t")  # L11 L12
    print gs
    g = graphine.Graph(gs)

    # edges_map = {0:1, 1:2, 6:6, 2:5 , 4:7 , 5:4, 10:8 , 8:9 , 7:11 , 9:13, 3:14 }
    edges_dict = dict()
    for i in range(len(gs.edges)):
        edge = gs.edges[i]
        if not edge.is_external():
            edges_dict[i]=edge
            # edges_dict[edges_map[i]]=edge
            # print edge.edge_id

    print edges_dict

    def cons_to_vertices(cons, edges_dict):

        vertices =  reduce(lambda x,y: x+y, map(lambda x:edges_dict[x].nodes, cons))
        res = list()
        for v in set(vertices):
            if vertices.count(v) ==1:
                res.append(v)

        # print res
        return set(res)

    def C(edges_dict, conservations, nloops):
        vertices = list(set(reduce(lambda x,y: x+y, map(lambda x: x.nodes, edges_dict.values()))))
        svertices = set(filter(lambda x: x.n_num=='s', vertices))
        tvertices = set(filter(lambda x: x.n_num=='t', vertices))
        internal_vertices = set(filter(lambda x: x.n_num==0, vertices))
        # print vertices
        # print svertices
        # print tvertices
        # print internal_vertices
        scons = set(filter(lambda x: (cons_to_vertices(x, edges_dict) & svertices) == svertices, conservations))
        tcons = set(filter(lambda x: (cons_to_vertices(x, edges_dict) & tvertices) == tvertices, conservations))
        # print scons
        # print cons_to_vertices((2,3,4,5),edges_dict)
        # print tcons
        cons_for_s_channel = conservations-tcons
        cons_for_t_channel = conservations-scons
        C_s = det(edges_dict, nloops+1, cons_for_s_channel)
        C_t = det(edges_dict, nloops+1, cons_for_t_channel)
        return C_s, C_t

    cons = find_all_loops(edges_dict)

    from dual_lib import dual_uv_index
    uv_index = dual_uv_index(g, half_d=half_d)
    if uv_index>0:
        C_s, C_t = C(edges_dict, cons, dual_loops_count(g))
        C_channels = {'s': poly(map(lambda x: (1,x), C_s)), 't': poly(map(lambda x: (1,x), C_t))}

    # print C_s
    # sys.exit()

    print uv_index








    D_ext = det(edges_dict, dual_loops_count(g), cons)
    # print sorted(D_ext), len(D_ext)
    print "len D_ext",  len(D_ext)
    # sys.exit()

    # sys.exit()
    # chanel_pairs = ([0, 5], [1, 6])
    # chanel_pairs = ([0, 1], [5, 6])
    #
    # chanel_pairs = ([0, 4], [1, 5])
    # chanel_pairs = ([0, 4], [0, 4])

    print
    # print sorted(cons_c, key=len)
    new_edges_dict = dict()
    dotted_edges = dict()
    for edge_id in edges_dict.keys():
        edge = edges_dict[edge_id]
        # print edge
        if edge.colors == 0:
            new_edges_dict[edge_id] = edge
        else:
            dotted_edges[edge_id] = edge.colors

    # print new_edges_dict
    # print dotted_edges
    # assert len(dotted_edges)==1
    # dotted_id = dotted_edges.keys()[0]
    # assert dotted_edges[dotted_id]==1


    from sd_tools_graphine import gen_speer_tree1, xMSNTreeElement2
    tree = gen_speer_tree1(new_edges_dict.keys(), cons, depth=dual_loops_count(g), skip_bad_branches=False)


    poly_d = poly(map(lambda x: (1,x), D_ext), degree=(-3,+1))

    M = map(lambda x: [x], filter(lambda x: x not in dotted_edges,new_edges_dict.keys()))
    poly_m = poly(map(lambda x: (1,x), M), degree=(0,-3))  # TODO: edges_dict or edges_dict1??



    for i in itertools.combinations_with_replacement(['s','t'], uv_index/2):
        expr_ =  poly_m
        prefix = "D%s_"%(half_d*2)+'_'.join(i)
        print "diff: ", prefix
        if len(i)>0:
            prefix+='_'
        for chanel in set(i):
            expr_ = expr_*C_channels[chanel].changeDegree(i.count(chanel)).changeConst(float(1/fact(i.count(chanel))))
        poly_d = poly(map(lambda x: (1,x), D_ext), degree=(-half_d-len(i), +1), c=float((-1.)**len(i)/dual_loops_count(g)))
        expr = [expr_*poly_d]

        print expr
        if uv_index>0:
            print C_channels
        # print C[chanel].changeDegree(i.count(chanel))
        print poly_d
        print poly_m


        for edge_id in dotted_edges:
            expr_diff = list()
            for term in expr:
                expr_diff += map(lambda x: x.set0toVar(edge_id), ((-1)**dotted_edges[edge_id]*term).diff(edge_id, count=dotted_edges[edge_id]))
            expr = expr_diff

        # print expr
        dir = os.path.join("sd_massive/", prefix+str(g))
        try:
            os.makedirs(dir)
        except OSError:
            pass
        if half_d==3:
            eps_order = 3-dual_loops_count(g)
        elif half_d == 4:
            eps_order = 1 - dual_loops_count(g)
        else:
            eps_order = -1
        import sd_tools_graphine as sd_tools
        for functions_file in sd_tools.generate_func_files(tree, lambda x: sectorAlphaDiagram(expr, x), eps_order):
            print os.path.join(dir, "%s.c" % functions_file.get_file_name(str(g))), functions_file.file_info, len(functions_file.functions), functions_file.functions_count
            f = open(os.path.join(dir, "%s.c" % functions_file.get_file_name(str(g))), "w")
            f.write(functions_file.get_c_file())
            f.close()
            f = open(os.path.join(dir, "%s.h" % functions_file.get_file_name(str(g))), "w")
            f.write(functions_file.get_h_file())
            f.close()
