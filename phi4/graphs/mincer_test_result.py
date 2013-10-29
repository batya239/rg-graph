#!/usr/bin/python
import collections
import os
import re

from phi4.symbolic_functions import e, tgamma, series

import graphine
import sys

graph = graphine.Graph.fromStr(sys.argv[1])

loops = graph.getLoopsCount()
alpha = len(graph.internalEdges())

graph_dir = "sample_extraction/%s" % graph

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
#print error
g11 = tgamma(e) * tgamma(-e + 1) ** 2 / tgamma(-2 * e + 2)
expr = reduce(lambda x, y: x + y, map(lambda x: x[1] * e ** x[0], result.items()))
#print series(expr*tgamma(alpha - loops*(1-e))/(e*g11)**loops,e,0,max_eps_power).evalf()
if alpha - loops * 2 <= 0:
    max_eps_power -= 1
print (alpha - loops * (2 - e)).expand()
final = series(expr * tgamma(alpha - loops * (2 - e)) / (e * g11) ** loops, e, 0, max_eps_power + 1).evalf()
print final

results = {
    'e11-e-::': 1 / e,
    'e112-2-e-::': 0.5 * e ** (-2) + 0.5 * e ** (-1) + 1.5 + 0.8938292905212171433 * e + 5.0233747388210952802 * e ** 2 + 3.0355504618527611193 * e ** 3 + 19.881646498182317079 * e ** 4+12.096918018576493531*e**5+ 79.53720161336304073*e**6,
    'e112-e2--::': (-0.5)*e**(-2)+0.5*e**(-1)+(-0.5000000000000000001)+2.1061707094787828563*e+(-3.2357161577786609941)*e**2+7.0111990157894294494*e**3+(-13.8105455744767948445)*e**4+27.666374977788140557*e**5+(-55.34336557621005371)*e**6,
    'e12-23-3-e-::': 7.2123414189575657126 - (4.683773734514887159) * e - (21.549990225248099193) * e ** 3 + (24.069147509221048373) * e ** 2,
    'e12-223-3-e-::': 3.276265548078106665+0.3333333333333333333/e**3+0.3333333333333333333/e**2+0.3333333333333333333/e-9.14747181594392599*e+38.35479100795094758* e**2-121.8709485789786307*e**3,
    'e12-e23-33--::': (-0.033333333333333333335)*e**(-2)+(-0.10555555555555555556)*e**(-1)+(-0.08888888888888888884)+0.084855825076363301824*e+0.26377745322552894935*e**2+0.29878072202252724067*e**3+0.21433389572441654735*e**4+0.10929928599756573176*e**5+0.03901335072699244663*e**6,
    'e12-23-34-4-e-::': 20.7385551028674 - 37.866830505981674 * e
}
if str(graph) in results:
    print
    print results[str(graph)]
    print series((results[str(graph)] - final), e, 0, max_eps_power + 1).expand()