__author__ = 'gleb'

from pole_extractor import utils
from pole_extractor import diagram_calculator

p2 = utils.get_diagrams(tails=2, loops=2)

for diag, coef in p2:
    print diagram_calculator.calculate_diagram_w_symmetries(diag, 3, 4)