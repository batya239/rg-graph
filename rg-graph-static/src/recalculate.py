#!/usr/bin/python
# -*- coding: utf8

import sys
import subprocess
import rggraph_static as rggrf
import re as regex
import os

def FindExecutables(ls_out,prefix):
    res = dict()
    for line in ls_out.splitlines():
        reg = regex.match("^%s_(.+)_e(\d+)$"%prefix, line)
        if reg:
            if reg.groups()[0] in res:
                res[reg.groups()[0]].append(line)
            else:
                res[reg.groups()[0]] = [line,]
    return res

model = None

def usage(progname):
    return "%s -model phi3R [-graph str_nickel] [-absolute N] [-relative N] [-target] [-debug]"

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

if "-graph" in sys.argv:
    g_list = [sys.argv[sys.argv.index('-graph')+1],]
else:
    g_list = model.GraphList()
    
if "-debug" in sys.argv:
    debug = True
else:
    debug = False
    
if "-target" in sys.argv:
    model.target = int(sys.argv[sys.argv.index('-target')+1])
    
#if "-method" in sys.argv:
#    method = sys.argv[sys.argv.index('-method')+1]
#else:
#    method = None
    

#if "-timeout" in sys.argv:
#    timeout = float(sys.argv[sys.argv.index('-timeout')+1])
#else:
#    timeout = None
    
if "-points" in sys.argv:
    npoints = int(eval(sys.argv[sys.argv.index('-points')+1]))

else:
    npoints = None
    

if "-threads" in sys.argv:
    nthreads = eval(sys.argv[sys.argv.index('-threads')+1])
else:
    nthreads = 2

for nickel in g_list:
    G = rggrf.Graph(model)
    G.Load(nickel)
    G.GenerateNickel()
    G.LoadResults('eps')
    if not G.CheckAccuracy(absolute, relative):
        print G.nickel , " " , 
        if npoints == 0:
            if "npoints_r" in G.__dict__:
                G.npoints = int(G.npoints_r)
            else:
                G.npoints = 10000 
        elif npoints ==None:
            if "npoints_r" in G.__dict__:
                G.npoints = int(G.npoints_r)*10
            else:
                G.npoints = 10000
        else:
            G.npoints = npoints
        
        G.WorkDir()
    
        process = subprocess.Popen(["ls %s*"%G.method,], shell=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = process.wait()
        (std_out,std_err) = process.communicate()
        if exit_code <> 0 :
            raise Exception, "\"ls %s*\" returned error code %s"%(G.method,exit_code)
    
        t_exec_dict = FindExecutables(std_out, G.method)
        if len(t_exec_dict)>1:
            raise ValueError, "found more then one set of executables: %s " %t_exec_dict.keys()
    
        prog_names = t_exec_dict[t_exec_dict.keys()[0]]
    
    
        t_res = rggrf.integration.CalculateEpsilonSeries(prog_names, points=G.npoints, threads=nthreads, debug=debug)
    
        (G.r1_dot_gamma, G.r1_dot_gamma_err) = ResultWithSd(t_res, G.NLoops(), G.model.target - G.NLoops())
        rggrf.utils.print_debug( G.r1_dot_gamma, debug)
        
        G.SaveResults(['r1_dot_gamma','r1_dot_gamma_err','npoints','method'])
        print "OK ", G.r1_dot_gamma, G.r1_dot_gamma_err
        

#print "симметрийный коэффициент: %s" %(G.sym_coeff)

#print "With Sd: %s" %ResultWithSd(res, NLOOPS, n_epsilon_series)

#print "Old Notation: %s" % ResultOldNotation(res)