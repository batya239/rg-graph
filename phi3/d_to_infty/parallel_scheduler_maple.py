#! /usr/bin/python
# ! encoding: utf8

__author__ = "kirienko"

from IPython.parallel import Client
# from ipyparallel import Client
from random import shuffle
import os


def comm(diag):
    import os
    path = os.path.expanduser('~') + '/rg-graph/phi3/d_to_infty/'
    os.chdir(path)
    from config import abspath, loops, order, digits
    from maple import maple
    os.chdir(abspath + 'diags_%d_loops/ints/order_%d/short/' % (loops, order))
    with open(diag) as fd:
        integrand = fd.read().strip()
    # find closing bracket ']':
    for j in xrange(-1,-10,-1):
        if integrand[j] == ']':
            integrand = integrand[:j+1] + ',numeric,method=_CubaCuhre,epsilon=1e-%d'%(digits-1) + integrand[j+1:]
    command = "evalf[%d](%s);" % (digits, integrand)
    # command = "eval(%s);" % (integrand.replace('Int','int'))
    maple('_EnvIntMaxPoints = 10000000000:')
    res = maple(command, Digits=digits)
    with open(abspath+"diags_%d_loops/ans/order_%d/short/%s" % (loops, order, diag), 'w') as fd:
        fd.write(res)


if __name__ == "__main__":
    from config import abspath, loops, order, ipython_profile
    from minimal_diag_set_l3 import *

    rc = Client(profile=ipython_profile)  # <-- ipcluster MUST be started at this moment
    # rc.block = True     # use synchronous computations (for direct view)
    print "Number of engines:", len(rc.ids)
    lview = rc.load_balanced_view()  # default load-balanced view

    diags = os.listdir('diags_%d_loops/ints/order_%d/short/' % (loops, order))
    #diags = final
    
    # skip diagram if already existed
    path_to_diags = abspath+'diags_%d_loops/ans/order_%d/short/' % (loops, order)
    existed = os.listdir(path_to_diags)
    rest_diags = [d for d in diags if d.replace('|', '-') not in existed] 
    shuffle(rest_diags)
    if len(rest_diags) < len(diags):
        print "only %d diags to proceed" % len(rest_diags)
        diags = rest_diags

    # cmd = ['maple -q < "%s" > %sdiags_%d_loops/order_%d/ans/%s' %
    #        (d, abspath, loops, order, d) for d in diags]
    res = lview.map(comm, diags, block=True)
