#!/usr/bin/python
# -*- coding: utf8
import copy
import symbolic_functions

__author__ = 'dimas'

import os
import itertools
from rggraphutil import ref
import graphine

import jrules_parser
import sector
import reduction_util


class ReductorHolder(object):
    def __init__(self, *reductors):
        self._reductors = reductors

    def calculate(self, graph):
        for r in self._reductors:
            v = r.calculate(graph)
            if v is not None:
                return v


class Reductor(object):
    def __init__(self,
                 env_name,
                 env_path,
                 propagators,
                 topologies,
                 all_propagators_count,
                 main_loop_count_condition,
                 masters):
        self._env_name = env_name
        self._env_path = env_path
        self._propagators = propagators
        self._topologies = reduce(lambda ts, t: ts | _enumerate_graph(t, self._propagators, to_sector=False),
                                  topologies,
                                  set())
        self._all_propagators_count = all_propagators_count
        self._main_loop_count_condition = main_loop_count_condition
        self._sector_rules = list()
        self._zero_sectors = list()
        self._open_j_rules()
        self._masters = dict()
        for m, v in masters.items():
            for enumerated in _enumerate_graph(m, self._propagators, to_sector=True):
                self._masters[enumerated] = v

    def _open_j_rules(self):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self._env_path)

        zero_sectors = jrules_parser.read_raw_zero_sectors(os.path.join(dir_path, "ZeroSectors[%s]" % self._env_name),
                                                           self._env_name)
        self._sector_rules.extend(zero_sectors[1])
        self._zero_sectors = zero_sectors[1]
        for f in os.listdir(dir_path):
            if f.startswith("jRules"):
                map(lambda r: self._sector_rules.append(r),
                    jrules_parser.x_parse_rules(os.path.join(dir_path, f), self._env_name, zero_sectors[0]))

    def calculate(self, graph):
        if graph.getLoopsCount() != self._main_loop_count_condition:
            return None
        return self._try_calculate(graph)

    def _try_calculate(self, graph):
        sectors = sector.Sector.create_from_topologies_and_graph(graph, self._topologies, self._all_propagators_count) \
            .as_sector_linear_combinations()
        while len(sectors):
            raw_sectors = sectors.sectors_to_coefficient.keys()
            not_masters = list()
            for s in raw_sectors:
                is_break = False
                for r in self._zero_sectors:
                    if r.is_applicable(s):
                        sectors = sectors.remove_sector(s)
                        is_break = True
                        break
                if is_break:
                    continue
                if s not in self._masters.keys():
                    not_masters.append(s)

            if not len(not_masters):
                break

            biggest = reduction_util.choose_max(not_masters)
            is_updated = False
            for rule in self._sector_rules:
                if rule.is_applicable(biggest):
                    new_sectors = rule.apply(biggest)
                    sectors = sectors.replace_sector_to_sector_linear_combination(biggest, new_sectors)
                    is_updated = True
                    break

            if not is_updated:
                return None
        value = sectors.get_value(self._masters)
        return value


_MAIN_REDUCTION_HOLDER = ref.Ref.create()


