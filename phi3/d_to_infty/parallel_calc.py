#! /usr/bin/ipython
# ! encoding: utf8

__author__ = "kirienko"

from IPython.parallel import Client
import os


def comm(command):
    import os
    path = os.path.expanduser('~') + '/rg-graph/phi3/d_to_infty/'
    os.chdir(path)
    os.system(command)


def diags_from_static(path_to_nonzero):
    """
    :param path_to_nonzero: path to files with name `static_diag` which contain dynamic diagrams list
    :return: list of diagrams by listing `nonzero` directory
    """
    static_diags = os.listdir(path_to_nonzero)
    dyn_diags = []
    for sd in static_diags:
        with open(abspath + 'diags_%d_loops/nonzero/' % loops + sd) as fd:
            dyn_diags += [dd.strip() for dd in fd.readlines()]
    return dyn_diags


def diags_from_dynamic(path_to_dyn_diags):
    return [d.replace('-', '|') for d in os.listdir(path_to_dyn_diags)]


if __name__ == "__main__":
    try:
        from config import *
    except ImportError:
        print "ERROR: cannot import config.py"
        exit(1)

    rc = Client(profile=ipython_profile)  # <-- ipcluster MUST be started at this moment
    print "Number of engines:", len(rc.ids)
    lview = rc.load_balanced_view()  # default load-balanced view
    abspath = os.path.expanduser('~') + '/rg-graph/phi3/d_to_infty/'
    diags = diags_from_static('diags_%s_loops/nonzero' % loops)

    # TODO: skip diagram if already existed
    output_path = '%sdiags_%d_loops/ints/order_%d/' % (abspath, loops, order)   # + 'short/'
    cmd = ['python %scalc.py "%s" > %s%s' % (abspath, d, output_path, d.replace('|', '-')) for d in diags]
    print "The first 3 cmd-s:"
    for j in range(3): print cmd[j]
    # lview.map(comm,cmd,block=True)
    lview.map(comm, cmd, block=False)
