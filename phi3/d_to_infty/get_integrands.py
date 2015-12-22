#! /usr/bin/python
#! encoding: utf8

__author__ = 'kirienko'


from d_to_infty_class import D_to_infty_graph as D
from sympy import var, factor, ln, prod
from copy import deepcopy
from sign_account import sign_account
import os, sys


def cut_edges(G,sub1,sub2):
    """

    :param nx_graph: initial networkx graph G
    :param sub1: list of nodes of the subgraph 1 of G
    :param sub2: list of nodes of the subgraph 1 of G
    :return: list of the internal edges of G such that are cut
    """
    edges = G.subgraph(sub1).edges(keys=True) + G.subgraph(sub2).edges(keys=True)
    return [e for e in G.edges_iter(keys=True) if (e not in edges and -1 not in e and -2 not in e)]


def integrand_maple(graph_obj, tv_num, dn, order=0):
    """
    
    :param graph_obj: instance of D_to_infty_graph class
    :param tv_num: number of time version to produce integrand
    :param dn: number of the diagram (some unique number)
    :return: integrand as a string
    """
    # diag_number = diag_dict[graph_obj.nickel]
    tv = graph_obj.get_time_versions()
    v = tv[tv_num][0]
    var(['k%d'%j for j in range(graph_obj.Loops)])
    var(['a%d'%j for j in range(graph_obj.Loops-1)])
    sq = lambda x: x**2
    denominator = 1
    for l in xrange(len(v)-1): # <-- loop over cuts
        all_momenta = [var('k%i'%i) for i in xrange(graph_obj.Loops)]
        stretch_factors = dict(zip(all_momenta,[1 for i in xrange(len(all_momenta))]))
        edges = cut_edges(graph_obj.U,v[:l+1],v[l+1:]) # <-- edges of the cut
        # print "\nMomenta in the cut",v[:l+1],"|",v[l+1:],":",map(graph_obj.momenta_in_edge,edges)
        ## Check if edges are in some significant subgraph
        for j,sub in enumerate(tv[tv_num][1]):
            sg_nodes = [n for n in sub.vertices if n>-1]
            sg = graph_obj.U.subgraph(sg_nodes)
            ## If the cut shares edges with subgraph, do stretches
            if set(sg.edges(keys=True)).intersection(set(edges)):
                ## Find simple momenta in this subgraph
                sg_simple_mom = [graph_obj.momenta_in_edge(e)[0] for e in sg.edges(keys=True) if len(graph_obj.momenta_in_edge(e)) == 1]
                # print "Subgraph:",sub," simple momenta:",sg_simple_mom
                for k in stretch_factors:
                    if str(k) not in sg_simple_mom:
                        stretch_factors[k] *= var('a%d'%j)
        # print "Stretching factors:",stretch_factors
        den = []
        for e in edges:
            # print "Edge:",e
            m = [var(x) for x in graph_obj.momenta_in_edge(e)]
            # print m,stretch_factors[m[0]]
            # print var(graph_obj.momenta_in_edge(e))
            den += factor(map(sq,map(lambda x: stretch_factors[x]*x,m)))
        denominator *= sum(den)/2 ## NB: 1/2 is for eliminating all len(v)-1 powers of 2 in the denominator

    numerator = 1
    numerator *= reduce(lambda x,y: x*y, var(['k%d'%j for j in range(graph_obj.Loops)])) # <-- Jacobian
    for b in graph_obj.bridges:
        test = map(lambda x: int(graph_obj.flow_near_node(x),2),b)
        shared_mom_bin = bin(test[0]&test[1])[2:]
        shared_mom     = [var("k%d"%j) for j,k in enumerate(shared_mom_bin[::-1]) if int(k) and j < graph_obj.Loops]
        if len(shared_mom) == 0:
            continue
        else:
            num = 0
            for m in shared_mom:
                term = sq(m)
                for j,sub in enumerate(tv[tv_num][1]):
                    ext_nodes = set([e.nodes[1] for e in sub.external_edges])
                    all_nodes = set([x for x in sub.vertices if x>-1])
                    int_nodes = all_nodes.difference(ext_nodes)
                    internal_mom = graph_obj.subgraph_simple_momenta(sub)
                    if str(m) not in internal_mom and b[0] in int_nodes and b[1] in int_nodes:
                        term *= sq(var('a%d'%j))
                    elif str(m) not in internal_mom and b[0] in int_nodes and b[1] not in int_nodes:
                        term *= var('a%d'%j)
                    elif str(m) not in internal_mom and b[0] not in int_nodes and b[1] in int_nodes:
                        term *= var('a%d'%j)
                num += term
            numerator *= (num)
    # print "\nDiagram: J%s, time version #%d"%(diag_number,tv_num)
    # print "numerator:\t",numerator
    # print "denominator:\t",denominator
    # print numerator/factor(denominator)
    _integrand = (numerator/denominator)

    ## taking partial with respect to m
    ans = []
    for l in xrange(graph_obj.Loops):
        # print "k%d --> 1:"%l
        __int = deepcopy(_integrand)
        for j,sub in enumerate(tv[tv_num][1]):
            # print "Simple momenta for sub#%d"%j,graph_obj.subgraph_simple_momenta(sub)
            if "k%d"%l in graph_obj.subgraph_simple_momenta(sub):
                __int = __int.subs(var("a%d"%j),1)
                # print "\ta%d --> 1"%j
        ans += [factor(__int.subs(var("k%d"%l),1))]


    ## Add integration and partial derivative
    str_ans = []
    for a in ans:
        letters_k = [var("k%d"%j) for j in xrange(graph_obj.Loops) if a.has(var("k%d"%j))]

        ## variable substitution: k² --> k
        if order == 0:
            a = a/prod(letters_k)/2**len(letters_k)                     # Jacobian
            a = a.subs([(i**2,i) for i in letters_k],simultaneous=True) # k² --> k

        if order == 1:
            # a *= ln(prod(letters_k)) / 2
            a *= ln(prod(letters_k))
        elif order == 2:
            # a *= (ln(prod(letters_k))/ 2)**2/2
            a *= (ln(prod(letters_k)))**2/2
        tmp = ''
        letters_a = []
        for j,sub in enumerate(tv[tv_num][1]):
            if a.has(var("a%d"%j)):
                letters_a += ["a%d"%j]
                if tmp == '':
                    # if analytic:
                    tmp = 'int(diff(%s,a%d)'%(str(a),j)
                    # else:
                    #     tmp = 'Int(diff(%s,a%d)'%(str(a),j)
                    # print "1)",tmp
                else:#
                    tmp = tmp[:-1]+',a%d)'%j
                    # print "2)",tmp
        if letters_a:
            tmp = tmp+',[%s])'%",".join(['%s=0..1'%l for l in letters_a])
            for letter in letters_a:
                tmp = tmp.replace("%s**2"%letter,letter)
        # if letters_a and letters_k:
        #     tmp = tmp[:-1]+",Assumptions->{%s}]"%",".join(["%s>1"%letter for letter in letters_k])
        for j in xrange(graph_obj.Loops):
            if a.has(var("k%d"%j)):
                if tmp == '':
                    if analytic:
                        tmp = 'int(%s,[k%d = 1..infinity])'%(str(a),j)
                    else:
                        tmp = 'Int(%s,[k%d = 1..infinity])'%(str(a),j)
                    # print "3)",tmp
                elif tmp[:9]=='int(diff(':
                    if analytic:
                        tmp = 'int(%s,[k%d =1..infinity])'%(tmp,j)
                    else:
                        # print "4)",tmp
                        tmp = 'Int(%s,[k%d =1..infinity])'%(tmp,j)
                else:
                    tmp = tmp[:-2]+',k%d =1..infinity])'%j
                    # print "5)",tmp

        str_ans += [tmp.replace("**","^")]
    if analytic:
        return 'j%sv%d:=simplify(%s):'%(dn,tv_num,'+'.join(str_ans))
    else:
        return ('j%sv%d:=(%s):'%(dn,tv_num,'+'.join(str_ans)))

