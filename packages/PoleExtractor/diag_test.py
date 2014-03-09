__author__ = 'gleb'

import graphine

from pole_extractor import reduced_vl
from pole_extractor import feynman
from pole_extractor import numcalc
from pole_extractor import utils
from pole_extractor import diagram_calculator


"""
rvl = reduced_vl.ReducedVacuumLoop.fromGraphineGraph(graphine.Graph.fromStr('e12|e3|44|56|5|7|77||'), zero_momenta=True)
fi = feynman.FeynmanIntegrand.fromRVL(rvl, 3)
sec = fi.sector_decomposition((4, ((9, (5, 6, 7, 10, 11, 12)), (7, (5, 6, 10, 11, 12)), (5, (6, 11, 12)), (11, (12,)))))
print sec

expansion = feynman.extract_poles(sec._integrand, 4)
for k in sorted(expansion.keys()):
    print str(k) + ': ' + str(len(expansion[k])) + ' elements'

num_expansion = numcalc.parallel_cuba_calculate(expansion)
"""

need_p2 = utils.get_diagrams(tails=2, loops=2)
need_p0 = need_p2 + utils.get_diagrams(tails=3, loops=2)

for label, coef in need_p0:
    e = diagram_calculator.calculate_diagram(label=label,
                                             theory=3,
                                             max_eps=4,
                                             zero_momenta=True,
                                             force_update=False)
    e_ = diagram_calculator.get_expansion(label, False, False)
    print e
    print e_
    print e == e_.cut(5)