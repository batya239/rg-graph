#! /usr/bin/python
#! encoding: utf8

__author__ = 'kirienko'


from d_to_infty_class import D_to_infty_graph as D
from sympy import var, factor, ln, prod, simplify, integrate, diff
from copy import deepcopy
from sign_account import sign_account
from collections import defaultdict
import os, sys


def cut_edges(G,sub1,sub2):
    """
    :param G: initial networkx graph
    :param sub1: list of nodes of the subgraph 1 of G
    :param sub2: list of nodes of the subgraph 1 of G
    :return: list of the internal edges of G such that are cut
    """
    edges = G.subgraph(sub1).edges(keys=True) + G.subgraph(sub2).edges(keys=True)
    return [e for e in G.edges_iter(keys=True) if (e not in edges and -1 not in e and -2 not in e)]

def integrand(graph_object, time_ver_number):
    """
    Returns integrand ( = numerator/denominator) that corresponds certain time version tv.
    No integral sign, no differentiantion and integration of stretching parameters.
    """
    version = graph_object.tv[time_ver_number]
    v = version[0]
    var(['k%d'%j for j in range(graph_object.Loops)])
    var(['a%d'%j for j in range(graph_object.Loops-1)])
    sq = lambda x: x**2
    denominator = 1
    for l in xrange(len(v)-1): # <-- loop over cuts
        all_momenta = [var('k%i'%i) for i in xrange(graph_object.Loops)]
        stretch_factors = dict(zip(all_momenta,[1 for i in xrange(len(all_momenta))]))
        edges = cut_edges(graph_object.U,v[:l+1],v[l+1:]) # <-- edges of the v
        ## Check if edges are in some significant subgraph
        for j,sub in enumerate(graph_object.tv[time_ver_number][1]):
            sg_nodes = [n for n in sub.vertices if n>-1]
            sg = graph_object.U.subgraph(sg_nodes)
            ## If the cut shares edges with subgraph, do stretches
            if set(sg.edges(keys=True)).intersection(set(edges)):
                ## Find simple momenta in this subgraph
                sg_simple_mom = [graph_object.momenta_in_edge(e)[0] for e in sg.edges(keys=True) if len(graph_object.momenta_in_edge(e)) == 1]
                for k in stretch_factors:
                    if str(k) not in sg_simple_mom:
                        stretch_factors[k] *= var('a%d'%j)
        # print "Stretching factors:",stretch_factors
        den = []
        for e in edges:
            m = [var(x) for x in graph_object.momenta_in_edge(e)]
            den += factor(map(sq,map(lambda x: stretch_factors[x]*x,m)))
        denominator *= sum(den)/2 ## NB: 1/2 is for eliminating all len(v)-1 powers of 2 in the denominator
    
    numerator = 1
    numerator *= reduce(lambda x,y: x*y, var(['k%d'%j for j in range(graph_object.Loops)])) # <-- Jacobian
    for b in graph_object.bridges:
        test = map(lambda x: int(graph_object.flow_near_node(x),2),b)
        shared_mom_bin = bin(test[0]&test[1])[2:]
        shared_mom     = [var("k%d"%j) for j,k in enumerate(shared_mom_bin[::-1]) if int(k) and j < graph_object.Loops]
        if len(shared_mom) == 0:
            continue
        else:
            num = 0
            for m in shared_mom:
                term = sq(m)
                for j,sub in enumerate(graph_object.tv[time_ver_number][1]):
                    ext_nodes = set([e.nodes[1] for e in sub.external_edges])
                    all_nodes = set([x for x in sub.vertices if x>-1])
                    int_nodes = all_nodes.difference(ext_nodes)
                    internal_mom = graph_object.subgraph_simple_momenta(sub)
                    if str(m) not in internal_mom and b[0] in int_nodes and b[1] in int_nodes:
                        term *= sq(var('a%d'%j))
                    elif str(m) not in internal_mom and b[0] in int_nodes and b[1] not in int_nodes:
                        term *= var('a%d'%j)
                    elif str(m) not in internal_mom and b[0] not in int_nodes and b[1] in int_nodes:
                        term *= var('a%d'%j)
                num += term
            numerator *= (num)
    # print "numerator:\t",numerator
    # print "denominator:\t",denominator
    return numerator/denominator
    
def integrate_diff_sympy(eq,var):
    #print "Integrate:\n",eq
    return integrate(diff(eq,var),(var,0,1))

def integrate_over_a_maple():
    pass

def get_letters_k(eq,L):
    return [var("k%d"%j) for j in xrange(L) if eq.has(var("k%d"%j))]
    
