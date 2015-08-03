#!/usr/bin/python
"""
QED generation example for 2-loop 2-fermion legs diagrams.

run script:
   $ python generate_qed.py

Expected output:
e12|e3|33||:0A_Ff_fF|1A_Ff|AA_fF|| 1
e12|e3|33||:0A_fF_Ff|1A_fF|AA_Ff|| 1
e12|23|3|e|:0A_Ff_fF|AA_Ff|fF|1A| 1

This output means 3 graphs where 'f' and 'F are fermion fields,
'A' - boson field. The number next to graph is symmetries coefficient.
"""
__author__ = 'dima'


from graphine.generator import topology
from graphine.generator import diagram_generator
from graphine.generator import sym_coef

for gs in topology.get_topologies({3: 4}, external_nodes_count=2, with_tadpoles=False, is_one_particle_irreducible=True):
    for _g in diagram_generator.generate_fields(gs,
                                         possible_fields=["fF", "AA"],
                                         possible_external_fields="AA",
                                         possible_vertices=["fFA"],
                                         ignore_cycles=True,
                                         unlabeled_legs=False):
        print _g, sym_coef.symmetry_coefficient(_g)
