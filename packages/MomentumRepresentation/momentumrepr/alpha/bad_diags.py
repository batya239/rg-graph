import graph_util_mr
import time_versions
import graphine
import itertools
import uv
import configure_mr
import momentum_enumeration
import polynomial
from collections import namedtuple
from rggraphutil import emptyListDict, zeroDict
from rggraphenv import symbolic_functions
from cache import cached_function
from polynomial.multiindex import MultiIndex, CONST
from polynomial.polynomial import Polynomial

__author__ = 'dima'

AlphaRepresentationPolynomials = namedtuple("AlphaRepresentationPolynomials", ["c", "d"])
SubGraphInfo = namedtuple("SubGraphInfo", ["idx", "alpha_params", "loops_count", "edges", "divergence", "regulizer"])

no_tadpoles = graphine.filters.no_tadpoles
one_irreducible = graphine.filters.one_irreducible
configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.cln(2) * symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(1300000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-10).\
    with_integration_algorithm("suave").\
    with_debug(False).configure()
__author__ = 'dima'

# graphs = list()
# graphs.append("e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA|0a|")
# graphs.append("e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA|0a|")
# graphs.append("e12|23|4|e5|55||:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|23|4|e5|55||:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|23|4|e5|55||:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||")
# graphs.append("e12|23|4|e5|55||:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||")
# graphs.append("e12|33|44|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|34|5|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|34|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|Aa|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|aA|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|35|e|55||:0A_aA_aA|aA_Aa|aA_aA|0a|Aa_Aa||")
# graphs.append("e12|e3|34|5|55||:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA||")
# graphs.append("e12|e3|44|55|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA||")
# graphs.append("e12|e3|45|45|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa||")
# graphs = map(lambda g: g + ":::::", graphs)
# #
graphs = list()
graphs.append("e12|e3|45|46|e|66||:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|0A|Aa_Aa||")
graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_Aa|aA_aA|aA_Aa|0a|aA_aA||")
graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|0a|aA_aA||")
graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_aA|aA_aA|aA_Aa|0a|aA_aA||")
graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_aA|aA_Aa|aA_aA|0a|Aa_Aa||")
graphs.append("e12|e3|45|46|e|66||:0a_Aa_Aa|0a_Aa|Aa_aA|Aa_Aa|0A|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||")
graphs.append("e12|e3|34|5|e6|66||:0a_aA_Aa|0a_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_aA|0A_aA|aA_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_aA|0A_aA|Aa_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_aA|aA_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||")
graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_aA|Aa_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0a_aA_Aa|0a_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0A_aA|Aa_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_Aa|aA_aA|Aa|0a_aA|Aa_Aa||")
graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_Aa|aA_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0A_aA|Aa_Aa|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|Aa|Aa|0A|")
graphs.append("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_aA|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa|aA|0a|")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|Aa_aA|0a_aA|0a_Aa|aA||")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|aA_aA|0a_Aa|0a_aA|Aa||")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|aA_aA|0a_Aa|0a_Aa|Aa||")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|Aa_aA|aA_aA|0a_Aa|0a_Aa|aA||")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|Aa_aA|aA_aA|0a_Aa|0a_Aa|Aa||")
graphs.append("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_aA||")
graphs.append("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_aA|Aa|0A_aA|0a_aA||")
graphs.append("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_Aa|Aa|0A_aA|0a_Aa||")
graphs.append("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|0a_Aa||")
graphs.append("e12|33|45|6|e6|e6||:0a_aA_Aa|aA_aA|Aa_aA|aA|0A_aA|0a_Aa||")
graphs.append("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_Aa||")
graphs.append("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_aA|Aa|0A_aA|0a_Aa||")
graphs.append("e12|33|45|6|e6|e6||:0a_Aa_aA|Aa_Aa|Aa_aA|Aa|0A_aA|0a_Aa||")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_aA|aA_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA|Aa|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA|Aa|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_aA|Aa_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_aA|aA_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_Aa|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_aA|Aa_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa|aA|0a|")
graphs.append("e12|e3|e4|45|6|66||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa|aA_aA||")
graphs.append("e12|e3|e4|45|6|66||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa|aA_aA||")
graphs.append("e12|e3|e4|45|6|66||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA|Aa_Aa||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_aA|0a_Aa||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|0a_aA||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_aA||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|Aa|0a_Aa|0a_aA||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|0a_Aa||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_Aa||")
graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|aA_aA|Aa_aA|0a|0a|")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_aA|Aa_Aa|0A|0a|")
graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA_aA|0a|0a|")
graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA_aA|0a|0a|")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_aA|Aa_aA|0A|0a|")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_aA|aA_Aa|aA|Aa_aA|Aa_aA|0A|0a|")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_aA|Aa|Aa_aA|Aa_aA|0A|0a|")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_Aa|Aa_aA|0A|0a|")
graphs.append("e12|e3|e4|55|66|6||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA_aA|Aa||")
graphs.append("e12|e3|e4|55|66|6||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa_Aa|aA||")
graphs.append("e12|e3|e4|55|66|6||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa_Aa|aA||")
graphs.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|Aa|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|aA_aA|aA|aA_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA|Aa_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|aA_Aa|Aa|0A|")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|Aa_Aa|Aa|0A|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|aA_aA|aA|Aa_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|aA|aA_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|aA_Aa|Aa|0A|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|aA|Aa_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|Aa_Aa|Aa|0A|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA|Aa|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA|aA_aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|Aa_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|aA|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|Aa|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|aA_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|aA|Aa|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|Aa|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|aA|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|Aa|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|Aa|0a|")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_Aa|Aa|0a_Aa|0A_aA|Aa_Aa||")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|0a_Aa|aA_aA||")
graphs.append("e12|23|4|e5|e6|66||:0A_aA_aA|Aa_aA|aA|0a_aA|0a_Aa|aA_aA||")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_aA|Aa|0a_Aa|0A_aA|Aa_Aa||")
graphs.append("e12|23|4|e5|e6|66||:0A_aA_aA|Aa_aA|aA|0a_Aa|0a_aA|Aa_Aa||")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_aA|aA_Aa|aA|0A_aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|e4|56|56|6||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA_aA|Aa||")
graphs.append("e12|e3|e4|56|56|6||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa_Aa|Aa||")
graphs.append("e12|e3|e4|56|56|6||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa_Aa|Aa||")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|Aa|0a_Aa|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|aA_Aa|Aa|0A_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|Aa_Aa|Aa|0A_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|Aa|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_Aa|aA_aA|aA|0a_Aa|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|aA|0A_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|Aa|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_Aa|aA|0a_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|aA_Aa|aA|0A_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|Aa|0A_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|Aa|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|aA|0A_aA|Aa|0a|")
graphs.append("e12|e3|44|55|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|Aa|0a|")
graphs.append("e12|e3|44|55|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|44|55|6|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs = map(lambda g: g + ":::::", graphs)


class AlphaParameter(object):
    CURRENT_FEYNMAN_PARAMETER_IDX = -1

    def __init__(self, idx, letter="u"):
        self._idx = idx
        self._letter = letter

    @staticmethod
    def reset():
        AlphaParameter.CURRENT_FEYNMAN_PARAMETER_IDX = -1

    @staticmethod
    def next():
        AlphaParameter.CURRENT_FEYNMAN_PARAMETER_IDX += 1
        return AlphaParameter(AlphaParameter.CURRENT_FEYNMAN_PARAMETER_IDX)

    @staticmethod
    def external():
        return AlphaParameter(0)

    def as_var(self):
        return symbolic_functions.var(str(self))

    def __hash__(self):
        return hash(self._idx) + 37 * hash(self._letter)

    def __cmp__(self, other):
        return cmp((self._letter, self._idx), (other._letter, other._idx))

    def __str__(self):
        return (self._letter + "%s") % self._idx

    __repr__ = __str__


def check(graph):
    for g in time_versions.find_time_versions(graph):
        if not _check(g):
            return False
    return True

def _check(graph):
    import feyn_representation
    graph = feyn_representation.introduce_feynman_parameters(graph)
    graph, sub_graph_infos = feyn_representation.find_sub_graphs_info(graph)
    edge_cs = time_versions.find_edges_cross_sections(graph)

    later = False
    for sg in sub_graph_infos:
        if sg.divergence == 2:
            later = True
            break
    if not later:
        return True

    all_sg_alphas = reduce(lambda s, sg: s| sg.alpha_params, sub_graph_infos, set())
    for cs in edge_cs:
        cs_alphas = set(map(lambda e: e.alpha_param,cs))

        if len(cs_alphas & all_sg_alphas) == 0:
            continue
        cs_alphas1 = cs_alphas
        for sg in sub_graph_infos:
            if len(cs_alphas & sg.alpha_params):
                cs_alphas1 = cs_alphas1 & sg.alpha_params
                if len(cs_alphas1) == 0:
                    return False
    return True

def is_bad(graphs):
    for g in graphs:
        g = graph_util_mr.from_str_alpha(g)
        if check(g):
            pass
            print "OK", g
        else:
            print "BADDD", g


is_bad(graphs)




