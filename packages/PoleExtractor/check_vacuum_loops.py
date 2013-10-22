__author__ = 'gleb'

import pole_extractor.feynman as feynman
import graphine
import pole_extractor.expansion
import pole_extractor.numcalc


# made from '111--'
two_loops_ee = ((6.0, 'e12-23-3-e-'), (6.0, 'e12-e3-33--'))
two_loops_eee = ((36.0, 'e12-e3-34-4-e-'), (18.0, 'e12-e3-e4-44--'), (6.0, 'e12-34-34-e-e-'))

# made from '112-3-33--'
three_loops_ee1 = ((8.0, 'e12-e3-34-5-55--'), (4.0, 'e12-34-35-e-55--'), (16.0, 'e12-23-4-e5-55--'),
                  (8.0, 'e12-23-4-45-5-e-'), (2.0, 'e12-33-44-5-5-e-'), (4.0, 'e12-e3-44-55-5--'))
three_loops_eee1 = ((24.0, 'e12-e3-e4-45-6-66--'), (24.0, 'e12-e3-45-46-e-66--'), (48.0, 'e12-e3-34-5-e6-66--'),
                   (48.0, 'e12-e3-34-5-56-6-e-'), (24.0, 'e12-33-45-6-e6-e6--'), (24.0, 'e12-23-4-56-56-e-e-'),
                   (48.0, 'e12-e3-44-56-5-6-e-'), (24.0, 'e12-23-4-e5-e6-66--'), (48.0, 'e12-23-4-e5-56-6-e-'),
                   (12.0, 'e12-e3-e4-55-66-6--'), (12.0, 'e12-e3-44-55-6-6-e-'))

# made from '123-23-3--'
three_loops_ee2 = ((12.0, 'e12-e3-45-45-5--'), (24.0, 'e12-34-35-4-5-e-'), (6.0, 'e12-34-34-5-5-e-'))
three_loops_eee2 = ((36.0, 'e12-e3-e4-56-56-6--'), (144.0, 'e12-e3-45-46-5-6-e-'), (36.0, 'e12-e3-45-45-6-6-e-'),
                    (24.0, 'e12-34-56-e5-e6-6--'), (72.0, 'e12-34-35-6-e5-6-e-'), (24.0, 'e12-34-35-6-e6-e6--'))


def calc_expansion(label):
    g = graphine.Graph.fromStr(label)
    f = feynman.Feynman(g, theory=3)

    sectors = feynman.sectors(g, conservation_laws=f._conslaws, symmetries=True)
    decomposed = map(lambda x: f.sector_decomposition(x), sectors)
    expansions = map(lambda x: pole_extractor.expansion.extract_poles(x._integrand, 5), decomposed)

    num_expansion = pole_extractor.numcalc.NumEpsExpansion()
    for e in expansions:
        num_expansion += pole_extractor.numcalc.CUBA_calculate(e)

    g_coef = pole_extractor.numcalc.get_gamma(f._gamma_coef2[0], f._gamma_coef2[1], 5)
    g_coef = g_coef ** (f._gamma_coef2[2])
    g_coef *= pole_extractor.numcalc.get_gamma(f._gamma_coef1[0], f._gamma_coef1[1], 5)
    g_coef *= float(f._inverse_coefficient) ** (-1)
    result = g_coef * num_expansion

    return result


m1 = pole_extractor.numcalc.NumEpsExpansion({0: [6.0, 0.0], 1: [-10.0, 0.0], 2: [4.0, 0.0], 3: [0.0, 0.0],
                                             4: [0.0, 0.0], 5: [0.0, 0.0]})
m2 = pole_extractor.numcalc.NumEpsExpansion({0: [6.0, 0.0], 1: [-22.0, 0.0], 2: [24.0, 0.0], 3: [-8.0, 0.0],
                                             4: [0.0, 0.0], 5: [0.0, 0.0]})
m3 = pole_extractor.numcalc.NumEpsExpansion({0: [6.0, 0.0], 1: [-15.0, 0.0], 2: [9.0, 0.0], 3: [0.0, 0.0],
                                             4: [0.0, 0.0], 5: [0.0, 0.0]})
m4 = pole_extractor.numcalc.NumEpsExpansion({0: [6.0, 0.0], 1: [-33.0, 0.0], 2: [54.0, 0.0], 3: [-27.0, 0.0],
                                             4: [0.0, 0.0], 5: [0.0, 0.0]})
"""
print sum(map(lambda x: calc_expansion(x[1]) * x[0], two_loops_ee), pole_extractor.numcalc.NumEpsExpansion())
print calc_expansion('111--') * m1
print

print sum(map(lambda x: calc_expansion(x[1]) * x[0], two_loops_eee), pole_extractor.numcalc.NumEpsExpansion())
print calc_expansion('111--') * m2
print

print sum(map(lambda x: calc_expansion(x[1]) * x[0], three_loops_ee1), pole_extractor.numcalc.NumEpsExpansion())
print calc_expansion('112-3-33--') * m3
print

print sum(map(lambda x: calc_expansion(x[1]) * x[0], three_loops_eee1), pole_extractor.numcalc.NumEpsExpansion())
print calc_expansion('112-3-33--') * m4
print

print sum(map(lambda x: calc_expansion(x[1]) * x[0], three_loops_ee2), pole_extractor.numcalc.NumEpsExpansion())
print calc_expansion('123-23-3--') * m3
print

print sum(map(lambda x: calc_expansion(x[1]) * x[0], three_loops_eee2), pole_extractor.numcalc.NumEpsExpansion())
print calc_expansion('123-23-3--') * m4
print
"""

for label in three_loops_ee1:
    print label[1]
    print calc_expansion(label[1])
print '###'
for label in three_loops_eee1:
    print label[1]
    print calc_expansion(label[1])
print '###'
for label in three_loops_ee2:
    print label[1]
    print calc_expansion(label[1])
print '###'
for label in three_loops_eee2:
    print label[1]
    print calc_expansion(label[1])
