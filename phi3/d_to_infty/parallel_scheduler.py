#! /usr/bin/ipython
#! encoding: utf8

__author__ = "kirienko"

from ipyparallel import Client
from os import system, listdir, mkdir
from os.path import exists, expanduser
from os.path import join as pjoin

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
    abspath = pjoin(expanduser('~'), 'rg-graph', 'phi3', 'd_to_infty')
    diags = listdir(pjoin('diags_%s_loops'%loops, 'nonzero'))
    ints_dir = pjoin(abspath, 'diags_%s_loops'%loops, 'ints')
    if not exists(ints_dir):
        mkdir(ints_dir)
        print "Created: %s" % ints_dir
    ints_order_dir = pjoin(ints_dir, 'order_%d' % order)
    if not exists(ints_order_dir):
        mkdir(ints_order_dir)
        print "Created: %s"%ints_order_dir
    cmd = ['python %s %s > %s' % 
            (pjoin(abspath,'get_integrands.py'), d, 
            pjoin(ints_order_dir, d)) 
            for d in diags]
    print "First 3 commands:"
    for i in xrange(3):
        print cmd[i]
    lview.map(comm, cmd)


