__author__ = 'gleb'

from pole_extractor import diagram_calculator as dc
from pole_extractor import utils


def print_exp(g, md):
    expansion = dc.get_expansion(g, rprime=False, momentum_derivative=md)
    print '{',
    for k in sorted(expansion.keys()):
        print str(k) + ': [' + str(expansion[k].n) + ', ' + str(expansion[k].s) + '],',
    print '}'


lls_p2 = utils.tau_differentiate(utils.get_diagrams(tails=2, loops=3), no_tails=True)
lls = utils.get_diagrams(tails=4, loops=3)

d = ('e12|3|45|46|e|66||::', 'e12|34|35|e|6|66||::', 'e12|34|35|e|56|6||::', 'e12|33|45|6|e6|6||::',
     'e12|23|4|e5|6|66||::', 'e12|23|4|e5|56|6||::', 'e12|3|34|5|66|e6||::', 'e12|3|34|5|e6|66||::',
     'e12|23|4|5|66|e6||::', 'e12|23|4|e5|66|6||::', 'e12|23|4|56|56||e|::', 'e12|23|4|5|56|6|e|::',
     'e12|23|4|45|6|e6||::', 'e12|e3|45|46||66||::', 'e12|e3|34|5|6|66||::', 'e12|e3|34|5|56|6||::',
     'e12|e3|4|45|6|66||::', 'e12|3|45|e4|6|66||::', 'e12|e3|44|56|5|6||::', 'e12|e3|4|55|66|6||::',
     'e12|e3|44|55|6|6||::', 'e12|3|44|e5|6|66||::', 'e12|33|45|6|5|6|e|::')


for l in lls_p2:
    if str(l[0]) not in d:
        dc.calculate_diagram(label=l[0],
                             theory=3,
                             max_eps=2,
                             zero_momenta=False,
                             verbose=0,
                             force_update=False)
    print l[0]
    print_exp(l[0], True)
    print

for l in lls:
    dc.calculate_diagram(label=l[0],
                         theory=3,
                         max_eps=2,
                         zero_momenta=True,
                         verbose=0,
                         force_update=False)
    print l[0]
    print_exp(l[0], False)
    print