if  __name__ == "__main__":
    analytic = False
    ## get variables 'loops' and 'ipython_profile'
    try:
        from config import *
    except ImportError:
        loops = 3
        order = 0
        digits = 10
        ipython_profile = 'default'

    vasya = 'e12|e3|34|5|55||:0A_aA_dA|0a_dA|dd_aA|aa|aA_dd||' # 5/32+5/8*Log(2) (No 1)
    one   = 'e12|e3|34|5|55||:0A_dd_aA|0a_Aa|dd_aA|Aa|aA_dd||' # 0, one time version (No 18)
    z     = 'e12|e3|45|45|5||:0A_dd_aA|0a_Aa|aA_da|Aa_dA|dd||' # -π²/24+1/4*Log(2)+1/4 ≈ 0.0120532784279297182362, two time versions (No 32)
    d5    = 'e12|e3|34|5|55||:0A_aA_dA|0a_dA|dd_aA|aA|aa_dd||'
    d25   = 'e12|e3|45|45|5||:0A_aA_dA|0a_dA|aa_dd|dd_aA|Aa||'
    d40   = 'e12|e3|44|55|5||:0A_dd_aA|0a_Aa|aA_dd|Aa_dd|aA||' # -π²/24, one time version
    d48   = 'e12|23|4|45|5|e|:0A_aA_dA|dd_aA|aA|dd_aA|ad|0a|'
    d77   = 'e12|23|4|e5|55||:0A_aA_dA|dd_aA|aA|0a_dA|aa_dd||'
    new   = 'e12|23|4|e5|67|89|89|89|||:0A_aA_da|dd_aA|Aa|0a_dA|Aa_dd|aA_dd|dd_Aa|Aa_aA|||'

    name = sys.argv[1]
    with open('diags_%d_loops/nonzero/%s'%(loops,name.replace('|','-'))) as fd:
        str_diags = [d.strip() for d in fd.readlines()]

    diags = [D(x) for x in str_diags]
    # one_tv = [x for x in diags if len(x.get_time_versions())==1]
    # tvs = 20
    # tv = [x for x in diags if len(x.get_time_versions()) == tvs]
    pg = digits
    for diag_num,x in enumerate(diags):
        print "restart:"
        print "Digits:=%d:" % pg
        print "assume(%s):"%", ".join(["k%s>1"%i for i in xrange(loops)])
        sign = sign_account(x)

        tv_num = len(x.get_time_versions())
        for ver_num in xrange(tv_num):
            print integrand_maple(x,ver_num,diag_num,order)
        if sign_account(x) == 1:
            if analytic:
                print "j%s:=simplify("%(diag_num)+\
                  " + ".join(["j%sv%d"%(diag_num,i) for i in xrange(tv_num)])+"):"
            else:
                print "j%s:=%s:"%(diag_num,"+".join(["j%sv%d" % (diag_num, i) for i in xrange(tv_num)]))
        else:
            if analytic:
                print "j%s := simplify(-("%(diag_num)+\
                  "+".join(["j%sv%d"%(diag_num,i) for i in xrange(tv_num)])+")):"
            else:
                print "j%s:=-(%s):"%(diag_num, "+".join(["j%sv%d"%(diag_num,i) for i in xrange(tv_num)]))
        print 'printf("\\n%%s --> %%.%de","%s",Re(j%s));'%(pg, x.nickel, diag_num)
