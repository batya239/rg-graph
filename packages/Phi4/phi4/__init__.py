#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

from ir_uv import IRRelevanceCondition, UVRelevanceCondition
from configure import Configure
from gfun_calculator import GGraphReducer
from r import ROperation
from const import DIM_PHI4, SPACE_DIM_PHI4
import graph_util
from numerators_util import GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR
from common import AbstractKOperation, MSKOperation, graph_has_not_ir_divergence_filter, CannotBeCalculatedError