#!/usr/bin/python
# -*- coding:utf8

model=None
import sys
import re
import rggraph_static as rggrf
import sympy

def usage(progname):
    return "%s -model phi3R [-overwrite] [-graph str_nickel] [-debug]"

if "-model" in sys.argv:
    model_module = sys.argv[sys.argv.index('-model')+1]
    try:
        exec('from %s import *'%model_module)
    except:
        print "Error while importing model!"
        sys.exit(1)
else:
    print "Usage : %s " %usage(sys.argv[0])
    sys.exit(1)


if "-graph" in sys.argv:
    g_list = [sys.argv[sys.argv.index('-graph')+1],]
else:
    g_list = model.GraphList()
    
if "-debug" in sys.argv:
    debug = True
else:
    debug = False


if "-nloops" in sys.argv:
    nloops = eval(sys.argv[sys.argv.index('-nloops')+1])
    if isinstance(nloops,int):
        nloops = [nloops,]
else:
    nloops = range(1,model.target+1)    

def CheckNodes(G):
    for idxN in G.internal_nodes:
        if G.nodes[idxN].type <> 1:
            return False
    return True

                 
def StrechAllSubgraphs(G):
    cur_G=G.Clone()
    cur_G.s_degree=dict()
    cur_G.s_type=dict()
    for sub in cur_G.subgraphs:
        sub_ext_atoms_str = FindExtMomentAtoms(sub)
        strech_var_str = "s%s"%cur_G.subgraphs.index(sub)
        sub_ext_path = [(i[0],i[1],strech_var_str) for i in FindExtMomentPath(sub, sub_ext_atoms_str)]
        for idx in sub_ext_path:
            if idx[1]=="L":
                obj = cur_G.lines[idx[0]]
            elif idx[1]=="N":
                obj = cur_G.nodes[idx[0]]
            model.AddStrech(obj, strech_var_str, sub_ext_atoms_str)
        if sub.type == 2:
            cur_G.s_type[strech_var_str]= 2
            cur_G.s_degree[strech_var_str] = subgraph_dim_with_diff(cur_G, sub)/sympy.Number(2) + 1
        elif sub.type == 1:
            cur_G.s_type[strech_var_str]= 1
            cur_G.s_degree[strech_var_str] = subgraph_dim_with_diff(cur_G, sub) + 1
        else: 
            raise ValueError, "invalid subgraph type (%s)"%sub.type
        
        
        
    return cur_G
                     
        

for nickel in g_list: 
    G = model.LoadGraph(nickel)
    if G.NLoops() in nloops:
        cur_G=G.Clone()
        #cur_G.lines[3].dots[1] = 1
        cur_G.WorkDir()
        cur_G.FindSubgraphs()
#        if not CheckNodes(cur_G):
#            print "%s has nodes with type <> 1 "%nickel
#            continue
        #G_s = StrechAllSubgraphs(cur_G)
#        G_r = feynman_reduce(G_s)
        F=rggrf.feynman.feynman2(cur_G)
        print F.internal_atoms_list
        print F.external_atoms_list
        print 
        
        A=L_dot_feynman2(cur_G)

        
        print nickel
        print 
        print "  F =  %s"%F
#        F.QForm()
#        print
#        print "F.B = ", F.B
#        print
#        print "F.D = ", F.D
#        print
#        print "F.E = ",F.E
#        print
#        print "GAMMAS = %s"%F.Gammas()
#        print 
#        print F.L_n()

#        print K_nR1_feynman(F)

#        print 
#        print "degree:", G_s.s_degree
#        print "type:",G_s.s_type
        
#        lines=dict()
        
