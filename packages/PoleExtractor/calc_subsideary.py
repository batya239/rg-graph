__author__ = 'gleb'

from pole_extractor import diagram_calculator
from pole_extractor import utils

# 2 loops for 3 loops
need_p2 = utils.tau_differentiate(utils.get_diagrams(2, 2), no_tails=True)
need_p0 = utils.get_diagrams(4, 2)

# 2 loops for 4 loops
need_p2 += utils.tau_differentiate(utils.tau_differentiate(utils.get_diagrams(2, 2), no_tails=True), no_tails=True)
need_p0 += utils.get_diagrams(5, 2)

# 3 loops for 4 loops
# ...

# vacuum loops
v_loops_2 = utils.get_diagrams(0, 2)
v_loops_3 = utils.get_diagrams(0, 3)
v_loops_4 = utils.get_diagrams(0, 4)

for diag in need_p0:
    if not diagram_calculator.is_present(diag[0], rprime=False, momentum_derivative=False):
        diagram_calculator.calculate_diagram(label=diag[0],
                                             theory=3,
                                             max_eps=4,
                                             zero_momenta=True,
                                             force_update=False)

for diag in need_p2:
    if not diagram_calculator.is_present(diag[0], rprime=False, momentum_derivative=True):
        diagram_calculator.calculate_diagram(label=diag[0],
                                             theory=3,
                                             max_eps=4,
                                             zero_momenta=False,
                                             force_update=False)