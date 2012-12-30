#!/usr/bin/python

import topology
import nickel
import sys



valence = eval(sys.argv[1])
check_tadpoles = True

if len(sys.argv) > 2:
    if eval(sys.argv[2]):
        check_tadpoles = True
    else:
        check_tadpoles = False

topologies = [t for t in topology.GetTopologies(valence)]

for t in topologies:
    if check_tadpoles:
        if not topology.HasTadpole(nickel.Nickel(string=t).edges):
            print t
    else:
        print t


