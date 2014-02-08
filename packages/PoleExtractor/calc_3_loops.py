__author__ = 'gleb'

from pole_extractor import diagram_calculator
from pole_extractor import utils

# calculating via 2-, 3-tailed diagrams
# first check that we have all base diagrams we need

need_p2 = utils.tau_differentiate(utils.tau_differentiate(utils.get_diagrams(tails=2, loops=1),
                                                          no_tails=True), no_tails=True)
need_p2 += utils.tau_differentiate(utils.get_diagrams(tails=2, loops=2), no_tails=True)

missing = ''
for diag in need_p2:
    if not diagram_calculator.is_present(diag[0], rprime=False, momentum_derivative=True):
        missing += str(diag[0]) + '~p^2\n'

need_p0 = utils.get_diagrams(tails=5, loops=1) + utils.get_diagrams(tails=4, loops=2)

for diag in need_p0:
    if not diagram_calculator.is_present(diag[0], rprime=False, momentum_derivative=False):
        missing += str(diag[0]) + '\n'

if missing:
    raise EnvironmentError('Missing diagrams:\n' + missing)

need_p2 = utils.get_diagrams(tails=2, loops=3)
need_p0 = need_p2 + utils.get_diagrams(tails=3, loops=3)
"""
for diag in need_p0:
    diagram_calculator.calculate_diagram(label=diag[0],
                                         theory=3,
                                         max_eps=3,
                                         zero_momenta=True,
                                         verbose=2,
                                         force_update=False)

for diag in need_p2:
    diagram_calculator.calculate_diagram(label=diag[0],
                                         theory=3,
                                         max_eps=3,
                                         zero_momenta=False,
                                         verbose=2,
                                         force_update=False)
"""
for diag in need_p0:
    diagram_calculator.calculate_rprime(diag[0],
                                        PHI_EXPONENT=3,
                                        force_update=True,
                                        verbose=2)
    print