#!/usr/bin/python

import topology
import unittest

class TestGetTopologies(unittest.TestCase):
    def testTopologies(self):
        topologies = set(topology.GetTopologies({3: 1}))
        self.assertEqual(set(), topologies)

        topologies = set(topology.GetTopologies({1: 2, 3: 2}))
        self.assertEqual(set(['e11-e-']), topologies)

        topologies = set(topology.GetTopologies({2: 3}))
        self.assertEqual(set(['12-2--']), topologies)

    def test_2_1_4_1(self):
        topologies = set(topology.GetTopologies({2: 1, 4: 1}))
        self.assertEqual(set(['011--']), topologies)

    def test_2_2_4_1(self):
        topologies = set(topology.GetTopologies({2: 2, 4: 1}))
        self.assertEqual(set(['012-2--', '11-22--']), topologies)


class TestGetTopologiesPhi3(unittest.TestCase):
    def test0legs2nodes(self):
        topologies = set(topology.GetTopologies({3: 2}))
        self.assertEqual(set(['111--']), topologies)

    def test0legs4nodes(self):
        topologies = set(topology.GetTopologies({3: 4}))
        self.assertEqual(set(['123-23-3--','112-3-33--']), topologies)

    def test0legs4nodes(self):
        topologies = set(topology.GetTopologies({3: 6}))
        self.assertEqual(set(['112-3-44-55-5--', '112-3-45-45-5--',
                              '112-3-34-5-55--', '123-24-5-45-5--',
                              '123-45-45-45---']),
                         topologies)


class TestGetTopologiesPhi4(unittest.TestCase):
    def test0legs1loop(self):
        topologies = set(topology.GetTopologies({4: 1}))
        self.assertEqual(set(['00-']), topologies)

    def test2legs2loops(self):
        topologies = set(topology.GetTopologies({1: 2, 4: 2}))
        self.assertEqual(set(['ee11-1-', 'e111-e-']), topologies)

    def test2legs3loops(self):
        topologies = set(topology.GetTopologies({1: 2, 4: 3}))
        self.assertEqual(set(['e112-22-e-', 'e112-e2-2-',
                              'ee12-222--', 'ee12-12-2-', 'ee11-22-2-']),
                         topologies)

        topologies = set(topology.GetTopologies({1: 2, 4: 3}, with_tadpoles=False))
        self.assertEqual(set(['e112-22-e-']), topologies)


class TestAddAllNodesFromPool(unittest.TestCase):
    def testAddAllNodesFromPool(self):
        inp = topology.NickelPool(nickel=[], pool={3: 2})
        out = list(topology.AddAllNodesFromPool(inp))
        self.assertEqual(
            [topology.NickelPool(nickel=[[1, 1, 1], []], pool={3: 0})],
            out)

        inp = topology.NickelPool(nickel=[], pool={2: 3})
        out = list(topology.AddAllNodesFromPool(inp))
        self.assertEqual(
            [topology.NickelPool(nickel=[[1, 2], [2], []], pool={2: 0})],
            out)

    def testAddAllNodesFromPoolWithEdges(self):
        inp = topology.NickelPool(nickel=[], pool={1: 2, 3: 2})
        out = list(topology.AddAllNodesFromPool(inp))
        self.assertEqual(
            [topology.NickelPool(nickel=[[-1, 1, 1], [-1]], pool={1: 0, 3: 0})],
            out)


