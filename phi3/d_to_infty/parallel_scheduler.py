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
    print rc.ids
    lview = rc.load_balanced_view() # default load-balanced view
    abspath = os.path.expanduser('~')+'/rg-graph/phi3/d_to_infty/'
    diags = os.listdir('diags_%s_loops/nonzero'%loops)
    #cmd = ['python %sget_integrands_reference.py %s > %sdiags_%s_loops/ints/%s'%(abspath,d,abspath,loops,d) for d in diags]
    cmd = ['python %sget_integrands.py %s > %sdiags_%s_loops/ints/%s'%(abspath,d,abspath,loops,d) for d in diags]
    #cmd = ['echo %d'%rc.ids[i] for i in xrange(4)]
    print cmd
    lview.map(comm,cmd,block=True)
    #print res


