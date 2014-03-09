#!/usr/bin/python
# -*- coding: utf8
import copy
from rggraphenv import symbolic_functions
import rggraphutil

__author__ = 'dimas'

import os
from rggraphutil import ref, VariableAwareNumber
from rggraphenv import abstract_graph_calculator
import graphine

import jrules_parser
import sector
import reduction_util
import graph_state
import scalar_product


e = symbolic_functions.e


DEBUG = False


class ReductorHolder(object):
    def __init__(self, reductors):
        self._reductors = reductors

    def is_applicable(self, graph):
        for r in self._reductors:
            if r.is_applicable(graph):
                return True
        return False

    def calculate(self, graph, scalar_product_aware_function=None):
        for r in self._reductors:
            v = r.calculate(graph, scalar_product_aware_function)
            if v is not None:
                return v
        return None


class StopSearchException(BaseException):
    pass


class RuleNotFoundException(BaseException):
    pass


def _enumerated_graph_as_sector(g, initial_propagators_len):
    raw_sector = [0] * initial_propagators_len
    for e in g.internalEdges():
        raw_sector[e.colors[0]] = 1
    return sector.Sector(raw_sector)


def _enumerate_graph(graph, init_propagators, to_sector=True, only_one_result=False):
    """
    propagators - iterable of tuples (1, 0, -1) = q - k2

    to_sector = True => return sector.Sector
    to_sector = False => return graphine.Graph with corresponding weight
    """

    empty_color = graph_state.Rainbow(("EMPTY",))
    def init_weight(graph, zeroColor=graph_state.Rainbow((0, 0)), unitColor=graph_state.Rainbow((1, 0))):
        edges = graph.allEdges()
        initedEdges = list()
        for e in edges:
            if e.weight is None:
                color = zeroColor if graph.external_vertex in e.nodes else unitColor
                initedEdges.append(graph_state.Edge(e.nodes, graph.external_vertex, colors=color))
            else:
                initedEdges.append(e)
        return graphine.Graph(initedEdges, external_vertex=graph.external_vertex, renumbering=False)
    graph = init_weight(graph, empty_color, empty_color)

    neg_init_propagators = dict()
    for p in init_propagators.values():
        neg_p = tuple(map(lambda q: -q, p))
        neg_init_propagators[p] = neg_p

    propagator_indices = dict()
    for p in init_propagators.items():
        propagator_indices[p[1]] = p[0]
        propagator_indices[neg_init_propagators[p[1]]] = p[0]

    momentum_count = len(init_propagators.values()[0])
    external_vertex = graph.external_vertex
    graph_vertices = graph.vertices()

    def _enumerate_next_vertex(remaining_propagators, _graph, vertex, result):
        if vertex not in graph_vertices:
            new_edges = map(lambda e_: e_.copy(colors=graph_state.Rainbow((propagator_indices[e_.colors], e_.colors.colors)) if not e_.is_external() else None),
                            _graph.allEdges())
            result.add(graphine.Graph(new_edges, external_vertex, renumbering=False))
            if only_one_result:
                raise StopSearchException()
            return
        vertex_known_factor = [0] * momentum_count
        not_enumerated = list()
        for e in _graph.edges(vertex):
            if e.colors is not empty_color:
                for i in xrange(momentum_count):
                    if vertex == e.nodes[0]:
                        vertex_known_factor[i] += e.colors[i]
                    else:
                        vertex_known_factor[i] -= e.colors[i]
            elif len(e.internal_nodes) == 1:
                if vertex == 0:
                    vertex_known_factor[0] += 1
                else:
                    vertex_known_factor[0] -= 1
            else:
                not_enumerated.append(e)
        if not len(not_enumerated):
            for x in vertex_known_factor:
                if x != 0:
                    return
            _enumerate_next_vertex(remaining_propagators, _graph, vertex + 1, result)
            return
        for index, remaining_propagator in remaining_propagators.items():
            neg_propagator = neg_init_propagators[remaining_propagator]
            for propagator in (remaining_propagator, neg_propagator):
                if len(not_enumerated) == 1:
                    is_zero = True
                    for x in zip(vertex_known_factor, propagator):
                        if x[0] + x[1] != 0:
                            is_zero = False
                            break
                    if is_zero:
                        new_remaining_propagators = copy.copy(remaining_propagators)
                        del new_remaining_propagators[index]
                        new_edges = copy.copy(_graph.allEdges())
                        new_edges.remove(not_enumerated[0])
                        new_edges.append(not_enumerated[0].copy(colors=graph_state.Rainbow(propagator)))
                        new_graph = graphine.Graph(new_edges, external_vertex=external_vertex, renumbering=False)
                        _enumerate_next_vertex(new_remaining_propagators, new_graph, vertex + 1, result)
                else:
                    new_remaining_propagators = copy.copy(remaining_propagators)
                    del new_remaining_propagators[index]
                    new_edges = copy.copy(_graph.allEdges())
                    new_edges.remove(not_enumerated[0])
                    new_edges.append(not_enumerated[0].copy(colors=graph_state.Rainbow(propagator)))
                    new_graph = graphine.Graph(new_edges, external_vertex=external_vertex, renumbering=False)
                    _enumerate_next_vertex(new_remaining_propagators, new_graph, vertex, result)

    _result = set()
    try:
        propagators_copy = copy.copy(init_propagators)
        _enumerate_next_vertex(propagators_copy, graph, 0, _result)
    except StopSearchException:
        pass
    if not to_sector:
        return _result
    else:
        return set(map(lambda g: _enumerated_graph_as_sector(g, len(init_propagators)), _result))


