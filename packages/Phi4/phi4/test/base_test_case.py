#!/usr/bin/python
# -*- coding: utf8
import unittest
from rggraphenv import storage, theory, symbolic_functions
import time

__author__ = 'daddy-bear'


class GraphStorageAwareTestCase(unittest.TestCase):
    TIME = 0

    def setUp(self):
        self.startTime = time.time()
        storage.initStorage(theory.PHI4, symbolic_functions.to_internal_code, graphStorageUseFunctions=True)

    def tearDown(self):
        storage.closeStorage(revert=True)
        t = time.time() - self.startTime
        print "TIME - %s: %.3f" % (self.id(), t)

    @classmethod
    def setUpClass(cls):
        GraphStorageAwareTestCase.TIME = time.time()

    @classmethod
    def tearDownClass(cls):
        t = time.time() - GraphStorageAwareTestCase.TIME
        print "SUMMARY TIME : %.3f" % t

