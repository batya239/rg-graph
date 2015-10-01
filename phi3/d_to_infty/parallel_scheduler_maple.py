#! /usr/bin/python
#! encoding: utf8

__author__ = "kirienko"

from IPython.parallel import Client
import os, sys

def comm(command):
    import os
    from config import abspath, loops
    os.chdir(abspath+'diags_%d_loops/ints/' % loops)
    os.system(command)

if  __name__ == "__main__":
    rc = Client()       # <-- ipcluster MUST be started at this moment
    #rc.block = True     # use synchronous computations (for direct view)
    print rc.ids
    lview = rc.load_balanced_view() # default load-balanced view
    from config import abspath, loops
    diags = os.listdir('diags_%d_loops/ints' % loops)
    cmd = ['maple -q < "%s" > %sdiags_%d_loops/ans/%s'%(d,abspath,loops,d) for d in diags]
    print cmd
    res = lview.map(comm,cmd,block=True)
    #res = lview.map(comm,cmd)
    #print res
    #import time
    #while not res.ready():
    #    time.sleep(1)
    #    print res.progress

