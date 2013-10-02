__author__ = 'gleb'

from pole_extractor import adjacency_combinatorics
from pole_extractor import feynman_construction as fc
from pole_extractor import feynman_operations as f_o
from pole_extractor import expansion_calculation as ec
from pole_extractor import gamma
import itertools
import copy


def calculate_expansion(diagram, model, max_eps, m_sq_derivative):
    """
    Calculates eps expansion of a diagram
    """
    g_info = adjacency_combinatorics.graph_info(diagram)
    feynman_repr = fc.feynman_representation(g_info, PHI_EXPONENT=model, momentum_derivative=m_sq_derivative)
    decomposed_diagram_info = f_o.decompose_integrand(feynman_repr, g_info)

    expansions = []
    for rep in decomposed_diagram_info['sector expressions']:
        expansions.append(copy.deepcopy(ec.extract_eps_poles(rep, max_eps)))

    numeric_expansion = dict()
    for rep, e in zip(decomposed_diagram_info['sector expressions'], expansions):
        current_expansion = ec.compute_exp_via_CUBA(e)
        for k in sorted(current_expansion.keys()):
            if k not in numeric_expansion.keys():
                numeric_expansion[k] = [0.0, 0.0]
            numeric_expansion[k][0] += current_expansion[k][0]
            numeric_expansion[k][1] += current_expansion[k][1]

    diag_expansion = ec.NumEpsExpansion(numeric_expansion)
    g1_expansion = ec.NumEpsExpansion(gamma.get_gamma(feynman_repr['gamma arguments'][0],
                                                      feynman_repr['gamma arguments'][1], max_eps))
    g2_expansion = ec.NumEpsExpansion(gamma.get_gamma(feynman_repr['gamma arguments'][2],
                                                      feynman_repr['gamma arguments'][3], max_eps))
    g2_coefficient = copy.deepcopy(g2_expansion)
    for _ in itertools.repeat(None, g_info['loops'] - 1):
        g2_coefficient = g2_expansion * g2_coefficient

    result_expansion = diag_expansion * g1_expansion * g2_coefficient

    return result_expansion


def set_expansion(NDiag, model, max_eps, m_sq_derivative):
    """

    """
    return