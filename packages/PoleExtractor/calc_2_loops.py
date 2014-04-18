__author__ = 'gleb'

from pole_extractor import diagram_calculator, utils

CLEAR = False

# calculating via 2-, 3-tailed diagrams

need_p2 = utils.get_diagrams(tails=2, loops=2)
need_p0 = need_p2 + utils.get_diagrams(tails=3, loops=2)

if CLEAR:
    map(lambda x: diagram_calculator.clear(x[0], rprime=False, momentum_derivative=True), need_p2)
    map(lambda x: diagram_calculator.clear(x[0], rprime=False, momentum_derivative=False), need_p0)
    map(lambda x: diagram_calculator.clear(x[0], rprime=True, momentum_derivative=True), need_p2)
    map(lambda x: diagram_calculator.clear(x[0], rprime=True, momentum_derivative=False), need_p0)
    utils.clear_log()

for diag in need_p0:
    diagram_calculator.calculate_diagram(label=diag[0],
                                         theory=3,
                                         max_eps=4,
                                         zero_momenta=True,
                                         force_update=False)

for diag in need_p2:
    diagram_calculator.calculate_diagram(label=diag[0],
                                         theory=3,
                                         max_eps=4,
                                         zero_momenta=False,
                                         force_update=False)

for diag in need_p0:
    diagram_calculator.calculate_rprime(diag[0],
                                        PHI_EXPONENT=3,
                                        force_update=True,
                                        verbose=2)
    print