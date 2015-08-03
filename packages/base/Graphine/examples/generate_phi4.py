#!/usr/bin/python
"""
$\phi^4$ generation example for 3-loop 4-legs diagrams

run script:
   $ python generate_phi4.py

Expected output:
ee11|22|33|ee| 3/8
ee11|23|e33|e| 3/2
ee12|ee3|333|| 1/2
ee12|e23|33|e| 6
ee12|e33|e33|| 3/2
ee12|223|3|ee| 3/4
e112|e3|e33|e| 3/2
e123|e23|e3|e| 1

The number next to graph means symmetries coefficient.
"""
__author__ = 'dima'


from graphine.generator import topology
from graphine.generator import sym_coef

for g in topology.get_topologies(valencies_to_num_nodes={4: 4},
                                 external_nodes_count=4,
                                 with_tadpoles=False,
                                 is_one_particle_irreducible=True):
    print g, sym_coef.symmetry_coefficient(g)
