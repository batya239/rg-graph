__author__ = 'gleb'

from pole_extractor import diagram_calculator
from pole_extractor import utils

# calculating via 2-, 3-tailed diagrams
# first check that we have all base diagrams we need

# so there must be a check that we have every diagram we need for R'

need_p2 = utils.get_diagrams(tails=2, loops=4)

need_p0 = need_p2 + utils.get_diagrams(tails=3, loops=4)

for i, diag in enumerate(need_p0):
    #if not diagram_calculator.is_present(diag[0], rprime=False, momentum_derivative=False):
    if i >= 69:
        print '(' + str(i + 1) + '/' + str(len(need_p0)) + ')'
        diagram_calculator.calculate_diagram(label=diag[0],
                                             theory=3,
                                             max_eps=-1,
                                             zero_momenta=True,
                                             force_update=False)


for i, diag in enumerate(need_p2):
    #if not diagram_calculator.is_present(diag[0], rprime=False, momentum_derivative=True):
        print '(' + str(i + 1) + '/' + str(len(need_p2)) + ')'
        diagram_calculator.calculate_diagram(label=diag[0],
                                             theory=3,
                                             max_eps=-1,
                                             zero_momenta=False,
                                             force_update=False)

for diag in need_p0:
    diagram_calculator.calculate_rprime(diag[0],
                                        PHI_EXPONENT=3,
                                        force_update=True,
                                        verbose=2)