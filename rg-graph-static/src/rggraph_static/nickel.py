#!/usr/bin/python
# -*- coding:utf8

from comb import xCombinations, xPermutations

class Nickel(object):
    """Class to generate Nickel-like graph notations.

    Usage:
    >>> n = nickel.Nickel(edges=[[-1, 0], [0, 1], [1, -1]])
    >>> n.nickel
    [[-1, 1], [-1]]
    >>> n.string
    'e1-e-'
    """
    node_to_char = {-2: '-', -1: 'e', 10: 'A', 11: 'B', 12: 'C', 13: 'D',
                    14: 'E', 15: 'F'}
    def __init__(self, edges=None, nickel=None, string=None):
        self.edges = edges
        self.nickel = nickel
        self.string = string

        if self.edges:
            for e in self.edges:
                e.sort()
            self.edges.sort()

        if self.nickel:
            for nn in self.nickel:
                nn.sort()

        if edges != None:
            self.edges = edges
            self.nickel = self.NickelFromEdges(edges)
            self.string = self.StringFromNickel(self.nickel)
        elif nickel != None:
            self.edges = self.EdgesFromNickel(nickel)
            self.nickel = nickel
            self.string = self.StringFromNickel(nickel)
        elif string != None:
            self.string = string
            self.nickel = self.NickelFromString(string)
            self.edges = self.EdgesFromNickel(self.nickel)

    def NickelFromEdges(self, edges):
        max_node = max(sum(edges, []))
        nickel = [[] for i in range(max(1, max_node))]
        for e in edges:
            [s, d] = sorted(e, key=lambda n: n if n >= 0 else 1000)
            nickel[s].append(d)
        for nn in nickel:
            nn.sort()
        return nickel

    def EdgesFromNickel(self, nickel):
        edges = []
        for n in range(len(nickel)):
            for m in nickel[n]:
                edges.append(sorted([n, m]))
        edges.sort()
        return edges

    def StringFromNickel(self, nickel):
        temp = [nn + [-2] for nn in nickel]
        temp = sum(temp, [])
        temp = [str(Nickel.node_to_char.get(n, n)) for n in temp]
        return ''.join(temp)

    def NickelFromString(self, string):
        char_to_node = dict(zip(Nickel.node_to_char.values(),
                                Nickel.node_to_char.keys()))
        flat_nickel = [int(char_to_node.get(c, c)) for c in string]
        nickel = []
        accum = []
        for n in flat_nickel:
            if n != -2:
                accum.append(n)
            else:
                nickel.append(accum)
                accum = []
        return nickel


class InputError(Exception):
    """Rased when when Canonicalization is called with wrong input.
    """
    pass


class Canonicalize(object):
    """Class to find canonical node maping and to give Nickel node list for it.

    Negative nodes assumed to be external. Non-negative ones - internal.
    Usage:
        c = nickel.Canonicalize([[-1, 10], [-1, 11], [10, 11]])
        assertEqual(c.nickel, [[-1, 1], [-1]])
        assertEqual(c.num_symmetries, 2)
        assertEqual(c.node_maps, [{10: 0, 11: 1}, {10: 1, 11: 0}])
        assertTrue(c.is_valid)
    """
    def __init__(self, edges):
        if not [n for n in sum(edges, []) if n < 0]:
            raise InputError('No external (negative) nodes found in the input.')
        if not IsConnected(edges):
            raise InputError('Input edge list is an unconnected graph.')

        self.orig = edges

        self.num_internal_nodes = 0
        for n in set(sum(edges, [])):
            if n >= 0:
                self.num_internal_nodes += 1

        # Shift original nodes to free space for canonical numbers.
        self.offset = max(100, self.num_internal_nodes)
        def shift(n):
            return n + self.offset if n >= 0 else -1
        self.edges = [[shift(n), shift(m)] for [n, m] in edges]

        # Do the work.
        self.curr_states = self.InitStates(self.edges)
        for _ in range(self.num_internal_nodes):
            self.curr_states = self.DoExpand(self.curr_states)

        # Collect results.
        nickels = [s.nickel_list for s in self.curr_states]
        self.num_symmetries = len(nickels)
        self.nickel = min(nickels)
        is_valid = self.nickel == max(nickels)
        self.is_valid = is_valid and (len(sum(self.nickel, [])) ==
                                      len(self.edges))

        # Shift back to original nodes.
        self.node_maps = []
        for state in self.curr_states:
            node_map = {}
            for key, value in state.node_map.items():
                node_map[key - self.offset] = value
            self.node_maps.append(node_map)

    def __str__(self):
        return Nickel(nickel=self.nickel).string

    def InitStates(self, edges):
        """Creates all possible initial states for node 0."""
        boundary_nodes = list(set(AdjacentNodes(-1, edges)))
        states = []
        for bound in boundary_nodes:
            states.append(Expander(MapNodes2({bound: 0}, self.edges),
                                                         [], {bound: 0}, 0, 1))
        return states

    def DoExpand(self, curr_states):
        states = [list(s.Expand()) for s in curr_states]
        states = sum(states, [])
        minimum = min(states)
        return [s for s in states if s == minimum]

    def GetGroupedEdges(self):
        permuts = PermutatedFromCanonical(self.node_maps)
        equal_graphs = [MapNodes2(permut, self.orig) for permut in permuts]
        equal_edges = zip(*equal_graphs)
        equal_edges = map(list, equal_edges)
        equal_edges = map(lambda x: sorted(x), equal_edges)
        Dedup(equal_edges)
        groups = [[] for _ in range(len(equal_edges))]
        for e in self.orig:
            for i in range(len(equal_edges)):
                if sorted(e) in equal_edges[i]:
                    groups[i].append(e)
        return groups


