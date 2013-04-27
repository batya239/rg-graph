#!/usr/bin/python
# -*- coding:utf8
import sys
import calculate
import sympy
from methods import sd_tools
import hashlib

from feynman_tools import normalize
from methods.feynman_tools import strech_indexes
from methods.sd_tools import xTreeElement

method_name = "feynmanSD_SF"
sd_tools.method_name = method_name
Prepare = sd_tools.Prepare
save = sd_tools.save
compile = sd_tools.compile
sd_tools.code_ = sd_tools.core_pv_code
code_ = sd_tools.core_pv_code

#mpi
#compile = sd_tools.compile_mpi
#sd_tools.code_=sd_tools.core_pvmpi_code

introduce = True

#sd_tools.debug = True

sd_tools.MaxSDLevel = -1
sd_tools.MaxABranches = -1
#sd_tools.MaxABranches=0
sd_tools._CheckBadDecomposition = True
#sd_tools._CheckBadDecomposition = False

#sd_tools._ASym2=False
#sd_tools._SSym=False

sd_tools._ASectorsDots = True


def execute(name, model, points=10000, threads=4, calc_delta=0., neps=0):
    return calculate.execute("%s/%s/"%(method_name,name), model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)


def result(model, method, **kwargs):
    return calculate.result(model, method, **kwargs)

from dynamics import relabel, rules

def saveSectorFile(name, graph, model):
    name_ = name[:name.rfind('/')] + "/sectors"

    f = open("%s.py" % name_, 'w')

    lfactor = 1.
    for qi_ in graph._qi.keys():
        lfactor = lfactor / sympy.factorial(graph._qi[qi_] - 1)
    D = relabel(graph._det, rules)
    if graph._cdet is None:
        C = relabel([[]], rules)
    else:
        C = relabel(graph._cdet, rules)
    ui = list()
    for qi_ in graph._qi:
        ui += [qi_] * (graph._qi[qi_] - 1)
    U = relabel([ui, ], rules)
    Coef = lfactor * graph.sym_coef()

    ua = list()
    for qi_ in graph._qi:
    #    for qi_ in [5,]:
        strechs = list()
        for i in range(len(graph._eqsubgraphs)):
            if qi_ in graph._eqsubgraphs[i]:
                strechs.append(i + 1000)
        ua.append(strechs + [qi_, ])

    T = relabel(ua, rules)

    sub_idx = -1
    for sub in graph._subgraphs:
        sub_idx += 1
        sub._strechvar = 1000 + sub_idx
        print "%s sub = %s" % (sub._strechvar, sub)

    strechs = strech_indexes(graph, model)
    print "strechs =", strechs

    Nf = 10000
    maxsize = 30000
    sector_terms = dict()

    idx = -1
    sectors = dict()
    cnt = 0
    for tree in graph._sectors:
        for sector in xTreeElement(tree, graphstate=True):
            if sd_tools._ASym2:
                cnomenkl = sector.graph_state
            else:
                cnomenkl = cnt
                cnt += 1
            if cnomenkl in sectors:
                sectors[cnomenkl].coef += sector.coef
            else:
                sectors[cnomenkl] = sector

    print "ASectors2 = ", len(sectors.keys())

    f.write("from dynamics import D1, D2, to1, mK0, mK1 \n\n")

    f.write('D = %s\nC = %s\nU = %s\nT = %s\nCoef = %s\n\n' % (D, C, U, T, Coef))

    f.write("sectors = [\n")

    for cnom in sectors:
        sector = sectors[cnom]

        idx += 1

        if (idx + 1) % (Nf / 10) == 0:
            print "%s " % (idx + 1)

        aOps = list()
        for var in strechs:
            varIdx = var - 1000
            if strechs[var] == 0:
                if var not in sector.ds or sector.ds[var] == 1:
                    aOps.append("\"to1('a%s')\"" % varIdx)
                else:
                    raise ValueError, "invalid strech %s : strechs = %s, sector.ds = %s " % (var, strechs, sector.ds)
            else:
                if var in sector.ds:
                    if sector.ds[var] == 1:
                        aOps.append("\"to1('a%s')\"" % varIdx)
                    else:
                        aOps.append("\"mK%s('a%s')\"" % (strechs[var] - 1, varIdx))
                else:
                    aOps.append("\"D%s('a%s')\"" % (strechs[var], varIdx))
        f.write("    (%s, %s, %s),\n" % sector.simpleRepresentation(aOps))
    f.write("]\n")

sd_tools.save_sd = saveSectorFile