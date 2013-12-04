__author__ = 'gleb'

import _conserv as conserv
import graphine


class ReducedVacuumLoop:
    """
    ReducedVacuumLoop class is everything you need (and nothing you don't) to
    build Feynman's representation: all conservation laws with >2 edges involved
    and all 2-edge conservation laws in form of how-many-times-is-edge-repeated
    dictionary.
    """

    def __init__(self, e_weights, cons_laws, loops, zero_momenta=True):
        self._ew_dict = e_weights
        self._cons_laws = cons_laws
        self._loops = loops
        self._zero_momenta = zero_momenta

    def edges(self):
        if self.zero_momenta():
            return self._ew_dict.keys()
        else:
            return sorted(self._ew_dict.keys())[:-1]

    def edges_weights(self):
        if self.zero_momenta():
            return self._ew_dict.values()
        else:
            return [self._ew_dict[k] for k in self._ew_dict.keys() if not k == max(self._ew_dict.keys())]

    def edges_with_weights(self):
        if self.zero_momenta():
            return self._ew_dict.items()
        else:
            return [(k, self._ew_dict[k]) for k in self._ew_dict.keys() if not k == max(self._ew_dict.keys())]

    def conservation_laws(self, exclude_ext_edges=False):
        if exclude_ext_edges and not self.zero_momenta():
            return map(lambda x: filter(lambda y: not y == max(self._ew_dict.keys()), x), self._cons_laws)
        else:
            return self._cons_laws

    def internal_conservation_laws(self):
        return filter(lambda x: max(self._ew_dict.keys()) not in x, self._cons_laws)

    def loops(self):
        return self._loops

    def zero_momenta(self):
        return self._zero_momenta

    @staticmethod
    def fromGraphineGraph(graphine_graph, zero_momenta=True):
        assert (type(graphine_graph) == graphine.Graph)
        assert (zero_momenta or (graphine_graph.externalEdgesCount() == 2))

        node_pair_list = map(lambda x: x.nodes, graphine_graph.allEdges(nickel_ordering=True))
        if not zero_momenta:
            ext_edges = filter(lambda x: -1 in x, node_pair_list)
            node_pair_list.append(tuple(filter(lambda x: x != -1, sum(map(lambda x: list(x), ext_edges), []))))
        vl_as_dict = {n: e for n, e in enumerate(node_pair_list) if -1 not in e}
        all_conservation_laws = sorted([tuple(sorted(list(law))) for law in
                                        list(conserv.Conservations(vl_as_dict))])

        internal_edges_nums = vl_as_dict.keys()
        pair_cls = filter(lambda x: 2 == len(x), all_conservation_laws)
        n_pair_cls = filter(lambda x: 2 != len(x), all_conservation_laws)
        for law in pair_cls:
            internal_edges_nums = [law[1] if x == law[0] else x for x in internal_edges_nums]
            n_pair_cls = map(lambda x: [] if law[0] in x and law[1] in x else
                             tuple(sorted(map(lambda y: law[1] if y == law[0] else y, x))), n_pair_cls)
        edges_weights = {e: internal_edges_nums.count(e) for e in internal_edges_nums}
        n_pair_cls = tuple(set(filter(lambda x: 0 != len(x), n_pair_cls)))
        return ReducedVacuumLoop(e_weights=edges_weights,
                                 cons_laws=n_pair_cls,
                                 loops=graphine_graph.getLoopsCount(),
                                 zero_momenta=zero_momenta)

    def __str__(self):
        s = '{Edges: ' + str(self._ew_dict) + \
            ', Loops: ' + str(self._loops) + \
            ', Conservation laws: ' + str(self._cons_laws)
        if not self.zero_momenta():
            s += ', Ext momenta edge: ' + str(max(self._ew_dict.keys()))
        s += '}'
        return s

    def __repr__(self):
        return str(self)