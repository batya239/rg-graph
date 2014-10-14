#!/usr/bin/python
import collections
import os
import re

from rggraphenv.symbolic_functions import e, tgamma, series
from graph_state_builder_static import gs_builder
import graphine
import sys
from uncertSeries import Series



def C4_G(lambdas_, n):
    if isinstance(lambdas_, int):
        lambdas = [1]*lambdas_
    else:
        lambdas = lambdas_
    res = tgamma(sum(lambdas) - (2 - e )* n)/(tgamma(e)*e*tgamma(1-e)**2/tgamma(2-2*e))**n
    for lambd in lambdas:
        if lambd != 0:
            res = res / tgamma(lambd)
    return res



Cn = C4_G

graph = graphine.Graph(gs_builder.graph_state_from_str(sys.argv[1]))

loops = graph.loops_count
alpha = graph.internal_edges_count


graph_dir = "sd6loop_massless/%s" % graph

_FILENAME_REGEXP = re.compile(".*_(\d+)_V(\d+)_E(.+)\.run.res")
_EXPR_REGEXP = re.compile(".* =(.*)$")

result_files = os.listdir(graph_dir)
result = collections.defaultdict(lambda: 0)
error = collections.defaultdict(lambda: 0)

max_eps_power = -100000
# res_series = Series(name='e')
res_dict = dict()
for result_file in result_files:

    regex_result = _FILENAME_REGEXP.match(result_file)
    if regex_result:
        n, v, eps_power = map(int, regex_result.groups())
        data = open(os.path.join(graph_dir, result_file)).readlines()[-4:]
        regex_result1 = _EXPR_REGEXP.match(data[0])
        regex_result2 = _EXPR_REGEXP.match(data[1])
        if eps_power > max_eps_power:
            max_eps_power = eps_power
        result[eps_power] += float(regex_result1.groups()[0])
        error[eps_power] += float(regex_result2.groups()[0])**2
        if eps_power not in res_dict:
            res_dict[eps_power]=list()
        res_dict[eps_power].append((float(regex_result1.groups()[0]), float(regex_result2.groups()[0])))
        # res_series += Series(n=max_eps_power,d={eps_power:(float(regex_result1.groups()[0]), float(regex_result2.groups()[0]))})
        # print eps_power, max_eps_power, Series(n=max_eps_power,d={eps_power:(float(regex_result1.groups()[0]), float(regex_result2.groups()[0]))}, name='e')
        # print res_series

res_series = Series(n=max_eps_power+1, name='e')
for eps_power in res_dict:
    for term in res_dict[eps_power]:
        res_series += Series(n=max_eps_power+1, d={eps_power: term}, name='e')

print "--"
print res_series.pprint()
print res_series



print result
for eps in error:
    error[eps]=error[eps]**0.5
print error

min_power = min(res_series.gSeries)


expr = reduce(lambda x, y: x + y, map(lambda x: x[1] * e ** x[0], result.items()))
final = series(expr * Cn(alpha, loops), e, 0, max_eps_power).evalf()

a1 = series(Cn(alpha, loops), e, 0, max_eps_power-(min_power), remove_order=True).evalf()
c_dict = dict()
for x in range(-5, max_eps_power-min_power):
    if float(a1.coeff(e,x))==0:
        continue
    else:
        c_dict[x]=(float(a1.coeff(e,x)),0)

c_series = Series(max_eps_power-min_power, c_dict, name='e')

print
print c_series*res_series
print final
results = {

}
if str(graph) in results:
    print
    print results[str(graph)]
    print series((results[str(graph)] - final), e, 0, max_eps_power + 1).expand()