class ReductorResult(object):
    def __init__(self, final_sector_linear_combinations, masters):
        self._masters = masters
        self._final_sector_linear_combinations = final_sector_linear_combinations

    def __str__(self):
        return str(self._final_sector_linear_combinations)

    def evaluate(self, substitute_sectors=False, _d=None, series_n=-1, remove_o=True):
        if not substitute_sectors:
            return self._evaluate_unsubsituted(_d=_d, series_n=series_n, remove_o=remove_o)
        value = self._final_sector_linear_combinations.get_value(self._masters)
        return ReductorResult._evaluate_coefficient(value, _d=_d, series_n=series_n, remove_o=remove_o)

    def _evaluate_unsubsituted(self, _d=None, series_n=-1, remove_o=True):
        evaled_additional_part = ReductorResult._evaluate_coefficient(
            self._final_sector_linear_combinations.additional_part.evaluate(),
            _d=_d,
            series_n=series_n,
            remove_o=remove_o)
        evaled_sectors_to_coefficients = rggraphutil.zeroDict()
        for s, c in self._final_sector_linear_combinations.sectors_to_coefficient.items():
            evaled_sectors_to_coefficients[s] = ReductorResult._evaluate_coefficient(
                c.evaluate(),
                _d=_d,
                series_n=series_n,
                remove_o=remove_o).normal()
        return sector.SectorLinearCombination(evaled_sectors_to_coefficients, evaled_additional_part)

    @staticmethod
    def _evaluate_coefficient(c, _d=None, series_n=-1, remove_o=True):
        if _d is None:
            return c
        if isinstance(c, (float, int)):
            return c
        _c = c.subs(sector.d == _d)
        return (_c if series_n == -1 else symbolic_functions.series(_c,
                                                                    e,
                                                                    0,
                                                                    series_n,
                                                                    remove_order=remove_o)).expand().collect(e)


