__author__ = 'Gleb Dovzhenko <dovjenko.g@gmail.com>'

from pole_extractor import diagram_calculator, utils

need_p0 = utils.get_diagrams(tails=3, loops=4)

for i, (d, c) in list(enumerate(need_p0))[0:-1:2]:
    v = diagram_calculator.get_expansion(d, False, False)[-1]
    if abs(v.s) / abs(v.n) > 1E-4:
        print '(' + str(i + 1) + '/' + str(len(need_p0)) + ')'
        diagram_calculator.calculate_diagram(label=d,
                                             theory=3,
                                             max_eps=-1,
                                             zero_momenta=True,
                                             force_update=False)