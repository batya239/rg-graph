__author__ = 'gleb'

import datetime
import sys
import itertools
import os

import graphine
import graph_state


def tau_differentiate(g, no_tails=False):
    seen = set()
    unreduced = tuple()
    if isinstance(g, graphine.Graph):
        new_vertex = max(g.vertices()) + 1
        for edge in g.internalEdges():
            g1 = g.deleteEdge(edge)
            ins = ([new_vertex, edge.nodes[0]], [new_vertex, edge.nodes[1]])
            if not no_tails:
                ins += ([new_vertex, g.external_vertex], )
            new_edges = map(lambda x: graph_state.Edge(x), ins)
            unreduced += tuple([g1.addEdges(new_edges)])
        return tuple((x, unreduced.count(x)) for x in unreduced if str(x) not in seen and not seen.add(str(x)))

    elif isinstance(g, tuple):
        for x in g:
            unreduced += tuple(map(lambda y: (y[0], y[1] * x[1]), tau_differentiate(x[0], no_tails)))

        result = tuple()
        for i, x in enumerate(unreduced):
            if str(x[0]) not in seen:
                seen.add(str(x[0]))
                new_num = 0
                for y in unreduced[i:]:
                    if str(y[0]) == str(x[0]):
                        new_num += y[1]
                result += tuple([(x[0], new_num), ])
        return result


def get_diagrams(tails=0, loops=0):
    if 1 == loops:
        result = (graphine.Graph.fromStr('e0|'), 1.0 / 2.0),
        for _ in itertools.repeat(None, tails - 1):
            result = tau_differentiate(result)
        return result

    v_loops = {2: (('111||', 1.0 / 12.0), ),
               3: (('112|3|33||', 1.0 / 16.0), ('123|23|3||', 1.0 / 24.0)),
               4: (('112|3|34|5|55||', 1.0 / 16.0), ('112|3|44|55|5||', 1.0 / 48.0), ('112|3|45|45|5||', 1.0 / 8.0),
                   ('123|24|5|45|5||', 1.0 / 12.0), ('123|45|45|45|||', 1.0 / 72.0)),
               5: (('112|3|34|5|56|7|77||', 1.0 / 16.0), ('112|3|34|5|66|77|7||', 1.0 / 16.0),
                   ('112|3|34|5|67|67|7||', 1.0 / 8.0), ('112|3|44|55|6|7|77||', 1.0 / 128.0),
                   ('112|3|44|56|7|67|7||', 1.0 / 16.0), ('112|3|45|45|6|7|77||', 1.0 / 32.0),
                   ('112|3|45|46|5|7|77||', 1.0 / 8.0), ('112|3|45|46|7|67|7||', 1.0 / 4.0),
                   ('112|3|45|67|56|7|7||', 1.0 / 8.0), ('112|3|45|67|66|77|||', 1.0 / 96.0),
                   ('112|3|45|67|67|67|||', 1.0 / 16.0), ('123|23|4|5|67|67|7||', 1.0 / 16.0),
                   ('123|24|5|46|7|67|7||', 1.0 / 4.0), ('123|24|5|67|67|67|||', 1.0 / 12.0),
                   ('123|45|46|56|7|7|7||', 1.0 / 48.0), ('123|45|46|57|7|6|7||', 1.0 / 16.0))}

    result = tuple(map(lambda x: (graphine.Graph.fromStr(x[0]), x[1]), v_loops[loops]))
    for _ in itertools.repeat(None, tails):
        result = tau_differentiate(result)

    return result


def dispatch_log_message(msg, ts=True):
    """
    """
    assert(isinstance(msg, str))

    if ts:
        time = datetime.datetime.now()
        timestamp = '### ' + ':'.join(map(lambda x: str(x), [time.hour, time.minute, time.second])) + ' '
    else:
        timestamp = ''

    f = open(sys.argv[0] + '.log', 'a')
    f.write(timestamp + msg + '\n')
    f.close()


def clear_log():
    fname = sys.argv[0] + '.log'
    if os.path.isfile(fname):
        os.remove(sys.argv[0] + '.log')
