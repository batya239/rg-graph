#!/usr/bin/python
# -*- coding: utf8
#
#
#    DEPRECATED SHIT
#
#
import copy
import itertools
import os
import shutil
import subprocess
import rggraphutil
from rggraphenv import symbolic_functions

__author__ = 'mkompan'

import sys
import graphine
import graph_state
import re


_MINCER_DEFAULT_TMP_DIR = "/tmp/__mincer1111_O_D_bl_N__"
_MINCER_DIR = rggraphutil.Ref.create(_MINCER_DEFAULT_TMP_DIR)
_MINCER2_H = "mincer2.h"
_FORM_VERSION = rggraphutil.Ref.create("tform")

_RESULT_REGEXP = re.compile("F\s=(.*);")


def init_mincer(mincer_dir=_MINCER_DEFAULT_TMP_DIR, use_multi_threading=True):
    _FORM_VERSION.set("tform" if use_multi_threading else "form")
    exception = None
    for i in xrange(2):
        try:
            _MINCER_DIR.set(mincer_dir)
            os.makedirs(_MINCER_DIR.get())
            shutil.copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib", _MINCER2_H),
                            os.path.join(_MINCER_DIR.get(), _MINCER2_H))
            return
        except OSError as e:
            dispose_mincer()
            exception = e
    raise exception


def dispose_mincer():
    shutil.rmtree(_MINCER_DIR.get())


# noinspection PyUnboundLocalVariable
def is_applicable(graph):
    if graph.getLoopsCount() > 3:
        return False
    edges = graph.allEdges()
    if not len(edges):
        return False
    for e in edges:
        c = e.colors
        if c is None or len(c) != 2:
            return False
        if c[1] != 0 or c[0] != int(c[0]):
            return False
    return True


#noinspection PyUnresolvedReferences
def calculate_graph(graph):
    t = write_form_file(graph, _MINCER_DIR.get())
    if t is None:
        return None
    file_name = t[2]

    proc = subprocess.Popen("cd " + _MINCER_DIR.get() + ";" + _FORM_VERSION.get() + " " + file_name, shell=True,
                            stdout=subprocess.PIPE)
    proc.wait()
    std_out = proc.stdout.read().replace("\n", "")

    raw_result = _RESULT_REGEXP.findall(std_out)[0]
    raw_result = raw_result.replace("Q.Q", "1").replace("^", "**").replace("ep", "e")
    raw_result = _replace_zetas(raw_result)
    raw_result = symbolic_functions.safe_integer_numerators(raw_result)
    if raw_result.strip() == '0':
        return None
    # noinspection PyUnusedLocal
    e = symbolic_functions.e
    # noinspection PyUnusedLocal
    p = symbolic_functions.p
    import swiginac
    #noinspection PyUnusedLocal
    zeta = swiginac.zeta
    res = eval(raw_result)
    print "MINCER", graph, res
    return res, _calculate_p_factor(graph)


def _replace_zetas(raw_result):
    return re.sub('z(\d+)', 'zeta(\\1)', raw_result)


def _calculate_p_factor(graph):
    factor0 = 0
    for e in graph.internalEdges():
        factor0 += e.colors[0]
    return factor0 - graph.getLoopsCount(), - graph.getLoopsCount()

# no signs for momenta at this moment
TOPOLOGIES = {
    'e12-23-3-e-': ('t1', ['Q', 'p1', 'p4', 'p5', 'p2', 'p3', 'Q']),
    'e12-e3-33--': ('t2', ['Q', 'p1', 'p2', 'Q', 'p1', 'p3', 'p4']),
    'e11-22-e-': ('t3', ['Q', 'p1', 'p2', 'p3', 'p4', 'Q']),
    'e12-e3-45-45-5--': ('o4', ['Q', 'p6', 'p7', 'Q', 'p6', 'p1', 'p4', 'p2', 'p3', 'p5']),
    'e12-23-4-45-5-e-': ('la', ['Q', 'p1', 'p6', 'p7', 'p2', 'p5', 'p8', 'p3', 'p4', 'Q']),
    'e12-34-35-4-5-e-': ('be', ['Q', 'p1', 'p5', 'p6', 'p2', 'p8', 'p4', 'p7', 'p3', 'Q']),
    'e12-34-34-e4--': ('bu', ['Q', 'p6', 'p7', 'p1', 'p4', 'p3', 'p5', 'Q', 'p2']),
    'e12-23-34-4-e-': ('fa', ['Q', 'p1', 'p5', 'p6', 'p2', 'p7', 'p4', 'p3', 'Q']),
    'e12-34-34-5-5-e-': ('no', ['Q', 'p1', 'p6', 'p2', 'p7', 'p8', 'p5', 'p3', 'p4', 'Q']),
}


def _set_momenta(graph_name, momenta_list):
    graph = graphine.Graph.fromStr(graph_name)
    edges_list = list()
    i = 0
    for edge in graph.allEdges(nickel_ordering=True):
        edge_ = copy.copy(edge)
        edge_.colors = graph_state.Rainbow((momenta_list[i],))
        i += 1
        edges_list.append(edge_)
    return graphine.Graph(graph_state.GraphState(edges_list))

INITED_GRAPHS = dict()
for topology in TOPOLOGIES:
    INITED_GRAPHS[topology] = _set_momenta(topology, TOPOLOGIES[topology][1])


def _find_topology(target_graph):
    target_graph_name = target_graph.getPresentableStr()
    for topology in TOPOLOGIES:
        model_graph = INITED_GRAPHS[topology]
        internal_edges = model_graph.internalEdges()
        n = len(internal_edges) - len(target_graph.internalEdges())
        if n < 0:
            continue
        elif n == 0:
            if topology == target_graph_name:
                return TOPOLOGIES[topology][0], model_graph

        for lines in itertools.combinations(internal_edges, n):
            shrunk = model_graph.batchShrinkToPoint([[x] for x in lines])
            gs_as_str = shrunk.getPresentableStr()
            if target_graph_name == gs_as_str:
                return TOPOLOGIES[topology][0], shrunk
    return None


_FORM_TEMPLATE = """
#-
#include mincer2.h
.global
Local F = 1{denom};
Multiply ep^3;
#call integral({topology})
Print +f;
.end
"""


def generate_form_file(topology_type, graph_with_momenta, graph_with_weights):
    denom = ""
    graph_with_momenta_and_weights = graphine.util.merge(graph_with_momenta, graph_with_weights)
    for line in graph_with_momenta_and_weights.internalEdges():
        denom += ''.join(["/%s.%s" % (line.colors[0], line.colors[0])] * line.colors[1])
    return _FORM_TEMPLATE.format(denom=denom, topology=topology_type)


def write_form_file(graph, directory="form_files"):
    ans = _find_topology(graph)
    if ans is not None:
        topology_type, graph_with_momenta = ans
        file_name = '%s.frm' % graph.getPresentableStr()
        f = open(os.path.join(directory, file_name), 'w+')
        f.write(generate_form_file(topology_type, graph_with_momenta, graph))
        f.close()
        return topology_type, graph_with_momenta, file_name
    else:
        return None


def can_calculate_graph_with_mincer(graph):
    for e in graph.allEdges(withIndex=False):
        colors = e.colors
        if colors is not None and colors[0] != 0:
            return False
    return True


def main():
    try:
        init_mincer()
        print calculate_graph(graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr(sys.argv[1]))))
    finally:
        dispose_mincer()


if __name__ == "__main__":
    main()