def initialize():
    #three_loop_reductor = Reductor("loop3",
    #                               "loop3",
    #                               [graphine.Graph.fromStr("e12-34-35-4-5-e-::[None, 1, 0, 2, 8, 7, 5, 4, 6, None]"),
    #                                graphine.Graph.fromStr("e12-34-35-4-5-e-::[None, 1, 0, 7, 6, 2, 3, 4, 8, None]"),
    #                                graphine.Graph.fromStr("e12-34-35-4-5-e-::[None, 8, 3, 2, 1, 4, 5, 7, 6, None]")],
    #                               9,
    #                               3,
    #                               [("P1", "e112-22-e-", ("G(1,1)*G(1,1)*G(2-2*e,1)", (2, -3))),
    #                                ("P2", "e11-222-e-", ("G(1,1)*G(1,1)*G(1-e,1)", (2, -3))),
    #                                ("P3", "e1111-e-", ("G(1,1)*G(1-e,1)*G(1-2*e,1)", (1, -3))),
    #                                ("L1", "e12-223-3-e-", ("(swiginac.exp(-3*swiginac.Euler*e)*(1./3/e/e/e+"
    #                                                        "7./3/e/e+"
    #                                                        "(31./3-Pi**2/12)/e+"
    #                                                        "(103./3-7*Pi**2/12+7*zeta(3)/3)+"
    #                                                        "e*(235./3-31*Pi**2/12+49*zeta(3)/3+5*Pi**4/96)+"
    #                                                        "e**2*(19./3-103*Pi**2/12+289*zeta(3)/3+35*Pi**4/96-7*Pi**2*zeta(3)/12+599*zeta(5)/5)))",
    #                                                        (3, -3)))])

    G = symbolic_functions.G
    l = symbolic_functions.l
    two_loop_reductor = Reductor("loop2",
                                 "loop2",
                                 #[(0, -1, 0),
                                 # (1, 1, 0),
                                 # (0, -1, 1),
                                 # (0, 0, -1),
                                 # (1, 0, 1)],
                                 [(0, 1, 0),
                                 (1, 1, 0),
                                 (0, 1, -1),
                                 (0, 0, 1),
                                 (1, 0, 1)],
                                 [graphine.Graph.fromStr("e12-23-3-e-")],
                                 5,
                                 2,
                                 {graphine.Graph.fromStr("e111-e-"): G(1, 1) * G(1 - l, 1),
                                  graphine.Graph.fromStr("e11-22-e-"): G(1, 1) ** 2})

    _MAIN_REDUCTION_HOLDER.set(ReductorHolder(two_loop_reductor))


def calculate(graph):
    return _MAIN_REDUCTION_HOLDER.get().calculate(graph)


def _enumerate_graph(graph, init_propagators, to_sector=True):
    """
    propagators - iterable of tuples (1, 0, -1) = q - k2

    to_sector = True => return sector.Sector
    to_sector = False => return graphine.Graph with corresponding colors
    """
    external_propagator = (1,) + (0,) * (len(init_propagators[0]) - 1)
    mapped_external_edges = map(lambda e: e.copy(colors=None), graph.externalEdges())
    internal_edges = graph.internalEdges()
    result = set()
    for i in xrange(len(init_propagators)):
        for comb in itertools.combinations(xrange(len(init_propagators)), i):
            propagators = copy.copy(init_propagators)
            for c in comb:
                propagators[c] = tuple(map(lambda q: -q, propagators[c]))
            enumerated = [x for x in enumerate(propagators)]
            for ps in itertools.permutations(enumerated, len(internal_edges)):
                _ps = dict(enumerated)
                _ps[None] = external_propagator
                mapped_internal_edges = map(lambda pair: pair[1].copy(colors=abs(pair[0][0])), zip(ps, internal_edges))
                graph = graphine.Graph(mapped_external_edges + mapped_internal_edges,
                                       externalVertex=graph.externalVertex)
                valid = True
                for v in graph.vertices():
                    if v is not graph.externalVertex:
                        vertex_edges = graph.edges(v)
                        if not _check_vertex_edges(v, vertex_edges, _ps):
                            valid = False
                            break
                if valid:
                    if not to_sector:
                        result.add(graph)
                    else:
                        raw_sector = [0] * len(init_propagators)
                        for p in ps:
                            raw_sector[p[0]] = 1
                        result.add(sector.Sector(raw_sector))
    return result


def _check_vertex_edges(vertex, edges, propagators):
    sequence = zip(*map(lambda e: propagators[e.colors[0] if e.colors else None] if (vertex == e.nodes[0] or (vertex != 0 and e.nodes[0] == -1))
                        else tuple(map(lambda q: -q, propagators[e.colors[0] if e.colors else None])), edges))
    _sum = map(lambda ps: sum(ps), sequence)
    for x in _sum:
        if x != 0:
            return False
    return True
