#! /usr/bin/ipython
#! encoding: utf8

__author__ = "kirienko"

from IPython.parallel import Client
import os, sys

def comm(command):
    import os
    path = os.path.expanduser('~')+'/rg-graph/phi3/d_to_infty/'
    os.chdir(path)
    os.system(command)

if  __name__ == "__main__":
    try: 
        from config import *
    except ImportError:
        print "ERROR: cannot import config.py"
        exit(1)

    rc = Client() # <-- ipcluster MUST be started at this moment
    print "Number of engines:",len(rc.ids)
    lview = rc.load_balanced_view() # default load-balanced view
    abspath = os.path.expanduser('~')+'/rg-graph/phi3/d_to_infty/'
    static_diags = os.listdir('diags_%s_loops/nonzero'%loops)
    dyn_diags = []
    for d in static_diags:
        with open(abspath + 'diags_%d_loops/nonzero/'%loops + d) as fd:
            dyn_diags += [dd.strip() for dd in fd.readlines()]
    cmd = ['python %sget_integrands.py "%s" > %sdiags_%s_loops/ints/%s' \
                % (abspath,d,abspath,loops,d.replace('|','-')) for d in dyn_diags]
    print "The first 3 cmd-s:"
    for j in range(3): print cmd[j]
    lview.map(comm,cmd,block=True)


