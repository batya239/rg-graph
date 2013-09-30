#!/usr/bin/python
__author__ = 'gleb'

from pole_extractor import adjacency_combinatorics
from pole_extractor import feynman_construction as fc
from pole_extractor import feynman_operations as f_o
from pole_extractor import expansion_calculation as ec
from pole_extractor import gamma
import itertools
import copy

# SET UP YOUR VARIABLES HERE
# Setting up initial data: connectivity list of a diagram we are interested in,
# number of loops in this diagram and model (3 for phi^3 and 4 for phi^4 diagrams).
# max_eps is maximal degree in resulting epsilon expansion
NLabel = 'ee11-22-ee-'
model = 4
max_eps = 4
# If you don't want to calculate the whole diagram, but only a few sectors, you can set them up here in
# sectors variable. If you want the program to generate all possible sectors for you and calculate the whole diagram,
# make it an empty list: sectors = [].
# Remember that Feynman's parameters are enumerated same as edges in Nickel's label.
sectors = []

# AND DO NOT CHANGE THIS PART
g_info = adjacency_combinatorics.graph_info(NLabel)
feynman_repr = fc.feynman_representation(g_info, PHI_EXPONENT=model,momentum_derivative=False)
print 'phi^' + str(model) + ' diagram ' + g_info['nickel label'] + '\n' + 'Feynman representation:'
print '[||' + str(feynman_repr['gamma arguments'][0]) + '+(' + str(feynman_repr['gamma arguments'][1]) + '*eps)||*||' + \
      str(feynman_repr['gamma arguments'][2]) + '+(' + str(feynman_repr['gamma arguments'][3]) + '*eps)||^' + \
      str(g_info['loops']) + ']*' + str(feynman_repr['integrand']) + '*DELTA[1-' + str(feynman_repr['d-func argument'])\
      + "]"

subgraph_combinations = adjacency_combinatorics.shrink_relevant_subgraphs(g_info['nickel label'], model)
print '\n' + '+++++++++ R\' OPERATION +++++++++'
print '\n' + 'R\' counterterms:'
for relevant_sg in subgraph_combinations:
    sg_str = ''
    for sg in relevant_sg[0]:
        sg_str += '(' + str(sg)[:-2] + ') * '
    print sg_str + str(relevant_sg[1])[:-2]

decomposed_diagram_info = f_o.decompose_integrand(feynman_repr, g_info, wanted_sectors=sectors)
print '\n' + '+++++++++ SECTOR DECOMPOSITION +++++++++'
print '\n' + 'Sectors:' + '\n'
for sec, rep in zip(decomposed_diagram_info['sectors'], decomposed_diagram_info['sector expressions']):
    print str(sec[1]) + " * " + str(sec[0]) + ":"
    print str(rep)
#    print f_o.rename_sector_vars(rep, sec[1])
    print

print '\n' + '+++++++++ EPS EXPANSION +++++++++' + '\n'
expansions = []
for rep in decomposed_diagram_info['sector expressions']:
    expansion = ec.extract_eps_poles(rep, max_eps)
    print '#' + str(rep) + ":"
    for k in sorted(expansion.keys()):
        print 'eps^{' + str(k) + '}:'
        for element in expansion[k]:
            out = ""
            out += str(element[0]) + '*('
            for logarithm in element[1]:
                out += str(logarithm)
                out += ' + '
            out = out[:-3]
            out += ')'
            print out
        print
    print
    expansions.append(copy.deepcopy(expansion))

print '+++++++++ NUMERICAL INTEGRATION +++++++++' + '\n'

numeric_expansion = dict()
for rep, e in zip(decomposed_diagram_info['sector expressions'], expansions):
    print '#' + str(rep) + ":"
    current_expansion = ec.compute_exp_via_CUBA(e)
    for k in sorted(current_expansion.keys()):
        print 'eps^{' + str(k) + '}:' + '\n' + str(current_expansion[k][0]) + \
              ' +- ' + str(current_expansion[k][1]) + '\n'
        if k not in numeric_expansion.keys():
            numeric_expansion[k] = [0.0, 0.0]
        numeric_expansion[k][0] += current_expansion[k][0]
        numeric_expansion[k][1] += current_expansion[k][1]

print '+++++++++ FINAL RESULT +++++++++' + '\n'
print 'Momentum integral calculated via Feynman\'s interpretation:'
for k in sorted(numeric_expansion.keys()):
    print 'eps^{' + str(k) + '}:'
    print str(numeric_expansion[k][0]) + " +- " + str(numeric_expansion[k][1])
    print
diag_expansion = ec.NumEpsExpansion(numeric_expansion)
g1_expansion = ec.NumEpsExpansion(gamma.get_gamma(feynman_repr['gamma arguments'][0],
                                                  feynman_repr['gamma arguments'][1], max_eps))
g2_expansion = ec.NumEpsExpansion(gamma.get_gamma(feynman_repr['gamma arguments'][2],
                                                  feynman_repr['gamma arguments'][3], max_eps))
g2_coefficient = copy.deepcopy(g2_expansion)
for _ in itertools.repeat(None, g_info['loops'] - 1):
    g2_coefficient = g2_expansion * g2_coefficient

result_expansion = diag_expansion * g1_expansion * g2_coefficient
print 'Whole diagram with Gamma-function poles:'
for k in sorted(result_expansion.keys()):
    print 'eps^{' + str(k) + '}:'
    print str(result_expansion[k][0]) + " +- " + str(result_expansion[k][1])
    print