class TestUtil(unittest.TestCase):
    def testCountNode(self):
        self.assertEqual(1, topology.CountNode([[1]], 1))
        self.assertEqual(0, topology.CountNode([[1]], 2))
        self.assertEqual(2, topology.CountNode([[1, 2, 2], [1]], 1))

    def testMaxNode(self):
        self.assertEqual(-1, topology.MaxNode([]))
        self.assertEqual(0, topology.MaxNode([[]]))
        self.assertEqual(2, topology.MaxNode([[2]]))

    def testCountInternalNodes(self):
        self.assertEqual(0, topology.CountInternalNodes(
            topology.NickelPool(nickel=[], pool={})))
        self.assertEqual(0, topology.CountInternalNodes(
            topology.NickelPool(nickel=[], pool={1: 1})))
        self.assertEqual(1, topology.CountInternalNodes(
            topology.NickelPool(nickel=[[0]], pool={})))
        self.assertEqual(1, topology.CountInternalNodes(
            topology.NickelPool(nickel=[], pool={3: 1})))

    def testAddEdges(self):
        self.assertEqual([()], list(topology.AddEdges(0, 1, 2, 2, 0)))
        # Impossible to add an edge.
        self.assertEqual([],
            list(topology.AddEdges(1, 1, 2, 2, 0)))
        self.assertEqual([(topology.LEG,)],
            list(topology.AddEdges(1, 1, 2, 2, 1)))
        self.assertEqual([(2,)],
            list(topology.AddEdges(1, 1, 2, 3, 0)))
        self.assertEqual([(topology.LEG,), (2,)],
            list(topology.AddEdges(1, 1, 2, 3, 1)))
        # Self connected.
        self.assertEqual([(8,)],
            list(topology.AddEdges(2, 8, 9, 9, 0)))
        self.assertEqual([(topology.LEG, topology.LEG), (8,)],
            list(topology.AddEdges(2, 8, 9, 9, 2)))

    def testAddEdgesValence3(self):
        self.assertEqual([(0, 1), (1, 1, 1)],
            list(topology.AddEdges(3, 0, 0, 2, 0)))

    def testAddEdges2EdgesBegin(self):
        self.assertEqual([(0,), (1, 1), (1, 2)],
            list(topology.AddEdges(2, 0, 0, 3, 0)))

    def testAddEdgesMinimalNodesFromPool(self):
        nick_inc = list(topology.AddEdges(3, 6, 7, 9, 0))
        self.assertTrue((7, 7, 8) in nick_inc)
        self.assertTrue((7, 8, 8) not in nick_inc)

    def testAreMinimalNodesFromPool(self):
        self.assertTrue(topology.AreMinimalNodesFromPool(3, []))
        self.assertFalse(topology.AreMinimalNodesFromPool(0, [1, 1]))
        self.assertFalse(topology.AreMinimalNodesFromPool(1, [1, 3]))
        self.assertTrue(topology.AreMinimalNodesFromPool(1, [1, 1, 2]))
        self.assertFalse(topology.AreMinimalNodesFromPool(1, [1, 2, 2]))

