#!/usr/bin/python
# -*- coding:utf8
"""Module for generating of topologies of feynman graphs.
"""
__author__ = "Sergey Novikov"

import collections
import itertools
import nickel
import graphine
import graph_state

# The node denoting a leg of a graph.
LEG = -1


def get_topologies(valencies_to_num_nodes, external_nodes_count, with_tadpoles=True, is_one_particle_irreducible=False):
    """
    Yields nickel strings of one particle irreducible graphs.

    :param valencies_to_num_nodes: dict mapping valencies to num of nodes.
    :param external_nodes_count: count of external legs
    :param with_tadpoles: whether to generate graphs with tadpoles.
    :param is_one_particle_irreducible: `True` if output graph must be 1-particle irreducible or `False` if graph must be connected
    """
    valencies_to_num_nodes = dict(valencies_to_num_nodes)
    assert 1 not in valencies_to_num_nodes, "Nodes MUST have >= 2 edges"
    valencies_to_num_nodes[1] = external_nodes_count
    return GetTopologies(valencies_to_num_nodes, with_tadpoles=with_tadpoles, is_irreducible=is_one_particle_irreducible)


def GetTopologies(valences_to_num_nodes, with_tadpoles=True, is_irreducible=False):
    topologies = set()
    initial_state = NickelPool(nickel=[], pool=valences_to_num_nodes)
    for nickpool in AddAllNodesFromPool(initial_state, is_irreducible=is_irreducible):
        topology = CanonicalString(nickpool.nickel)
        if topology in topologies:
            continue
        topologies.add(topology)

        if not with_tadpoles:
            if HasTadpole(nickel.Nickel(nickel=nickpool.nickel).edges):
                continue

        yield graphine.Graph(graph_state.GraphState.from_str(topology))


NickelPool = collections.namedtuple('NickelPool', 'nickel pool')


def AddAllNodesFromPool(nickpool, is_irreducible):
    '''Yields NickelPool objects all nodes from pool added to nickel.'''
    nodes_left = CountNodesInPool(nickpool.pool)
    if nodes_left > 1:
        for deeper in AddNodeFromPool(nickpool, is_irreducible):
            for recursive in AddAllNodesFromPool(deeper, is_irreducible):
                yield recursive
    elif nodes_left == 1:
        for deepest in AddNodeFromPool(nickpool, is_irreducible):
            if deepest.pool.get(1, 0) == 0:
                yield deepest
    else:
        yield nickpool


def AddNodeFromPool(nickpool, is_irreducible):
    if IsOneParticleReducibleOrConnectivity(nickpool.nickel, is_irreducible):
        return
    canonicals = set()

    node = len(nickpool.nickel)
    taken_valence = CountNode(nickpool.nickel, node)
    free_node = MaxNode(nickpool.nickel) + 1
    end_node = CountInternalNodes(nickpool)
    max_legs = nickpool.pool.get(1, 0)
    for valence in nickpool.pool:
        if nickpool.pool[valence] <= 0:
            continue
        if valence == 1:
            continue
        if valence < taken_valence:
            continue
        for add_nickel in AddEdges(valence - taken_valence,
                                   node, free_node, end_node, max_legs):
            # Filter by number of legs.
            if max_legs:
                num_legs = add_nickel.count(LEG)
                if num_legs > max_legs:
                    continue
                if node == 0 and num_legs == 0:
                    continue

            new_nickel = list(nickpool.nickel) + [list(add_nickel)]
            # Update pool.
            new_pool = dict(nickpool.pool)
            new_pool[valence] -= 1
            if max_legs:
                new_pool[1] -= num_legs

            if not NickelFitsPool(new_nickel, new_pool):
                continue

            canonical = CanonicalString(new_nickel)
            if canonical in canonicals:
                continue
            canonicals.add(canonical)

            yield NickelPool(nickel=new_nickel, pool=new_pool)


def IsOneParticleReducibleOrConnectivity(nickel_list, check_reducibility):
    if not nickel_list:
        return False
    free_node = len(nickel_list)
    edges_to_pool = CountNode(nickel_list, free_node)
    # Disconnected.
    if edges_to_pool == 0:
        return True
    # Single edge goes to pool.
    if check_reducibility:
        if edges_to_pool == 1:
            if CountNode(nickel_list, free_node + 1) == 0:
                return True
    # Merge all pool nodes into one and check reducibility.
    merge = lambda node: min(node, free_node)
    merged_nickel = [map(merge, nodes) for nodes in nickel_list]
    edges = nickel.Nickel(nickel=merged_nickel).edges
    if IsNCutDisconnectable(edges, 1 if check_reducibility else 0):
        return True

    return False


def CountNode(nickel_list, node):
    return sum([nodes.count(node) for nodes in nickel_list])


def IsNCutDisconnectable(edges, num_to_cut):
    '''Returns true if cutting of num_to_cut edges disconnects the graph.'''
    # Brute force solution.
    for edges_part in itertools.combinations(edges, len(edges) - num_to_cut):
        if not IsConnected(edges_part):
            return True
    return False


def GetNodesConnectedToNode(edges, node):
    '''Returns connected component which contains given node.
     If the connected component contains LEG node, this indicates that component has
     at least one external leg.
    '''
    old_len = 0
    visited_nodes = set([node])
    while old_len < len(visited_nodes):
        old_len = len(visited_nodes)
        for edge in edges:
            for node in edge:
                if node != LEG:
                    if node in visited_nodes:
                        visited_nodes.update(edge)
                        break
    return visited_nodes


