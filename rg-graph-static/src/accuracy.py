#!/usr/bin/python
# -*- coding:utf8
import sys
import sympy 
import rggraph_static as rggrf
model = None

def usage(progname):
    return "%s -model phi3R [-absolute N] [-relative N] [-graph str_nickel]"

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
    
if "-absolute" in sys.argv:
    absolute = float(sys.argv[sys.argv.index('-absolute')+1])
else:
    absolute = 0.00001

if "-relative" in sys.argv:
    relative = float(sys.argv[sys.argv.index('-relative')+1])
else:
    relative = 0.01
    
if "-target" in sys.argv:
    target = int(sys.argv[sys.argv.index('-target')+1])
else:
    target = model.target

if "-graph" in sys.argv:
    g_list = [sys.argv[sys.argv.index('-graph')+1],]
else:
    g_list = model.GraphList()

if "-debug" in sys.argv:
    debug = True
else:
    debug = False

    
eps = sympy.var('eps')

#print phi3.name
for file in g_list:
        #print "--- %s"%file,
        G = model.LoadGraph(file)
        G.DefineNodes({})
        G.GenerateNickel()
        G.LoadResults('eps')
        (res,a_ratio,r_ratio)=G.CheckAccuracy(absolute, relative)
        if not res:
            if debug:
                print "(%s/%s) "%((g_list.index(file)+1),len(g_list)),
            print file , 
            if debug:
                print "absolute_ratio = %s , relative_ratio = %s"%(a_ratio,r_ratio)
            else:
                print

        