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



#print green
#print model.name
G_list = rggrf.graph.LoadFromGRC(grc,model)
for G in G_list:
    G.GenerateNickel()
    G.green = green
    rggrf.utils.print_debug("%s, %s" %(G.nickel, G.sym_coeff),debug)
    G.Save(overwrite=True)
    
    

    