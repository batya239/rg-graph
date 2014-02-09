__author__ = 'gleb'

from pole_extractor import diagram_calculator as dc

lls_p2 = ('e12|34|34||e|', 'e12|23|4|e4||', 'e12|3|44|e4||', 'e12|e3|4|44||', 'e12|e3|34|4||')
lls = ('e12|e3|e4|45|5|e|', 'e12|e3|45|45|e|e|', 'e12|e3|34|5|e5|e|', 'e12|e3|e4|e5|55||')

for l in lls_p2:
    dc.calculate_diagram(label=l,
                         theory=3,
                         max_eps=4,
                         zero_momenta=False,
                         verbose=2,
                         force_update=False)

for l in lls:
    dc.calculate_diagram(label=l,
                         theory=3,
                         max_eps=4,
                         zero_momenta=True,
                         verbose=2,
                         force_update=False)