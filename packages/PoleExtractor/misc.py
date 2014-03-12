__author__ = 'gleb'

from pole_extractor import utils
from pole_extractor import diagram_calculator
from pole_extractor import reduced_vl
from pole_extractor import feynman

import graphine

p2 = utils.get_diagrams(tails=2, loops=3)

for diag, coef in p2:
    #rvl = reduced_vl.ReducedVacuumLoop.fromGraphineGraph(diag, zero_momenta=False)
    #print '\n'.join(map(lambda x: str(x), feynman.FeynmanIntegrand.fromRVL_w_symmetries(rvl, 3)))
    #print feynman.FeynmanIntegrand.fromRVL(rvl, 3)
    #print
    e = diagram_calculator.calculate_p2_w_symmetries(diag, 3, 4)
    e_ = diagram_calculator.calculate_diagram(diag, 3, 4, False, False)
    print '#####\n' + str(e) + '\n' + str(e_) + '\n' + str(e.cut(5) == e_.cut(5)) + '\n#####'