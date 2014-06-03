#!/usr/bin/python
# -*- coding: utf8

#
# common environment objects
#
import theory
import graph_calculator
import symbolic_functions
from storage import StorageSettings, StoragesHolder
from graph_calculator import GraphCalculatorManager
from abstract_graph_calculator import AbstractGraphCalculator
from g_graph_calculator import GLoopCalculator
try:
    from mongo_storage import MongoClientWrapper, GraphIdExtractor, StrGraphIdExtractor
except ImportError:
    pass

__author__ = 'daddy-bear'


