__author__ = 'Gleb Dovzhenko <dovjenko.g@gmail.com>'

from pole_extractor import diagram_calculator, utils

need_p2 = utils.get_diagrams(tails=2, loops=4)

for i, (d, c) in reversed(list(enumerate(need_p2))):
    v = diagram_calculator.get_expansion(d, False, True)[-1]
    if abs(v.s) / abs(v.n) > 1E-3:
        print '(' + str(i + 1) + '/' + str(len(need_p2)) + ')'
        diagram_calculator.calculate_diagram(label=d,
                                             theory=3,
                                             max_eps=-1,
                                             zero_momenta=False,
                                             force_update=False)