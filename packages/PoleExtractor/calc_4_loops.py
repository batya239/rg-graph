__author__ = 'Gleb Dovzhenko <dovjenko.g@gmail.com>'

from pole_extractor import diagram_calculator, utils

# calculating via 2-, 3-tailed diagrams
# first check that we have all base diagrams we need

# so there must be a check that we have every diagram we need for R'

need_p2 = utils.get_diagrams(tails=2, loops=4)
need_p0 = need_p2 + utils.get_diagrams(tails=3, loops=4)
"""
for i, (d, c) in enumerate(need_p0):
    v = diagram_calculator.get_expansion(d, False, False)[-1]
    if abs(v.s) / abs(v.n) > 1E-4:
    #if not diagram_calculator.is_present(d, rprime=False, momentum_derivative=False):
        print '(' + str(i + 1) + '/' + str(len(need_p0)) + ')'
        diagram_calculator.calculate_diagram(label=d,
                                             theory=3,
                                             max_eps=-1,
                                             zero_momenta=True,
                                             force_update=False)
        #print (d, diagram_calculator.get_expansion(d, rprime=False, momentum_derivative=False).to_base_dict())
"""
for i, (d, c) in reversed(list(enumerate(need_p2))[:38]):
    v = diagram_calculator.get_expansion(d, False, True)[-1]
    if abs(v.s) / abs(v.n) > 1E-3:
    #if not diagram_calculator.is_present(d, rprime=False, momentum_derivative=True):
        print '(' + str(i + 1) + '/' + str(len(need_p2)) + ')'
    diagram_calculator.calculate_diagram(label=d, theory=3, max_eps=-1, zero_momenta=False, force_update=False)
        #print (d, diagram_calculator.get_expansion(d, rprime=False, momentum_derivative=True).to_base_dict())

for diag in need_p0:
    diagram_calculator.calculate_rprime(diag[0], theory=3, verbose=2, force_update=False)
