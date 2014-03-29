__author__ = 'gleb'

from pole_extractor import utils
from pole_extractor import diagram_calculator

need_p2 = utils.get_diagrams(tails=2, loops=2) + utils.get_diagrams(tails=2, loops=3)
need_p0 = need_p2 + utils.get_diagrams(tails=3, loops=2) + utils.get_diagrams(tails=3, loops=3)

for diag in need_p0:
    if diagram_calculator.is_present(diag[0], rprime=False, momentum_derivative=False):
        d1 = diagram_calculator.calculate_diagram(label=diag[0],
                                                  theory=3,
                                                  max_eps=3,
                                                  zero_momenta=True,
                                                  force_update=False)
        d2 = diagram_calculator.get_expansion(diag[0], rprime=False, momentum_derivative=False)
        print '#####\n' + str(d1)
        print d2
        print str(d1.cut(2) == d2.cut(2)) + '\n#####'

for diag in need_p2:
    if diagram_calculator.is_present(diag[0], rprime=False, momentum_derivative=True):
        d1 = diagram_calculator.calculate_diagram(label=diag[0],
                                                  theory=3,
                                                  max_eps=3,
                                                  zero_momenta=False,
                                                  force_update=False)
        d2 = diagram_calculator.get_expansion(diag[0], rprime=False, momentum_derivative=True)
        print '#####\n' + str(d1)
        print d2
        print str(d1.cut(2) == d2.cut(2)) + '\n#####'