class Reductor(object):
    TOPOLOGIES_FILE_NAME = "topologies"
    MASTERS_FILE_NAME = "masters"

    CALLS_COUNT = 0

    def __init__(self,
                 env_name,
                 env_path,
                 topologies,
                 main_loop_count_condition,
                 masters):
        self._env_name = env_name
        self._env_path = env_path
        self._graph_topologies = topologies
        self._main_loop_count_condition = main_loop_count_condition
        self._graph_masters = masters

        self._propagators = None
        self._topologies = None
        self._zero_sectors = None
        self._sector_rules = None
        self._all_propagators_count = None
        self._masters = None
        self._masters_graph = None
        self._scalar_product_rules = None

        self._is_inited = False

    def initIfNeed(self):
        if self._is_inited:
            return
        self._propagators = jrules_parser.parse_propagators(self._get_file_path(self._env_name),
                                                            self._main_loop_count_condition)

        read_topologies = self._try_read_topologies()
        if read_topologies:
            self._topologies = read_topologies
        else:
            self._topologies = reduce(lambda ts, t: ts | _enumerate_graph(t, self._propagators, to_sector=False),
                                      self._graph_topologies,
                                      set())
            self._save_topologies()

        self._all_propagators_count = len(self._propagators)
        self._sector_rules = rggraphutil.emptyListDict()
        self._zero_sectors = list()
        self._open_reduction_rules()
        self._scalar_product_rules = list()
        self._open_scalar_product_rules()
        read_masters = self._try_read_masters()
        if read_masters:
            self._masters, self._masters_graph = read_masters
        else:
            self._masters = dict()
            self._masters_graph = dict()
            master_sectors = jrules_parser.parse_masters(self._get_file_path(self._env_name),
                                                         self._env_name)
            for m, v in self._graph_masters.items():
                for enumerated_g in _enumerate_graph(m, self._propagators, to_sector=False):
                    enumerated = _enumerated_graph_as_sector(enumerated_g, len(self._propagators))
                    if enumerated in master_sectors:
                        self._masters[enumerated] = v
                        self._masters_graph[enumerated] = str(enumerated_g)
            self._save_masters()
        self._is_inited = True

    @property
    def main_loops_condition(self):
        return self._main_loop_count_condition

    @property
    def env_name(self):
        """
        test only
        """
        return self._env_name

    @property
    def env_path(self):
        """
        test only
        """
        return self._env_path

    def evaluate_sector_size(self):
        """
        test only
        """
        for s in self._masters.keys():
            return len(s.propagators_weights)
        raise AssertionError()

    def _open_reduction_rules(self):
        dir_path = self._get_dir_path()

        zero_sectors = jrules_parser.read_raw_zero_sectors(os.path.join(dir_path, "ZeroSectors[%s]" % self._env_name),
                                                           self._env_name)
        self._zero_sectors = zero_sectors[1]
        for f in os.listdir(dir_path):
            if f.startswith("jRules"):
                map(lambda (k, r): self._sector_rules[k].append(r),
                    jrules_parser.x_parse_rules(os.path.join(dir_path, f), self._env_name, parse_symmetry=False))

    def _open_scalar_product_rules(self):
        self._scalar_product_rules = \
            jrules_parser.parse_scalar_products_reducing_rules(self._get_file_path(self._env_name),
                                                               self._env_name)

    def is_applicable(self, graph):
        if graph.getLoopsCount() != self._main_loop_count_condition:
            return False
        for e in graph.allEdges():
            if e.weight.b != 0:
                return False
        return True

    def calculate(self, graph, scalar_product_aware_function=None):
        """
        scalar_product_aware_function(topology_shrunk, graph) returns iterable of scalar_product.ScalarProduct
        """
        self.initIfNeed()
        Reductor.CALLS_COUNT += 1
        if graph.getLoopsCount() != self._main_loop_count_condition:
            return None

        probably_calculable_sectors = set()
        str_graph = str(graph)
        str_graph = str_graph[:str_graph.index(":")]
        as_topologies = _enumerate_graph(graphine.Graph.fromStr(str_graph),
                                         self._propagators,
                                         to_sector=False)
        for t in as_topologies:
            res = reduction_util.find_topology_for_graph(graph,
                                                         (t,),
                                                         scalar_product.find_topology_result_converter)
            probably_calculable_sectors.add(res)

        for res in probably_calculable_sectors:
            try:
                s = sector.Sector.create_from_shrunk_topology(res[0], res[1], self._all_propagators_count).as_sector_linear_combinations()
                if scalar_product_aware_function:
                    for sp in scalar_product_aware_function(*res):
                        s = sp.apply(s, self._scalar_product_rules)
                return self.evaluate_sector(s)
            except RuleNotFoundException:
                pass
        return None
        
    def _try_calculate(self, graph):
        return self.evaluate_sector(sector.Sector.create_from_topologies_and_graph(graph,
                                                                                   self._topologies,
                                                                                   self._all_propagators_count))

    def evaluate_sector(self, a_sectors):
        self.initIfNeed()
        if a_sectors is None:
            return None
        import time
        ms = time.time()
        dfs_cache = dict()
        _all = rggraphutil.Ref.create(0)
        hits = rggraphutil.Ref.create(0)


        def dfs(_sector, sector_rules, _all, hits):
            cached = dfs_cache.get(_sector, None)
            _all.set(_all.get() + 1)
            if cached is not None:
                hits.set(hits.get() + 1)
                return cached
            if _sector in self._zero_sectors:
                res = 0
            elif _sector in self._masters:
                res = _sector.as_sector_linear_combinations()
            else:
                is_updated = False
                for rule in sector_rules:
                    if rule.is_applicable(_sector):
                        res = rule.apply(_sector)
                        not_masters = dict()
                        raw_sectors = res.sectors_to_coefficient.keys()
                        for s in raw_sectors:
                            if s.as_rule_key() in self._zero_sectors:
                                res = res.remove_sector(s)
                            elif s not in self._masters.keys():
                                not_masters[s] = res.sectors_to_coefficient[s]
                                res = res.remove_sector(s)

                        if not len(not_masters):
                            is_updated = True
                            break

                        key_to_sector = rggraphutil.emptyListDict()
                        for s in not_masters.keys():
                            key_to_sector[s.as_rule_key()].append(s)
                        sorted_keys = sorted(key_to_sector.keys())
                        for k in sorted_keys:
                            cur_rules = self._sector_rules[k]
                            cur_sectors = key_to_sector[k]
                            for _s in cur_sectors:
                                res += dfs(_s, cur_rules, _all, hits) * not_masters[_s]
                        is_updated = True
                        break
                if not is_updated:
                    raise RuleNotFoundException(_sector)
            dfs_cache[_sector] = res
            return res

        a_sectors = a_sectors.as_sector_linear_combinations()
        raw_sectors = a_sectors.sectors_to_coefficient.keys()
        not_masters = dict()
        for s in raw_sectors:
            if s.as_rule_key() in self._zero_sectors:
                a_sectors = a_sectors.remove_sector(s)
            elif s not in self._masters.keys():
                not_masters[s] = a_sectors.sectors_to_coefficient[s]
                a_sectors = a_sectors.remove_sector(s)

        key_to_sector = rggraphutil.emptyListDict()
        for s in not_masters.keys():
            key_to_sector[s.as_rule_key()].append(s)
        sorted_keys = sorted(key_to_sector.keys())
        for k in sorted_keys:
            cur_rules = self._sector_rules[k]
            cur_sectors = key_to_sector[k]
            for _s in cur_sectors:
                a_sectors += dfs(_s, cur_rules, _all, hits) * not_masters[_s]
        if DEBUG:
            print "time", (time.time()-ms), " cache hits", hits.get(), " all cache points", _all.get()
        return ReductorResult(a_sectors, self._masters)

    def _get_file_path(self, file_name):
        dir_path = self._get_dir_path()
        file_path = os.path.join(dir_path, file_name)
        return file_path

    def _get_dir_path(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), self._env_path)

    def _get_topologies_file_path(self):
        return self._get_file_path(Reductor.TOPOLOGIES_FILE_NAME)

    def _get_masters_file_path(self):
        return self._get_file_path(Reductor.MASTERS_FILE_NAME)

    def _try_read_topologies(self):
        file_path = self._get_topologies_file_path()
        if os.path.exists(file_path):
            topologies = set()
            with open(file_path, 'r') as f:
                for s in f:
                    topologies.add(graphine.Graph.fromStr(s))
                return topologies
        return None

    def _save_topologies(self):
        file_path = self._get_topologies_file_path()
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                for t in self._topologies:
                    f.write(str(t) + "\n")
        else:
            raise ValueError("file %s already exists" % file_path)

    def _try_read_masters(self):
        file_path = self._get_masters_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                masters = dict()
                masters_graphs = dict()
                for s in f:
                    raw_master_graph, raw_sector, raw_value = s.split(";")
                    _sector = sector.Sector(eval(raw_sector))
                    masters[_sector] = symbolic_functions.evaluate(raw_value)
                    masters_graphs[_sector] = raw_master_graph
                return masters, masters_graphs
        return None

    def _save_masters(self):
        file_path = self._get_masters_file_path()
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                for s, v in self._masters.iteritems():
                    f.write(
                        self._masters_graph[s] +
                        ";" +
                        str(s.propagators_weights) +
                        ";" +
                        symbolic_functions.safe_integer_numerators_strong(str(v)) + "\n")
        else:
            raise ValueError("file %s already exists" % file_path)

    @staticmethod
    def as_internal_graph(graph):
        new_edges = list()
        if graph.getGraphStatePropertiesConfig() is graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG:
            return graph
        for e in graph.allEdges(nickel_ordering=True):
            weight = graph_state.Rainbow((1, 0)) if e.weight is None else e.weight
            arrow = graph_state.Arrow(graph_state.Arrow.NULL) if e.arrow is None else e.arrow
            new_edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge(e.nodes, weight=weight, arrow=arrow, marker=e.marker))
        return graphine.Graph(new_edges)


_MAIN_REDUCTION_HOLDER = ref.Ref.create()
_IS_INITIALIZED = ref.Ref.create(False)


def initialize(*reductors):
    _IS_INITIALIZED.set(True)
    _MAIN_REDUCTION_HOLDER.set(ReductorHolder(reductors))


def calculate(graph, scalar_product_aware_function=None):
    return _MAIN_REDUCTION_HOLDER.get().calculate(graph, scalar_product_aware_function)


def is_applicable(graph):
    return _MAIN_REDUCTION_HOLDER.get().is_applicable(graph)
