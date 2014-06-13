#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

"""
Convert legacy *func*.c files into CIntegrate input" \
"""

import os, sys, re

try:
    inPath  = sys.argv[1]
except IndexError:
    print "inPath is not set, use '.'"
    inPath  = '.'
try:
    maxeval = sys.argv[2] ## <-- number of Monte Carlo points
except IndexError:
    print "'maxeval' is not set, use 1M"
    maxeval = '1000000'
try:
    epsrel = sys.argv[3] ## <-- number of Monte Carlo points
except IndexError:
    print "'epsrel' is not set, use 1.E-06"
    epsrel = '1.E-06'

integrator = 'suaveCuba' ## 'vegasCuba', 'cuhreCuba', 'divonneCuba', 'suaveCuba'

funcs = [f for f in os.listdir(inPath) if os.path.isfile(os.path.join(inPath, f)) and '__func_' in f]

pat_interm_func = re.compile("^double func" + "[0-9].*")
pat_var = re.compile(".*double u" + "[0-9].*")

def pow_replace(txt):
    """ replaces pow(...) --> p[...] """
    while 'pow' in txt: ## <-- for nested power expressions
        pows = re.findall('pow\(.*?\)',txt)
        for elem in pows:
            txt = txt.replace(elem, 'p['+elem[4:-1]+']')
    return txt.replace(';','').strip()

def make_cintegrate_input(f):
    #print(f)
    with open(f, 'r') as data:
        lines = data.readlines()
    intermediate = {} ## intermediate functions f[1], f[2], ...
    number_of_func = 0
    number_of_vars = 0
    ## Searching for sectors
    for line in lines:
        if pat_interm_func.match(line):
            intermediate['f[%d]' % (number_of_func+1)] = ''
            vars = []
            number_of_vars = 0
        ## Searching for vars in a sector
        if pat_var.match(line):
            vars.append(line.strip().split()[1])
            number_of_vars +=1

        if "coreExpr = " in line:
            coreExpr = line.strip().split('=')[1]
            ## Substituting vars
            for j,var in enumerate(vars):
                coreExpr = coreExpr.replace(var,'x[%d]'%(j+1))#+number_of_vars-len(vars)))
            ## Substituting 'power' brackets
            intermediate['f[%d]' % (number_of_func+1)] += pow_replace(coreExpr)
        if "f += coreExpr" in line:
            ## symmetry number
            intermediate['f[%d]' % (number_of_func+1)] += ' *'+line.strip().split('*')[1]
            number_of_func += 1
    with open(f.replace('.c','.int'),'w') as out_file:
        out_file.write("SetIntegrator\n%s\n"%integrator)
        out_file.write("SetCurrentIntegratorParameter\nmaxeval\n%s\n"%maxeval)
        out_file.write("SetCurrentIntegratorParameter\nepsrel\n%s\n"%epsrel)
        out_file.write("CubaCores\n8\n")
        out_file.write("GetCurrentIntegratorParameters\n")
        out_file.write("Integrate\n%d;\n%d;\n" %(number_of_vars,len(intermediate)))
        for i in intermediate:
            out_file.write(intermediate[i]+'\n')
        out_file.write('+'.join(intermediate.keys())+';\n')
        out_file.write('|\nExit')

if __name__ == '__main__':
    #diag = 'e111-e-_O__func_0_E0.c'    ## <-- '-0.019105958'
    #diag = 'e112-22-e-_O__func_0_E0.c'  ## <-- '-0.019674801'
    for diag in funcs:
        make_cintegrate_input(diag)