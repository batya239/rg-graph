__author__ = 'gleb'

from pole_extractor import diagram_calculator as dc


test_labels = ('e111-e-', 'ee11-22-ee-', 'ee12-e22-e-',
               'e112-22-e-', 'ee11-22-33-ee-', 'ee11-23-e33-e-',
               'ee12-ee3-333--', 'ee12-e33-e33--', 'e112-e3-e33-e-',
               'ee12-e23-33-e-', 'e123-e23-e3-e-', 'ee12-223-3-ee-')
big_label = 'e12-e3-44-56-7-68-8-e8--'

labels2tails = ('e12-e3-33--', 'e12-23-3-e-')
labels3tails = ('e12-e3-e4-44--', 'e12-e3-34-4-e-', 'e12-34-34-e-e-')

g0_3 = (('112-3-33--', 0.0625), ('123-23-3--', 1.0/24.0))

g2_3 = (('e12-23-4-45-5-e-', 0.5),  ('e12-34-35-e-55--', 0.25), ('e12-e3-44-55-5--', 0.25),
        ('e12-23-4-e5-55--', 1.0),  ('e12-e3-45-45-5--', 0.5),  ('e12-34-35-4-5-e-', 1.0),
        ('e12-34-34-5-5-e-', 0.25), ('e12-e3-34-5-55--', 0.5),  ('e12-33-44-5-5-e-', 0.125))

g3_3 = (('e12-e3-45-46-e-66--', 1.5),  ('e12-e3-34-5-e6-66--', 3.0),  ('e12-e3-45-45-6-6-e-', 1.5),
        ('e12-34-56-e5-e6-6--', 1.0),  ('e12-33-45-6-e6-e6--', 1.5),  ('e12-23-4-e5-56-6-e-', 3.0),
        ('e12-e3-e4-45-6-66--', 1.5),  ('e12-34-35-6-e6-e6--', 1.0),  ('e12-23-4-56-56-e-e-', 1.5),
        ('e12-e3-e4-55-66-6--', 0.75), ('e12-e3-44-56-5-6-e-', 3.0),  ('e12-e3-34-5-56-6-e-', 3.0),
        ('e12-e3-45-46-5-6-e-', 6.0),  ('e12-23-4-e5-e6-66--',  1.5), ('e12-e3-e4-56-56-6--', 1.5),
        ('e12-34-35-6-e5-6-e-', 3.0),  ('e12-e3-44-55-6-6-e-', 0.75))
"""
for l in g2_3:
    dc.calculate_diagram(label=l[0],
                         theory=3,
                         max_eps=2,
                         zero_momenta=False,
                         verbose=2,
                         force_update=True)
    dc.calculate_diagram(label=l[0],
                         theory=3,
                         max_eps=2,
                         zero_momenta=True,
                         verbose=2,
                         force_update=True)
    print
"""
for l in g0_3:
    dc.calculate_diagram(label=l[0],
                         theory=3,
                         max_eps=4,
                         zero_momenta=True,
                         verbose=2,
                         force_update=True)
