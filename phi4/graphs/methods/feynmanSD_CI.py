#!/usr/bin/python
# -*- coding:utf8
import calculate
from methods import sd_tools

from feynman_tools import normalize
method_name= "feynmanSD_CI"
sd_tools.method_name=method_name
Prepare = sd_tools.Prepare
save = sd_tools.save
compile = sd_tools.compile_mpi
sd_tools.code_=sd_tools.core_pvmpi_code

def execute(name, model, points=10000, threads=4, calc_delta=0., neps=0):
    return calculate.execute_mpi("%s/%s/"%(method_name,name), model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)


def result(model, method, **kwargs):
    return calculate.result(model, method, **kwargs)