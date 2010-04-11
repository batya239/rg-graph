#!/usr/bin/python
# -*- coding:utf8

model=None
import sys
import rggraph_static as rggrf

def usage(progname):
    return "%s -model phi3R [-overwrite] [-graph str_nickel] [-debug] [-target N]"

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

if "-overwrite" in sys.argv:
    overwrite = True
else:
    overwrite = False
    
if "-target" in sys.argv:
    model.target = int(sys.argv[sys.argv.index('-target')+1])


for file in g_list:
    rggrf.utils.print_debug(file, debug)
    G = model.LoadGraph(file)
    G.WorkDir()
    G.model = model
    for sub in G.subgraphs:
        sub.model = model

    G.Save(overwrite=overwrite)
    G.SaveAsPNG("graph.png")

#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).nickel
#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).edges
#print G.sym_coeff

    