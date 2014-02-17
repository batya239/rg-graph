__author__ = 'gleb'

from pole_extractor import diagram_calculator
from pole_extractor import utils

# calculating via 2-, 3-tailed diagrams
# first check that we have all base diagrams we need

need_p2 = utils.tau_differentiate(utils.get_diagrams(tails=2, loops=3), no_tails=True)
need_p0 = utils.get_diagrams(tails=4, loops=3)

print need_p2
print need_p0