class TestAddNodeFromPool(unittest.TestCase):
    def testAddTwoNodesFromPool(self):
        inp = topology.NickelPool(nickel=[], pool={3: 2})
        out = []
        for one in topology.AddNodeFromPool(inp):
            for two in topology.AddNodeFromPool(one):
                out.append(two)
        self.assertEqual(
            [topology.NickelPool(nickel=[[1, 1, 1], []], pool={3: 0})],
            out)

    def test_3_6(self):
        in1 = topology.NickelPool(nickel=[[1, 2, 3]], pool={3: 5})
        in2 = topology.NickelPool(nickel=[[1, 2, 3], [4, 5]], pool={3: 4})
        self.assertTrue(in2 in list(topology.AddNodeFromPool(in1)))
        in3 = topology.NickelPool(nickel=[[1, 2, 3], [4, 5], [4, 5]], pool={3: 3})
        self.assertTrue(in3 in list(topology.AddNodeFromPool(in2)))

    def test_2_1_4_1(self):
        inp = topology.NickelPool(nickel=[], pool={2: 1, 4: 1})
        out = []
        out.append(topology.NickelPool(nickel=[[0]], pool={2: 0, 4: 1}))
        out.append(topology.NickelPool(nickel=[[1, 1]], pool={2: 0, 4: 1}))
        out.append(topology.NickelPool(nickel=[[0, 0]], pool={2: 1, 4: 0}))
        out.append(topology.NickelPool(nickel=[[0, 1, 1]], pool={2: 1, 4: 0}))
        self.assertEqual(out, list(topology.AddNodeFromPool(inp)))

        self.assertEqual([], list(topology.AddNodeFromPool(out[0])))
        self.assertEqual(
                [topology.NickelPool(nickel=[[1, 1], [1]], pool={2: 0, 4: 0})],
                list(topology.AddNodeFromPool(out[1])))

    def testAddNodeFromPool(self):
        inp = topology.NickelPool(nickel=[], pool={3: 1})
        self.assertEqual([], list(topology.AddNodeFromPool(inp)))

        inp = topology.NickelPool(nickel=[], pool={2: 1})
        out = topology.NickelPool(nickel=[[0]], pool={2: 0})
        self.assertEqual([out], list(topology.AddNodeFromPool(inp)))

        inp = topology.NickelPool(nickel=[], pool={2: 3})
        out = []
        out.append(topology.NickelPool(nickel=[[0]], pool={2: 2}))
        out.append(topology.NickelPool(nickel=[[1, 1]], pool={2: 2}))
        out.append(topology.NickelPool(nickel=[[1, 2]], pool={2: 2}))
        self.assertEqual(out, list(topology.AddNodeFromPool(inp)))

        inp = topology.NickelPool(nickel=[[1, 1]], pool={3: 2})
        out = topology.NickelPool(nickel=[[1, 1], [2]], pool={3: 1})
        self.assertEqual([out], list(topology.AddNodeFromPool(inp)))

        inp = topology.NickelPool(nickel=[[1, 2]], pool={3: 2})
        out = []
        out.append(topology.NickelPool(nickel=[[1, 2], [1]], pool={3: 1}))
        out.append(topology.NickelPool(nickel=[[1, 2], [2, 2]], pool={3: 1}))
        self.assertEqual(out, list(topology.AddNodeFromPool(inp)))

        inp = topology.NickelPool(nickel=[[1, 2]], pool={1: 3, 3: 2})
        out = []
        out.append(topology.NickelPool(nickel=[[1, 2], [-1, -1]], pool={3: 1, 1: 1}))
        out.append(topology.NickelPool(nickel=[[1, 2], [-1, 2]], pool={3: 1, 1: 2}))
        out.append(topology.NickelPool(nickel=[[1, 2], [1]], pool={3: 1, 1: 3}))
        out.append(topology.NickelPool(nickel=[[1, 2], [2, 2]], pool={3: 1, 1: 3}))
        self.assertEqual(out, list(topology.AddNodeFromPool(inp)))

        inp = topology.NickelPool(nickel=[], pool={3: 1, 4: 1})
        out = []
        out.append(topology.NickelPool(nickel=[[0, 1]], pool={3: 0, 4: 1}))
        out.append(topology.NickelPool(nickel=[[1, 1, 1]], pool={3: 0, 4: 1}))
        out.append(topology.NickelPool(nickel=[[0, 0]], pool={3: 1, 4: 0}))
        out.append(topology.NickelPool(nickel=[[0, 1, 1]], pool={3: 1, 4: 0}))
        self.assertEqual(out, list(topology.AddNodeFromPool(inp)))

    def testLegsOptimization(self):
        inp = topology.NickelPool(nickel=[], pool={1: 2, 3: 2})
        out = list(topology.AddNodeFromPool(inp))
        self.assertTrue(
            topology.NickelPool(nickel=[[-1, -1, 1]], pool={1: 0, 3: 1}) in out)
        self.assertFalse(
            topology.NickelPool(nickel=[[1, 1, 1]], pool={1: 2, 3: 1}) in out)

    def testAddNodeOneParticleReducible(self):
        inp = topology.NickelPool(nickel=[[0]], pool={2: 1})
        self.assertEqual([], list(topology.AddNodeFromPool(inp)))

        inp = topology.NickelPool(nickel=[[0, 1]], pool={3: 1})
        self.assertEqual([], list(topology.AddNodeFromPool(inp)))

    def testCanonicalString(self):
        self.assertEqual('0-', topology.CanonicalString([[0]]))
        self.assertEqual('11--', topology.CanonicalString([[1, 1]]))
        self.assertEqual('1-2--', topology.CanonicalString([[1, 2]]))
        self.assertEqual('1-2--', topology.CanonicalString([[1], [2]]))

    def testMaxValenceInPool(self):
        self.assertEqual(0, topology.MaxValenceInPool({}))
        self.assertEqual(0, topology.MaxValenceInPool({1: 1}))
        self.assertEqual(0, topology.MaxValenceInPool({1: 1, 2: 0}))
        self.assertEqual(2, topology.MaxValenceInPool({1: 1, 2: 1}))

    def testCountNodesInPool(self):
        self.assertEqual(0, topology.CountNodesInPool({}))
        self.assertEqual(0, topology.CountNodesInPool({1: 1}))
        self.assertEqual(0, topology.CountNodesInPool({1: 1, 2: 0}))
        self.assertEqual(1, topology.CountNodesInPool({1: 1, 2: 1}))
        self.assertEqual(6, topology.CountNodesInPool({1: 1, 2: 1, 3: 5}))

    def testCountAllNodesInPool(self):
        self.assertEqual(0, topology.CountAllNodesInPool({}))
        self.assertEqual(1, topology.CountAllNodesInPool({1: 1}))
        self.assertEqual(1, topology.CountAllNodesInPool({1: 1, 2: 0}))
        self.assertEqual(2, topology.CountAllNodesInPool({1: 1, 2: 1}))
        self.assertEqual(7, topology.CountAllNodesInPool({1: 1, 2: 1, 3: 5}))

    def testNickelFitsPool(self):
        self.assertFalse(topology.NickelFitsPool([[1]], {}))
        # Big valence.
        self.assertFalse(topology.NickelFitsPool([[1, 1, 1]], {2: 1}))
        self.assertTrue(topology.NickelFitsPool([[1]], {2: 1}))
        # Two nodes are needed.
        self.assertFalse(topology.NickelFitsPool([[1, 2]], {2: 1}))
        self.assertTrue(topology.NickelFitsPool([[1, 1]], {2: 1}))

