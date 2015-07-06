

import graph_util_ms
import sector_decomposition
import feyn_repr
import polynomial
import time_versions
import configure_mr

from rggraphenv import symbolic_functions
configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.CLN_TWO * symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(20000000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-8).\
    with_integration_algorithm("suave").\
    with_debug(False).configure()

def get_sectors(v_substitutor, _d, graph):
    for u, subs in v_substitutor.iteritems():
        _d = _d.changeVarToPolynomial(u, subs)
    sectors = sector_decomposition.calculate_sectors(sector_decomposition.strategy_a, _d, graph)
    return sectors.get_all_sectors()

with open("p_4l_3t.txt") as f:
    for l in f:

        graph = graph_util_ms.from_str(l[:-1] + "::::")

        tvs = time_versions.find_time_versions(graph)
        # print "Time version count:", len(tvs)
        sec_len = list()
        for g in tvs:
            c, _d, c_tau, c_omega, v_substitutor, v_params, v_rate, tau_rate, _graph = feyn_repr.get_polynomials(g, p2=False)
            omega_c = polynomial.poly(map(lambda u: (1, u), c_omega))
            sectors = get_sectors(v_substitutor, _d, g)
            print g, len(sectors)