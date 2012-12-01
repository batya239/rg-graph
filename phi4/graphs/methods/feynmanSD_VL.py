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

method_name= "feynmanSD_VL"
sd_tools.method_name=method_name
Prepare = sd_tools.Prepare
save = sd_tools.save
compile = sd_tools.compile
sd_tools.code_=sd_tools.core_pv_code
code_=sd_tools.core_pv_code

#mpi
#compile = sd_tools.compile_mpi
#sd_tools.code_=sd_tools.core_pvmpi_code


#sd_tools.debug=True


sd_tools.MaxSDLevel=-1
sd_tools.MaxABranches=-1
sd_tools._CheckBadDecomposition=True
#sd_tools._CheckBadDecomposition=False

#sd_tools._ASym2=False
#sd_tools._SSym=False

def save_sd(name, graph, model):
    name_ = "%s_%s_" % (name, "O")
    neps = model.target - graph.NLoops()

    lfactor = 1.
    for qi_ in graph._qi.keys():
        lfactor = lfactor / sympy.factorial(graph._qi[qi_] - 1)
    if graph._cdet == None:
        A1 = poly_exp(graph._det, (-2, 0.5), coef=(float(lfactor * graph.sym_coef()), 0))
    else:
        A1 = poly_exp(graph._det, (-3, 0.5), coef=(float(lfactor * graph.sym_coef()), 0))
    ui = reduce(lambda x, y: x + y, [[qi_] * (graph._qi[qi_] - 1) for qi_ in graph._qi])
    ui = list()
    for qi_ in graph._qi:
        ui += [qi_] * (graph._qi[qi_] - 1)
    A2 = poly_exp([ui, ], (1, 0))

    ua = list()
    for qi_ in graph._qi:
    #    for qi_ in [5,]:
        strechs = list()
        for i in range(len(graph._eqsubgraphs)):
            if qi_ in graph._eqsubgraphs[i]:
                strechs.append(i + 1000)
        ua.append(strechs + [qi_, ])

    A3 = poly_exp(ua, (3, 0))
    print
    print "A1 ", A1
    print "A2 ", A2
    print "A3 ", A3

    if graph._cdet <> None:
        A4 = poly_exp(graph._cdet, (1, 0), coef=(-1, 0))

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
    size = 0
    idx_save = 0
    Nsaved = 0
    NZero = 0
    sectors=dict()
    cnt=0
    for tree in graph._sectors:
        for sector in xTreeElement(tree,graphstate=True):
            if sd_tools._ASym2:
                cnomenkl=sector.graph_state
            else:
                cnomenkl=cnt
                cnt+=1
            if sectors.has_key(cnomenkl):
                sectors[cnomenkl].coef+=sector.coef
            else:
                sectors[cnomenkl]=sector

#    if debug:
#        for cnom in sectors:
#            sector=sectors[cnom]
##            print " pt pt ",  hashlib.sha1(cnom).hexdigest(), sectors[cnom].coef
#            print " pt pt -",  str(cnom)

    print "ASectors2 = ", len(sectors.keys())

    #    for tree in graph._sectors:
    #        for sector in xTreeElement(tree):
    for cnom  in sectors:
        sector=sectors[cnom]
#        name_="%s_%s_%s_"%(name,hashlib.sha1(str(cnom)).hexdigest(), hashlib.sha1(str(cnom)).hexdigest())
    #            print "sector = ", subsectors
        #sector = Sector(subsectors)
        #            print
        #            print "sector = ", sector
        C_ = poly_exp([[]], (1, 0), coef=(sector.coef, 0))
        idx += 1

        if (idx + 1) % (Nf / 10) == 0:
            print "%s " % (idx + 1)

        if graph._cdet == None:
            terms = decompose_expr(sector, [A1, A2, A3, C_], strechs)
        else:
            terms = decompose_expr(sector, [A1, A2, A3, A4, C_], strechs)

        #            print "A3=",A3
        #            print "A4=",A4
        #            print
        #            print factorize_poly_lst(terms[0])

        s_terms = list()
        for term in terms:
            s_terms += diff_subtraction(term, strechs, sector)

        s_terms_ = list()
        for term in s_terms:
            if len(term) > 0:
                s_terms_.append(term)
        if len(s_terms_) > 0:
            sector_terms[sector] = s_terms_
            size += s_terms_.__sizeof__()
        else:
            NZero += 1

        if size>=maxsize:
            save_sectors(graph, sector_terms, strechs.keys(), name_, idx_save, neps)
            idx_save +=1
            Nsaved += len(sector_terms)
            print "saved to file  %s(%s) sectors (%s) size=%s..." % (Nsaved, Nsaved + NZero, idx_save, size)
            sys.stdout.flush()
            sector_terms = dict()
            size = 0

    if len(sector_terms) > 0:
        save_sectors(graph, sector_terms, strechs.keys(), name_, idx_save, neps)
        idx_save += 1
        Nsaved += len(sector_terms)
        print "saved to file  %s(%s) sectors (%s) size=%s..." % (Nsaved, Nsaved + NZero, idx_save, size)
        sys.stdout.flush()
        sector_terms = dict()

    for j in range(neps + 1):
        f = open("%s_E%s.c" % (name_, j), 'w')
        f.write(code_(idx_save - 1, len(graph._qi.keys()) + len(strechs.keys()), "%s_func" % name_, neps=j))
        f.close()

sd_tools.save_sd=save_sd

def execute(name, model, points=10000, threads=4, calc_delta=0., neps=0):
    return calculate.execute("%s/%s/"%(method_name,name), model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)


def result(model, method, **kwargs):
    return calculate.result(model, method, **kwargs)