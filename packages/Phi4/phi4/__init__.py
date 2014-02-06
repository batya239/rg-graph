#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import ir_uv
import lambda_number
from gfun_calculator import GGraphReducer
from r import KR1, KRStar_quadratic_divergence
import r
import graph_util
from numerators_util import GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR
from common import AbstractKOperation, MSKOperation, defaultGraphHasNotIRDivergenceFilter, DEFAULT_SUBGRAPH_UV_FILTER, CannotBeCalculatedError