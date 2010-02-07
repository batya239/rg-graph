#!/usr/bin/python

class Nickel(object):
  """Class to generate graph notations by Nickel.
  """
  def __init__(self, edges):
    self.edges = edges
    self.node_to_char = {-2: '-', -1: 'e'}

  def GetList(self):
    """Generates list signature of the diagram"""
    max_node = max(sum(self.edges, []))
    nodes = [[] for i in range(max(1, max_node))]
    for e in self.edges:
      [s, d] = sorted(e, key=lambda n: n if n >= 0 else 1000)
      nodes[s].append(d)
    for nn in nodes:
      nn.sort()
    return nodes

  def GetString(self):
    nodes = self.GetList()
    for nn in nodes:
      nn.append(-2)
    nodes = sum(nodes, [])
    nodes = [str(self.node_to_char.get(n, n)) for n in nodes]
    return ''.join(nodes)

class Canonicalize(object):
  def __init__(self, edges):
    # TODO: Check that there is an external node.
    # TODO: Check that the graph is connected.
    # TODO: Raise exception?
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
    self.node_maps = [s.node_map for s in self.curr_states]
    nickels = [s.nickel_list for s in self.curr_states]
    self.num_symmetries = len(nickels)
    self.nickel = min(nickels)

    is_valid = self.nickel == max(nickels)
    self.is_valid = is_valid and (len(sum(self.nickel, [])) == len(self.edges))

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


class Expander(object):
  """A helper class for Canonicalize.

  Eats edges adjacent to already canonicalized nodes and canonicalizes them.
  """
  def __init__(self, edges, nickel_list, node_map, curr_node, free_node):
    self.edges = edges
    self.nickel_list = nickel_list  # Nested lists must be sorted.
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
    for perm in Permutations(free_nodes):
      node_map = dict(zip(new_nodes, perm))
      expanded_nodes = MapNodes1(node_map, nodes)
      expanded_nodes.sort()
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


def Combinations(seq, n):
  """Generator of all the n-element combinations of the given sequence.
  """
  if n == 0:
    yield seq[0:0]
  else:
    for i in range(len(seq)):
      for tail in Combinations(seq[:i] + seq[i+1:], n - 1):
        yield seq[i:i+1] + tail


def Permutations(seq):
  """Generator of all the permutations of the given sequence.
  """
  return Combinations(seq, len(seq))


def MapNodes1(dict, list_of_nodes):
  return [dict.get(n, n) for n in list_of_nodes]


def MapNodes2(dict, list_of_lists):
  return [MapNodes1(dict, x) for x in list_of_lists]


if __name__ == "__main__":
  pass