def GetConnectedComponents(edges):
    '''Yields connected components, each component is set of nodes.
    If connected component has LEG node, this indicates that component has
    at least one external leg.
    '''
    all_nodes = set(nickel.flatten(edges))
    all_nodes.discard(LEG)
    while len(all_nodes) > 0:
        connected_to_node = GetNodesConnectedToNode(edges, all_nodes.pop())
        yield connected_to_node
        all_nodes = all_nodes - connected_to_node


def IsConnected(edges):
    '''Returns true for connected graph. Legs are treated as amputated.'''
    if not edges:
        return False

    node = edges[0][0] if edges[0][0] != LEG else edges[0][1]
    connected_to_node = GetNodesConnectedToNode(edges, node)
    all_nodes = set(nickel.flatten(edges))
    return connected_to_node == all_nodes


def RemoveNode(edges, node_to_remove):
    '''Given node is removed from graph, lines connected to this node will
     be connected to separate nodes, e.g. if node 4 removed, then lines are
     connected to nodes (with valence=1) 4A, 4B, 4C etc.

     Here assumed that edges has only integer nodes and there is no nodes like '4A'
    '''
    new_edges = []
    node_label = ord('A')
    for edge in edges:
        new_edge = []
        for node in edge:
            if node == node_to_remove:
                new_edge.append('%s%s' % (node_to_remove, chr(node_label)))
                node_label += 1
            else:
                new_edge.append(node)
        new_edges.append(new_edge)
    return new_edges


def HasTadpole(edges):
    '''Returns True if graph has tadpole.
    Graph has tadpole if removing of a node produces connected
    component without external legs.
    '''
    all_nodes = set(nickel.flatten(edges))
    all_nodes.discard(LEG)

    for node in all_nodes:
        for component in GetConnectedComponents(RemoveNode(edges, node)):
            if LEG not in component:
                return True
    return False


def MaxNode(nickel_list):
    in_nickel = len(nickel_list) - 1
    from_pool = max(nickel.flatten(nickel_list) + [-1])
    return max(in_nickel, from_pool)


def CountInternalNodes(nickpool):
     return len(nickpool.nickel) + CountNodesInPool(nickpool.pool)


def CountNodesInPool(pool):
    return sum(pool.values()) - pool.get(1, 0)


def CountAllNodesInPool(pool):
    return sum(pool.values())


def CanonicalString(nickel_list):
    edges = nickel.Nickel(nickel=nickel_list).edges
    return str(nickel.Canonicalize(edges=edges))


def AddEdges(num_edges, start_node, free_node, end_node, add_legs):
    '''Yields all sorted combinations of legs and available nodes.

    Args:
        num_edges: number of edges to add
        start_node: first internal node to connect edges to. The edges connected to
             it are considered self-connected.
        free_node: the first node in pool which is not referenced in nickel.
        end_node: limit of the number of nodes.
        add_legs: whether to add legs.
    '''
    # assert free_node > start_node
    free_node = free_node if free_node > start_node else start_node + 1
    leg = [LEG] if add_legs else []
    reachable_end =  min(free_node + num_edges, end_node)
    reachable_nodes = leg + range(start_node, reachable_end)
    for nodes in itertools.combinations_with_replacement(reachable_nodes, num_edges):
        pool_nodes = [node for node in nodes if node >= free_node]
        if pool_nodes and not AreMinimalNodesFromPool(free_node, pool_nodes):
            continue

        # Avoid double accounting of self connected nodes.
        self_count = nodes.count(start_node)
        if self_count != 0:
            if self_count % 2 == 1:
                continue
            self_index = nodes.index(start_node)
            nodes = (nodes[:self_index + self_count/2] +
                     nodes[self_index + self_count:])

        yield nodes


def NickelFitsPool(nickel_list, node_pool):
    free_node = len(nickel_list)
    pool_nodes = [node for node in nickel.flatten(nickel_list) if node >= free_node]
    pool_nodes.sort()
    wanted_pool = {}
    for _, group_iter in itertools.groupby(pool_nodes):
        group_len = len(tuple(group_iter))
        wanted_pool[group_len] = wanted_pool.get(group_len, 0) + 1
    if MaxValenceInPool(wanted_pool) > MaxValenceInPool(node_pool):
        return False
    if CountAllNodesInPool(wanted_pool) > CountNodesInPool(node_pool):
        return False

    return True


def MaxValenceInPool(pool):
    valences = [valence for valence in pool if valence != 1 and pool[valence] > 0]
    if not valences:
        return 0
    return max(valences)


def AreMinimalNodesFromPool(free_node, pool_nodes):
    '''Optimization to find early non-minimal nickel list.'''
    if not pool_nodes:
        return True
    unique_nodes = []
    group_lengths = []
    for node, group_iter in itertools.groupby(pool_nodes):
        unique_nodes.append(node)
        group_lengths.append(len(tuple(group_iter)))
    # Detect gap.
    if unique_nodes[0] > free_node:
        return False
    if unique_nodes[-1] - unique_nodes[0] + 1 != len(unique_nodes):
        return False
    # Lengths of groups should be non-increasing.
    if group_lengths != sorted(group_lengths, reverse=True):
        return False

    return True


if __name__ == '__main__':
    pass
