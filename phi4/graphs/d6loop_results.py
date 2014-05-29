#!/usr/bin/python
import collections
import os
import re

from rggraphenv.symbolic_functions import e, tgamma, series, Order
from graph_state_builder_static import gs_builder
import graphine
import sys
from symmetry_coefficient import symmetry_coefficient

def C6(lambdas_, n):
    if isinstance(lambdas_, int):
        lambdas = [1]*lambdas_
    else:
        lambdas = lambdas_

    res = tgamma(sum(lambdas) - 3 * n + n * e) * tgamma(4 - 2 * e) ** n / tgamma(e - 1) ** n / tgamma(2 - e) ** (2 * n) / (-6 * e) ** n
    for lambd in lambdas:
        if lambd != 0:
            res = res / tgamma(lambd)
    return res


def C6m(lambdas_, n):
    if isinstance(lambdas_, int):
        lambdas = [1]*lambdas_
    else:
        lambdas = lambdas_
    d = 6-2*e
    res = tgamma(sum(lambdas) - 3 * n + n * e)/((8/d *tgamma(e)/tgamma(3)-1/d*tgamma(e+1)/tgamma(4)-2*tgamma(e)/tgamma(3) )/2 * (-6 * e)) ** n
    for lambd in lambdas:
        if lambd != 0:
            res = res / tgamma(lambd)
    return res


def C6s(lambdas_, n):
    if isinstance(lambdas_, int):
        lambdas = [1]*lambdas_
    else:
        lambdas = lambdas_
    d = 6-2*e
    res = tgamma(sum(lambdas) - 3 * n + n * e)
    for lambd in lambdas:
        if lambd != 0:
            res = res / tgamma(lambd)
    return res

def C6g(lambdas_,n):
    return C6s(lambdas_,n)*tgamma(3-e)**n/2**n

Cn = C6s



graph = graphine.Graph(gs_builder.graph_state_from_str(sys.argv[1]))

loops = graph.loops_count
alpha = len(graph.internal_edges)
if graph.internal_edges_count == 2:
    alpha += 1

graph_dir = "d6loop/%s" % graph

_FILENAME_REGEXP = re.compile(".*_(\d+)_V(\d+)_E(.+)\.run.res")
_EXPR_REGEXP = re.compile(".* =(.*)$")

result_files = os.listdir(graph_dir)
result = collections.defaultdict(lambda: 0)
error = collections.defaultdict(lambda: 0)

max_eps_power = -100000
for result_file in result_files:
    regex_result = _FILENAME_REGEXP.match(result_file)
    if regex_result:
        n, v, eps_power = map(int, regex_result.groups())
        data = open(os.path.join(graph_dir, result_file)).readlines()[-4:]
        regex_result1 = _EXPR_REGEXP.match(data[0])
        regex_result2 = _EXPR_REGEXP.match(data[1])
        if eps_power > max_eps_power:
            max_eps_power = eps_power
            #       print
            #       print data
        result[eps_power] += float(regex_result1.groups()[0])
        error[eps_power] += float(regex_result2.groups()[0])

print result
print error
if len(sys.argv) > 2:
    max_eps_power = int(sys.argv[2])

expr = reduce(lambda x, y: x + y, map(lambda x: x[1] * e ** x[0], result.items()))
expr += Order(e**(max(result.keys())+1))
#print series(expr*tgamma(alpha - loops*(1-e))/(e*g11)**loops,e,0,max_eps_power).evalf()
if alpha - loops * 2 <= 0:
    max_eps_power -= 1
print (alpha - loops * (3 - e)).expand()
final = series(expr * Cn(alpha,loops), e, 0, max_eps_power + 1).evalf()
print final
print "Gleb:", series(expr*C6g(alpha, loops)*symmetry_coefficient(graph.to_graph_state()),e,0,max_eps_power+1).evalf()
print "Gleb:", series(expr*C6g(alpha, loops),e,0,max_eps_power+1).evalf()

results = {

}
if str(graph) in results:
    print
    print results[str(graph)]
    print series((results[str(graph)] - final), e, 0, max_eps_power+1 ).expand()