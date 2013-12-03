__author__ = 'gleb'

import pole_extractor.diagram_calculator as dc


test_labels = ('e111-e-', 'ee11-22-ee-', 'ee12-e22-e-',
               'e112-22-e-', 'ee11-22-33-ee-', 'ee11-23-e33-e-',
               'ee12-ee3-333--', 'ee12-e33-e33--', 'e112-e3-e33-e-',
               'ee12-e23-33-e-', 'e123-e23-e3-e-', 'ee12-223-3-ee-')
big_label = 'e12-e3-44-56-7-68-8-e8--'

labels2tails = ('e12-e3-33--', 'e12-23-3-e-')
labels3tails = ('111--', 'e12-e3-e4-44--', 'e12-e3-34-4-e-', 'e12-34-34-e-e-')


for l in labels2tails:
    dc.calculate_diagram(label=l,
                         theory=3,
                         max_eps=5,
                         zero_momenta=False,
                         verbose=2)
    print

for l in labels3tails:
    dc.calculate_diagram(label=l,
                         theory=3,
                         max_eps=5,
                         zero_momenta=True,
                         verbose=2)