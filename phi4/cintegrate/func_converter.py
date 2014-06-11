#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

"""
Convert legacy *func*.c files into CIntegrate input" \
"""

"""
out_0_e111-e-_cuhre_50M_e-8_e-12
СUHRE RESULT:   -0.01910595770373 +- 0.00000000010177   p = 0.000

out_0_e112-22-e-_cuhre_50M_1e-8_1e-12:
CUHRE RESULT:	-0.01967480121018 +- 0.00000000019595	p = 0.000
"""

import os, sys, re
import string as s

inPath = sys.argv[1]
funcs = [f for f in os.listdir(inPath) if os.path.isfile(os.path.join(inPath, f)) and '_func_' in f]

pat_interm_func = re.compile("^double func" + "[0-9].*")
pat_var = re.compile(".*double u" + "[0-9].*")

def pow_replace(txt):
    """ replaces pow(...) --> p[...] """
    pows = re.findall('pow\(.*?\)',txt)
    for elem in pows:
        txt = txt.replace(elem, 'p['+elem[4:-1]+']')
    return txt.replace(';','')


def make_cintegrate_input(f):
    print(f)
    with open(f, 'r') as data:
        lines = data.readlines()
    intermediate = {} ## intermediate functions
    ## Searching for sectors
    i = 0
    for line in lines:
        if pat_interm_func.match(line):
            #print(line)
            intermediate['f%d' % i] = ''
            #print(intermediate)
            vars = []
        ## Searching for vars in a sector
        if pat_var.match(line):
            vars.append(line.strip().split()[1])

        if "coreExpr = " in line:
            coreExpr = line.strip().split('=')[1]
            ## Substituting vars
            for j,var in enumerate(vars):
                coreExpr = coreExpr.replace(var,'x[%d]'%(j+1))
            ## Substituting 'power' brackets
            intermediate['f%d' % i] += pow_replace(coreExpr)
            i += 1
    print(intermediate)

for f in funcs:
    make_cintegrate_input(f)

