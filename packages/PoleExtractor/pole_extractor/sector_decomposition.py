__author__ = 'gleb'

import graph_state
import graphine
import itertools
import reduced_vl
import polynomial
import copy


def sectors(rvl):
    """
    returns sectors as tuple of elements (coef, sector), where
    coef is a symmetry coefficient, and
    sector is sector as ((main_variable_1, ()), (main_variable_1, ()), ...)
    """
    assert (isinstance(rvl, reduced_vl.ReducedVacuumLoop))
    conservation_laws = rvl.conservation_laws(exclude_ext_edges=True)

    loops_number = rvl.loops()
    variable_list = rvl.edges()

    dec_subspace = variable_list
    main_vars = tuple(itertools.permutations(dec_subspace, loops_number))
    result = []
    sector = []

    for p in main_vars:
        for edge in p:
            dec_subspace = tuple(x for x in dec_subspace if x != edge)
            sector.append((edge, dec_subspace))
        result.append(sector)
        sector = []
        dec_subspace = variable_list

    for law in conservation_laws:
        # removing sectors that have conservation laws in their main variables
        for i in reversed(range(len(result))):
            if set(map(lambda x: x[0], result[i])).issuperset(set(law)):
                result.pop(i)

        # removing sectors that are unnecessary after removing ones with conservation laws
        for sector in result:
            for i in range(1, len(sector)):
                main_vars = map(lambda x: x[0], sector[:i])
                if not len(set(law) - set(main_vars)) == 1:
                    continue
                for j in range(i, len(sector)):
                    if set(main_vars + list(sector[j][1])).issuperset(set(law)):
                        sector[j] = (sector[j][0], tuple(x for x in sector[j][1] if x not in law))

    for i in range(len(result)):
        result[i] = tuple(filter(lambda x: not len(x[1]) == 0, result[i]))

    return tuple(map(lambda x: (1, x), result))


def reduce_symmetrical_sectors(ns_sectors, graph):
    def note_sector(sector, graph_edges):
        palette = map(lambda x: x[0], sector[1])
        edges_list = map(lambda x: graph_state.Edge(nodes=x[1].nodes, colors=palette.index(x[0])+1)
                         if x[0] in palette else graph_state.Edge(nodes=x[1].nodes, colors=0),
                         enumerate(graph_edges))
        return graphine.Graph(edges_list)

    assert(isinstance(graph, graphine.Graph))
    g_edges = graph.allEdges(nickel_ordering=True)
    sector_labels = map(lambda x: str(note_sector(x, g_edges)), ns_sectors)

    seen = set([])
    return [(sector_labels.count(str(note_sector(s, g_edges))), s[1]) for s in ns_sectors
            if str(note_sector(s, g_edges)) not in seen and not seen.add(str(note_sector(s, g_edges)))]
