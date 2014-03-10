__author__ = 'dima'


import itertools
import spherical_coordinats
import graph_util_mr
from rggraphutil import zeroDict
from rggraphenv import symbolic_functions


class ScalarProductAlgebraElement(object):
    def momentum_pairs(self):
        raise NotImplementedError()

    def substitute(self, substitutor):
        raise NotImplementedError()

    def __add__(self, other):
        return _Sum(self, other)

    def __mul__(self, other):
        return _Prod(self, other)


class ScalarProduct(ScalarProductAlgebraElement):
    def __init__(self, flow1, flow2, sign):
        assert sign is not None
        self._flow1 = flow1
        self._flow2 = flow2
        self._unordered_pairs = ScalarProduct.resolve_flows(flow1, flow2)
        self._sign = sign

    @staticmethod
    def resolve_flows(flow1, flow2):
        assert not flow1.is_external()
        assert not flow2.is_external()
        unordered_pairs_to_coefficient = zeroDict()
        for p in itertools.product(enumerate(flow1.loop_momentas),  enumerate(flow2.loop_momentas)):
            if p[0][1] != 0 and p[1][1] != 0:
                unordered_pairs_to_coefficient[frozenset((p[0][0], p[1][0]))] += p[0][1] * p[1][1]
        return unordered_pairs_to_coefficient

    def momentum_pairs(self):
        return set(self._unordered_pairs.keys())

    def substitute(self, substitutor):
        result = symbolic_functions.CLN_ZERO
        for p in itertools.product(enumerate(self._flow1.loop_momentas),  enumerate(self._flow2.loop_momentas)):
            if p[0][1] != 0 and p[1][1] != 0:
                k = frozenset((p[0][0], p[1][0]))
                r = p[0][1] * p[1][1]
                if len(k) == 2:
                    r *= symbolic_functions.var("k%s" % p[0][0])
                    r *= self._flow1.get_stretcher_for_var_index(p[0][0])
                    r *= symbolic_functions.var("k%s" % p[1][0])
                    r *= self._flow2.get_stretcher_for_var_index(p[1][0])
                    r *= substitutor[k].fake_variable
                elif len(k) == 1:
                    r *= symbolic_functions.var("k%s" % (list(k))[0]) ** 2
                else:
                    raise AssertionError(k)
                result += r
        return result * self._sign

    def __str__(self):
        return "SP(%s, %s)" % (self._unordered_pairs, self._sign)

    __repr__ = __str__


class _Sum(ScalarProductAlgebraElement):
    def __init__(self, *elements):
        self._elements = elements

    def momentum_pairs(self):
        pairs = set()
        for e in self._elements:
            pairs |= e.momentum_pairs()
        return pairs

    def substitute(self, substitutor):
        return reduce(lambda x, y: x + y.substitute(substitutor), self._elements)


class _Prod(ScalarProductAlgebraElement):
    def __init__(self, *elements):
        self._elements = elements

    def momentum_pairs(self):
        pairs = set()
        for e in self._elements:
            pairs |= e.momentum_pairs()
        return pairs

    def substitute(self, substitutor):
        return reduce(lambda x, y: x * y.substitute(substitutor), self._elements, 1)


def extract_scalar_products(graph):
    extracted_numerated_edges = list()
    for e in graph.allEdges():
        if e.arrow is not None and not e.arrow.is_null():
            extracted_numerated_edges.append(e)
    if len(extracted_numerated_edges) == 0:
        return None
    elif len(extracted_numerated_edges) == 2:
        raw_common_vertex = set(extracted_numerated_edges[0].nodes) & set(extracted_numerated_edges[1].nodes)
        if not len(raw_common_vertex):
            sign = resolve_scalar_product_sign(graph, extracted_numerated_edges)
        else:
            common_vertex = raw_common_vertex.pop()
            adjusted_numerators = map(lambda e: e.arrow if e.nodes[0] == common_vertex else -e.arrow, extracted_numerated_edges)
            sign = -1 if adjusted_numerators[0] == adjusted_numerators[1] else 1

        sp = ScalarProduct(extracted_numerated_edges[0].flow,
                           extracted_numerated_edges[1].flow,
                           sign=sign)
        return sp
    else:
        raise AssertionError(str(graph))


def resolve_scalar_product_sign(graph, extracted_numerated_edges):
    momentum_passing = map(lambda e: e.nodes, filter(lambda e: e.marker == graph_util_mr.MARKER_1, graph.allEdges()))
    momentum_passing.remove(extracted_numerated_edges[0].nodes)
    for j in xrange(2):
        current_node = extracted_numerated_edges[0].nodes
        current_vertex = current_node[j]
        sign = (1 if extracted_numerated_edges[0].arrow.is_left() else -1) * ((-1) ** j)
        while True:
            nodes_found = False
            for n in momentum_passing:
                if n != current_node and current_vertex in n:
                    current_node = n
                    current_vertex = filter(lambda i: i != current_vertex, current_node)[0]
                    momentum_passing.remove(current_node)
                    nodes_found = True
                    break
            if not nodes_found:
                break
            if current_node == extracted_numerated_edges[1].nodes:
                sign *= (1 if extracted_numerated_edges[1].arrow.is_left() else -1)
                sign *= 1 if current_vertex == current_node[0] else -1
                return sign