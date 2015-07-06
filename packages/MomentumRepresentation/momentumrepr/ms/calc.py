__author__ = 'dima'

import os
import uncertainties

logs = filter(lambda s: "log3l" in s, os.listdir("../"))
import sym_coef

import t_3_groups
full_ans = 0
for g in t_3_groups.get_all():
    sc = 1
    if not isinstance(g, list):
        sc = sym_coef.sc(g).evalf().to_double()
    found = False
    for f in logs:
        with open("../" + f) as ff:
            ff1 = [x for x in ff]
            for l in ff1:
                if l[:-1] == str(g):
                    line = ff1[ff1.index(l) + 2]
                    line = line[line.index("-1:") +3:]
                    try:
                        answer = uncertainties.ufloat(*eval(line[:line.index(",")].replace("+/-", ",")))
                    except:
                        answer = uncertainties.ufloat(*eval(line[:line.index("}")].replace("+/-", ",")))
                    full_ans += answer * sc
                    found = True
                    break
    assert found
    print g
print full_ans
# 0.020707+/-0.000004