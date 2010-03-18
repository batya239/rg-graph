#!/usr/bin/python
# -*- coding:utf8
model = None
import sys

import rggraph_static as rggrf

def usage(progname):
    return "%s -grc out.grf -green G2 -model phi3R [-debug]"

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

if "-grc" in sys.argv:
    grc = sys.argv[sys.argv.index('-grc')+1]
else:
    print "Usage : %s " %usage(sys.argv[0])
    sys.exit(1)

if "-green" in sys.argv:
    green = sys.argv[sys.argv.index('-green')+1]
else:
    print "Usage : %s " %usage(sys.argv[0])
    sys.exit(1)
    
if "-debug" in sys.argv:
    debug = True
else:
    debug = False



print green
print model.name
G_list = rggrf.graph.LoadFromGRC(grc,model)
for G in G_list:
    G.GenerateNickel()
    G.green = green
    rggrf.utils.print_debug("%s, %s" %(G.nickel, G.sym_coeff),debug)
    G.Save(overwrite=True)
    
    
#G=G_list[0]
#for idx in G.__dict__:
#    print idx, G.__dict__[idx].__class__.__name__ , G.__dict__[idx]
    
#print G.__dict__['lines'][1]
#lines = {}
#map(lambda k,v: lines.update({k: str(v)}),G.lines.keys(),G.lines.values())
#print lines
#print G._ToDict() 
#
#G = rggrf.Graph(phi3)
#G.LoadLinesFromFile(filename)
#G.DefineNodes({})
#G.GenerateNickel()
#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).nickel
#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).edges
#print G.sym_coeff

    