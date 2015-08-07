#! /usr/bin/python
#! encoding: utf8

__author__ = "kirienko"

import os, sys

loop = sys.argv[1].split('-')[1][0]
with open(sys.argv[1]) as source:
    diags = [l.strip() for l in source.readlines()]

for i,d in enumerate(diags):
    #sys.stdout.write("\r%d of %d" % (i,len(diags)))
    #sys.stdout.flush()
    #sys.sleep(1)
    cmd = "pypy spine.py '%s' %s > diags_%s_loops/%s"%(d, loop, loop, d.replace('|','-'))
    print "%d of %d:"%(i+1,len(diags)),cmd
    os.system(cmd)
#sys.stdout("\n")
