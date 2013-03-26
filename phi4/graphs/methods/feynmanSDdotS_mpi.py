#!/usr/bin/python
# -*- coding:utf8
import sys
import calculate
import sympy
from methods import sd_tools
import hashlib

from feynman_tools import normalize
from methods.feynman_tools import strech_indexes
from methods.poly_tools import poly_exp
from methods.sd_tools import _cnomenkl, debug, xTreeElement, decompose_expr, diff_subtraction, save_sectors

import methods.feynmanSDdot

method_name = "feynmanSDdotS_mpi"
sd_tools.method_name = method_name
Prepare = sd_tools.Prepare
save = sd_tools.save
compile = sd_tools.compile
sd_tools.code_ = sd_tools.core_pvmpi_code
code_ = sd_tools.core_pvmpi_code
methods.feynmanSDdot.code_ = code_
sd_tools.save_sd = methods.feynmanSDdot.save_sd

#mpi
#compile = sd_tools.compile_mpi
#sd_tools.code_=sd_tools.core_pvmpi_code


#sd_tools.debug = True

sd_tools.MaxSDLevel = -1
sd_tools.MaxABranches = -1
#sd_tools.MaxABranches=0
sd_tools._CheckBadDecomposition = True
#sd_tools._CheckBadDecomposition = False

#sd_tools._ASym2=False
#sd_tools._SSym=False

sd_tools._ASectorsDots = True

sd_tools.save_sd = methods.feynmanSDdot.saveSectorFile


def execute(name, model, points=10000, threads=4, calc_delta=0., neps=0):
    return calculate.execute("%s/%s/" % (method_name,name), model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)


def result(model, method, **kwargs):
    return calculate.result(model, method, **kwargs)