def PermutatedFromCanonical(list_of_dicts):
    dic = list_of_dicts[0]
    back_dic = dict(zip(dic.values(), dic.keys()))
    permutations = []
    for d in list_of_dicts:
      permutation = dict(zip(d.keys(), [back_dic[v] for v in d.values()]))
      permutations.append(permutation)
    return permutations


def Dedup(mylist):
    mylist.sort()
    last = mylist[-1]
    for i in range(len(mylist) - 2, -1, -1):
        if last == mylist[i]:
            del mylist[i]
        else:
            last = mylist[i]


class Expander(object):
    """A helper class for Canonicalize.

    Eats edges adjacent to already canonicalized nodes and canonicalizes them.
    """
    def __init__(self, edges, nickel_list, node_map, curr_node, free_node):
        self.edges = edges
        self.nickel_list = nickel_list    # Nested lists must be sorted.
        self.node_map = node_map
        self.curr_node = curr_node
        self.free_node = free_node

    def __cmp__(self, other):
        # Shorten the long list to not let unexpanded one win.
        min_len = min(len(self.nickel_list), len(other.nickel_list))
        return cmp(self.nickel_list[:min_len], other.nickel_list[:min_len])

    def Expand(self):
        nodes = AdjacentNodes(self.curr_node, self.edges)
        edge_rest = [e for e in self.edges if self.curr_node not in e]
        new_nodes = [n for n in nodes if n > self.free_node]
        new_nodes = list(set(new_nodes))
        free_nodes = range(self.free_node, self.free_node + len(new_nodes))
        for perm in xPermutations(free_nodes):
            node_map = dict(zip(new_nodes, perm))
            expanded_nodes = MapNodes1(node_map, nodes)
            edges = MapNodes2(node_map, edge_rest)
            node_map.update(self.node_map)
            yield Expander(edges, self.nickel_list + [expanded_nodes],
                           node_map, self.curr_node + 1,
                           self.free_node + len(new_nodes))


def AdjacentNodes(node, edges):
    nodes = []
    for e in edges:
        if e[0] == node:
            nodes.append(e[1])
        elif e[1] == node:
            nodes.append(e[0])
    return nodes


def IsConnected(edges):
    if not edges:
        return False
    else:
        old_len = 0
        visited = set(edges[0])
        while old_len < len(visited):
            old_len = len(visited)
            for [s, d] in edges:
                if s in visited or d in visited:
                    visited.update([s, d])
        return visited == set(sum(edges, []))


def MapNodes1(dic, list_of_nodes):
    return sorted([dic.get(n, n) for n in list_of_nodes])


def MapNodes2(dic, list_of_lists):
    return [MapNodes1(dic, x) for x in list_of_lists]


if __name__ == "__main__":
    pass
