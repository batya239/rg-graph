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
        Loops = sys.argv[1]
    except IndexError:
        print "usage:\n\t$ python %s number_of_loops" % os.path.relpath(sys.argv[0])
        # exit(1)
        Loops = 2
    rc = Client() # <-- ipcluster MUST be started at this moment
    print rc.ids
    lview = rc.load_balanced_view() # default load-balanced view
    abspath = os.path.expanduser('~')+'/rg-graph/phi3/d_to_infty/'
    diags = os.listdir('diags_%s_loops/nonzero'%Loops)
    cmd = ['python %sintegrand_maple.py %s > %sdiags_%s_loops/ints/%s'%(abspath,d,abspath,loops,d) for d in diags]
    #cmd = ['echo %d'%rc.ids[i] for i in xrange(4)]
    print cmd
    lview.map(comm,cmd,block=True)
    #print res


