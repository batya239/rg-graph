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

for f in funcs:
    print(f)
    with open(f, 'r') as data:
        lines = data.readlines()
    intermediate = {} ## intermediate functions
    ## Searching for sectors
    j = 0
    for line in lines:
        if pat_interm_func.match(line):
            # print(line)
            intermediate['f%d' % j] = [0,'']
            vars = []
        if pat_var.match(line):
            # print(line)
            vars.append(int(line.strip().split()[1][1:]))

        if "coreExpr = " in line:
            # print(line)
            # print("Vars:",vars)
            intermediate['f%d' % j] = [vars,line.strip().split('=')[1]]
            j += 1
    print(intermediate)
    ## Searching for vars in a sector
    ## Substituting vars
    ## Substituting 'power' brackets

## Generating outputs
