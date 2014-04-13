__author__ = 'gleb'

from pole_extractor import diagram_calculator
from pole_extractor import utils


def to_tex_str(expansion):
    result = '$'
    for k in sorted(expansion.keys()):
        result += '\epsilon^{' + str(k) + '} [' + str(expansion[k].n) + ' \pm ' + str(expansion[k].s) + '] + '
    return result[:-3] + '$'

need_p2 = utils.get_diagrams(tails=2, loops=2)
need_p0 = utils.get_diagrams(tails=3, loops=2)


for diag, coef in need_p2:
    print str(diag)[:-2] + ' & ' + str(coef) + ' & ' + \
          to_tex_str(diagram_calculator.get_expansion(diag, True, True).cut(0)) + ' \\\\'

for diag, coef in need_p0:
    print str(diag)[:-2] + ' & ' + str(coef) + ' & ' + \
          to_tex_str(diagram_calculator.get_expansion(diag, True, False).cut(0)) + ' \\\\'