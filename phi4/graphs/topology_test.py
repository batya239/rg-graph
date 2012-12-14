#!/usr/bin/python

import topology
import unittest

class TestGetTopologies(unittest.TestCase):
    def testTopologies(self):
        #topologies = topology.GetTopologies({3: 2})
        #self.assertEqual(['111--'], topologies)
        pass

class TestUtil(unittest.TestCase):
    def testCountNode(self):
        self.assertEqual(1, topology.CountNode([[1]], 1))
        self.assertEqual(0, topology.CountNode([[1]], 2))
        self.assertEqual(2, topology.CountNode([[1, 2, 2], [1]], 1))

    def testCountInternalNodes(self):
        self.assertEqual(0, topology.CountInternalNodes(
            topology.NickelPool(nickel=[], pool={})))
        self.assertEqual(0, topology.CountInternalNodes(
            topology.NickelPool(nickel=[], pool={1: 1})))
        self.assertEqual(1, topology.CountInternalNodes(
            topology.NickelPool(nickel=[[0]], pool={})))
        self.assertEqual(1, topology.CountInternalNodes(
            topology.NickelPool(nickel=[], pool={3: 1})))

    def testAddNodeFromPool(self):
        inp = topology.NickelPool(nickel=[], pool={3: 1})
        out = topology.NickelPool(nickel=[[1] * 3], pool={3: 0})
        self.assertEqual([out], list(topology.AddNodeFromPool(inp)))

        inp = topology.NickelPool(nickel=[[1]], pool={3: 1})
        out = topology.NickelPool(nickel=[[1], [2, 2]], pool={3: 0})
        self.assertEqual([out], list(topology.AddNodeFromPool(inp)))

        inp = topology.NickelPool(nickel=[[1]], pool={3: 2})
        out = topology.NickelPool(nickel=[[1], [3, 3]], pool={3: 1})
        self.assertEqual([out], list(topology.AddNodeFromPool(inp)))

        inp = topology.NickelPool(nickel=[[1]], pool={3: 2, 1: 3})
        out = topology.NickelPool(nickel=[[1], [3, 3]], pool={3: 1, 1: 3})
        self.assertEqual([out], list(topology.AddNodeFromPool(inp)))

        inp = topology.NickelPool(nickel=[], pool={3: 1, 4: 1})
        out1 = topology.NickelPool(nickel=[[2] * 3], pool={3: 0, 4: 1})
        out2 = topology.NickelPool(nickel=[[2] * 4], pool={3: 1, 4: 0})
        self.assertEqual([out1, out2], list(topology.AddNodeFromPool(inp)))

if __name__ == "__main__":
    unittest.main()