class TestConnectivity(unittest.TestCase):
    def testIsOneParticleReducible(self):
        self.assertFalse(topology.IsOneParticleReducibleOrConnectivity([]))
        self.assertTrue(topology.IsOneParticleReducibleOrConnectivity([[0]]))
        self.assertTrue(topology.IsOneParticleReducibleOrConnectivity([[0, 1]]))
        self.assertFalse(topology.IsOneParticleReducibleOrConnectivity([[1, 1]]))
        self.assertFalse(topology.IsOneParticleReducibleOrConnectivity([[1, 2]]))

        self.assertTrue(topology.IsOneParticleReducibleOrConnectivity(
                            [[1, 2, 3], [1], [3, 3], []]))
        self.assertTrue(topology.IsOneParticleReducibleOrConnectivity([[1, 2, 3], [1]]))

        self.assertTrue(topology.IsOneParticleReducibleOrConnectivity(
                            [[-1, 1, 2, 3], [-1, 1], [2, 3], [3]]))
        self.assertTrue(topology.IsOneParticleReducibleOrConnectivity(
                            [[-1, 1, 2, 3], [-1, 1]]))

        self.assertFalse(topology.IsOneParticleReducibleOrConnectivity([[1, 2, 3], [4, 5]]))

    def testIsNCutDisconnectable(self):
        self.assertTrue(topology.IsNCutDisconnectable([], 0))
        self.assertTrue(topology.IsNCutDisconnectable([[0, 1], [2, 3]], 0))

        self.assertFalse(topology.IsNCutDisconnectable([[0, 1]], 0))
        self.assertTrue(topology.IsNCutDisconnectable([[0, 1]], 1))

        self.assertFalse(
            topology.IsNCutDisconnectable([[0, 1], [1, 2], [2, 3], [3, 0]], 1))
        self.assertTrue(
            topology.IsNCutDisconnectable([[0, 1], [1, 2], [2, 3], [3, 0]], 2))

        self.assertTrue(
            topology.IsNCutDisconnectable(
                [[-1, 0], [0, 1], [0, 2], [0, 3], [-1, 1], [1, 1]], 1))

        self.assertTrue(
            topology.IsNCutDisconnectable([[0, 1], [0, 2], [1, 3]], 1))

    def testIsConnected(self):
        self.assertFalse(topology.IsConnected([]))
        # Lists and tuples.
        self.assertTrue(topology.IsConnected([[0, 1]]))
        self.assertTrue(topology.IsConnected([(0, 1)]))
        self.assertTrue(topology.IsConnected(((0, 1),)))

        self.assertFalse(topology.IsConnected([[0, 1], [2, 3]]))
        self.assertTrue(topology.IsConnected([[0, 1], [1, 2]]))
        # Leg is amputated
        self.assertFalse(topology.IsConnected([[-1, 1], [-1, 2]]))

        self.assertTrue(topology.IsConnected([[-1, 0], [-1, 0], [0, 1]]))

    def testGetNodesConnectedToNode(self):
        component = topology.GetNodesConnectedToNode([[-1, 0], [-1, 1]], 0)
        self.assertEqual(set([-1, 0]), component)

        component = topology.GetNodesConnectedToNode([[-1, 0], [-1, 1], [0, 2]], 0)
        self.assertEqual(set([-1, 0, 2]), component)

        component = topology.GetNodesConnectedToNode([[0, 3], [1, 1], [3, 2]], 0)
        self.assertEqual(set([0, 2, 3]), component)

    def testGetConnectedComponents(self):
        components = list(topology.GetConnectedComponents(
                [[-1, 0], [-1, 1]]))
        self.assertEqual([set([-1, 0]), set([-1, 1])], components)

        components = list(topology.GetConnectedComponents(
                [[-1, 0], [-1, 1], [0, 2]]))
        self.assertEqual([set([-1, 0, 2]), set([-1, 1])], components)

        components = list(topology.GetConnectedComponents(
                [[0, 3], [1, 1], [3, 2]]))
        self.assertEqual([set([0, 2, 3]), set([1])], components)

    def testRemoveNode(self):
        nonode = topology.RemoveNode([[0, 1], [0, 2]], 0)
        self.assertEqual([['0A', 1], ['0B', 2]], nonode)

    def testHasTadpole(self):
        self.assertFalse(topology.HasTadpole([[-1, 1]]))
        self.assertTrue(topology.HasTadpole([[0, 1]]))
        self.assertTrue(topology.HasTadpole([[-1, 0], [0, 0]]))
        self.assertTrue(topology.HasTadpole([[-1, 0], [0, 1], [1, 2], [1, 2]]))
        self.assertFalse(topology.HasTadpole(
                [[-1, 0], [0, 1], [0, 1], [1, 2], [1, 2], [2, -1]]))


if __name__ == "__main__":
    unittest.main()

