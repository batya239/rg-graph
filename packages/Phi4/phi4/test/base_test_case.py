#!/usr/bin/python
# -*- coding: utf8
import unittest
from rggraphenv import storage, theory
import symbolic_functions

__author__ = 'daddy-bear'


class GraphStorageAwareTestCase(unittest.TestCase):
    def setUp(self):
        storage.initStorage(theory.PHI4, symbolic_functions.toInternalCode, graphStorageUseFunctions=True)

    def tearDown(self):
        storage.closeStorage(revert=True)