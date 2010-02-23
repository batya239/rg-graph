#!/usr/bin/python
# -*- coding: utf8

import sys
import subprocess
import rggraph_static as rggrf
from phi3 import *
import re as regex

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

if "-prefix" in sys.argv:
    prefix = sys.argv[sys.argv.index('-prefix')+1]
else:
    prefix = "MCO_f"

if "-points" in sys.argv:
    npoints = eval(sys.argv[sys.argv.index('-points')+1])
else:
    npoints = 10000

if "-threads" in sys.argv:
    nthreads = eval(sys.argv[sys.argv.index('-threads')+1])
else:
    nthreads = 2

process = subprocess.Popen(["ls %s*"%prefix,], shell=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
exit_code = process.wait()
(std_out,std_err) = process.communicate()
if exit_code <> 0 :
    raise Exception, "ls returned error code %s"%exit_code

t_exec_dict = FindExecutables(std_out, prefix)
if len(t_exec_dict)>1:
    raise ValueError, "found more then one set of executables: %s " %t_exe_dict.keys()

prog_names = t_exec_dict[t_exec_dict.keys()[0]]


res = rggrf.integration.CalculateEpsilonSeries(prog_names, points=npoints, threads=nthreads)
print res
#print "симметрийный коэффициент: %s" %(G.sym_coeff)

#print "With Sd: %s" %ResultWithSd(res, NLOOPS, n_epsilon_series)

print "Old Notation: %s" % ResultOldNotation(res)