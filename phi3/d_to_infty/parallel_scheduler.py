#! /usr/bin/python
#! encoding: utf8

__author__ = "kirienko"

from IPython.parallel import Client
import os, sys

def comm(command):
    import os
    path = '/home/kirienko/rg-graph/phi3/d_to_infty/'
    os.chdir(path)
    os.system(command)

if  __name__ == "__main__":
    rc = Client() # <-- ipcluster MUST be started at this moment
    print rc.ids
    lview = rc.load_balanced_view() # default load-balanced view
    abspath = '/home/kirienko/rg-graph/phi3/d_to_infty/'
    diags = os.listdir('diags_4_loops/nonzero')
    cmd = ['python %sintegrand_maple.py %s > %sdiags_4_loops/ints/%s'%(abspath,d,abspath,d) for d in diags]
    #cmd = ['echo %d'%rc.ids[i] for i in xrange(4)]
    print cmd
    lview.map(comm,cmd,block=True)
    #print res


