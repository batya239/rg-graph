#! /usr/bin/python
# ! encoding: utf8

__author__ = "kirienko"

# from IPython.parallel import Client
from ipyparallel import Client
import os, sys


def comm(diag):
    import os
    path = os.path.expanduser('~') + '/rg-graph/phi3/d_to_infty/'
    os.chdir(path)
    from config import abspath, loops, order, digits
    from maple import maple
    os.chdir(abspath + 'diags_%d_loops/ints/order_%d' % (loops, order))
    with open(diag) as fd:
        integrand = fd.read().strip()
    command = "evalf[%d](%s);" % (digits, integrand)
    res = maple(command, Digits=digits)
    with open("../../ans/order_%d/%s" % (order, diag), 'w') as fd:
        fd.write(res)
    # os.system(command)


if __name__ == "__main__":
    from config import abspath, loops, order, ipython_profile

    rc = Client(profile=ipython_profile)  # <-- ipcluster MUST be started at this moment
    # rc.block = True     # use synchronous computations (for direct view)
    print "Number of engines:", len(rc.ids)
    lview = rc.load_balanced_view()  # default load-balanced view

    diags = os.listdir('diags_%d_loops/ints/order_%d' % (loops, order))
    # cmd = ['maple -q < "%s" > %sdiags_%d_loops/order_%d/ans/%s' %
    #        (d, abspath, loops, order, d) for d in diags]
    # res = lview.map(comm, cmd, block=True)
    res = lview.map(comm, diags, block=True)