def integrand_maple(graph_obj,order = 0):
    """
    
    :param graph_obj: instance of D_to_infty_graph class
    :return: integrand as a string
    """

    # diag_number = diag_dict[graph_obj.nickel]
    tv = graph_obj.get_time_versions()
    integrands = defaultdict(list)
    for tv_num,ver in enumerate(tv):       ## Loop over time versions
        _integrand = integrand(graph_obj, tv_num) ## this is a composition pf sympy variables
        
        ## taking partial with respect to m
        ans = []
        for l in xrange(graph_obj.Loops):
            __int = deepcopy(_integrand)
            for j,sub in enumerate(tv[tv_num][1]):
                if "k%d"%l in graph_obj.subgraph_simple_momenta(sub):
                    __int = __int.subs(var("a%d"%j),1)
            ans += [factor(__int.subs(var("k%d"%l),1))]
        
        ## Add log() and posible variable substitution
        for a in ans:
            # letters_k = [var("k%d"%j) for j in xrange(graph_obj.Loops) if a.has(var("k%d"%j))]
            letters_k = get_letters_k(a, graph_obj.Loops)
            
            a = a/prod(letters_k)/2**len(letters_k)                     # Jacobian
            a = a.subs([(i**2,i) for i in letters_k],simultaneous=True) # k² --> k

            if order == 1:
                a *= ln(prod(letters_k)) / 2
            elif order == 2:
                a *= (ln(prod(letters_k))/ 2)**2/2

        ## sp.simplify(sp.integrate(sp.diff(eq,a0),(a0,0,1)))
        ## Add integration and partial derivative
        str_ans = []
        for a in ans:
            tmp = a
            letters_a = []
            for j,sub in enumerate(tv[tv_num][1]):
                if a.has(var("a%d"%j)): # if there's an 'a' --> differentiate
                    letters_a += ["a%d"%j]
                    tmp = integrate_diff_sympy(tmp,letters_a[-1])
            key = "/".join(sorted(map(str,get_letters_k(a,graph_obj.Loops))))
            integrands[key].append(tmp)

        #TODO: MARK
    ## sum up all time versions
    ans = []
    for k,v in integrands.items():
        integrands[k] = sum(v)

    str_ans = []
    for k,v in integrands.items():
        k_vars = "["+",".join(map(lambda x:"%s=1..infinity"%x,k.split('/')))+"]"
        str_ans += [("Int(%s,%s)"% (str(v),k_vars)).replace("**","^")]

    sign = sign_account(graph_obj)
    if sign == 1:
        return ('j:=%s:'%('+'.join(str_ans)))
    else:
        return ('j:=-(%s):'%('+'.join(str_ans)))

if  __name__ == "__main__":
    analytic = False
    ## get variables 'loops' and 'ipython_profile'
    try:
        from config import *
    except ImportError:
        loops = 3
        order = 0  ##
        digits = 10
        ipython_profile = 'default'

    vasya = 'e12|e3|34|5|55||:0A_aA_dA|0a_dA|dd_aA|aa|aA_dd||' # 5/32+5/8*Log(2) (No 1)
    one   = 'e12|e3|34|5|55||:0A_dd_aA|0a_Aa|dd_aA|Aa|aA_dd||' # 0, one time version (No 18)
    z     = 'e12|e3|45|45|5||:0A_dd_aA|0a_Aa|aA_da|Aa_dA|dd||' # -π²/24+1/4*Log(2)+1/4 ≈ 0.0120532784279297182362, two time versions (No 32)
    d5    = 'e12|e3|34|5|55||:0A_aA_dA|0a_dA|dd_aA|aA|aa_dd||'
    d25   = 'e12|e3|45|45|5||:0A_aA_dA|0a_dA|aa_dd|dd_aA|Aa||'
    d40   = 'e12|e3|44|55|5||:0A_dd_aA|0a_Aa|aA_dd|Aa_dd|aA||' # -π²/24, one time version ≈ -0.411233516712 
    d48   = 'e12|23|4|45|5|e|:0A_aA_dA|dd_aA|aA|dd_aA|ad|0a|'
    d77   = 'e12|23|4|e5|55||:0A_aA_dA|dd_aA|aA|0a_dA|aa_dd||'
    new   = 'e12|23|4|e5|67|89|89|89|||:0A_aA_da|dd_aA|Aa|0a_dA|Aa_dd|aA_dd|dd_Aa|Aa_aA|||'

    name = D(sys.argv[1])
    print "restart:"
    print "Digits:=%d:" % digits
    print "assume(%s):"%", ".join(["k%s>1"%i for i in xrange(loops)])

    print integrand_maple(name,order)
    print 'printf("%%s --> %%.9e","%s",Re(j));'%(name.nickel)

