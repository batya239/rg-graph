#!/usr/bin/python
# -*- coding: utf8
from rggraphutil.env import graph_calculator

__author__ = 'dima'

import symbolic_functions
from gfunctions.gfun_calculator import GGraphReducer
from graphine.momentum import oneIrreducible, connected, \
    xPassExternalMomentum, xPickPassingExternalMomentum, passMomentOnGraph, xArbitrarilyPassMomentum
from graphine.filters import graphFilter
from gfunctions.r import KR1
from common import AbstractKOperation, MSKOperation, defaultGraphHasNotIRDivergenceFilter, defaultSubgraphUVFilter, CannotBeCalculatedError