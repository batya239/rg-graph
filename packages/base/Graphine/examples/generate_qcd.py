#!/usr/bin/python
"""
QCD generation example for 1-loop 2-fermion legs bubbles with labeled legs.

run script:
   $ python generate_qcd.py

Expected output:
e11|e|:0A_AA_AA|1A| 1/2
e11|e|:0A_Ff_fF|1A| 1
e11|e|:0A_Gg_gG|1A| 1

This output means 3 graphs where 'f' and 'F are fermion fields, 'g' anf 'G' are ghost fields,
'A' - boson field. The number next to graph is symmetries coefficient.
"""
__author__ = 'dima'


from graphine.generator import topology
from graphine.generator import diagram_generator
from graphine.generator import sym_coef

for gs in topology.get_topologies({3: 2},
                                  external_nodes_count=2,
                                  with_tadpoles=False,
                                  is_one_particle_irreducible=True):
    for _g in diagram_generator.generate_fields(gs,
                                         possible_fields=["fF", "AA", "gG"],
                                         possible_external_fields="AA",
                                         possible_vertices=["fFA", "gGA", "AAA", "AAAA"],
                                         ignore_cycles=True,
                                         unlabeled_legs=False):
        print _g, sym_coef.symmetry_coefficient(_g)
