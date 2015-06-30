__author__ = 'dima'

from rggraphenv import symbolic_functions

unit = symbolic_functions.CLN_ONE
two = symbolic_functions.CLN_TWO
e = symbolic_functions.e
pi = symbolic_functions.Pi
d = symbolic_functions.cln(4) - e
cln = symbolic_functions.cln
ln = symbolic_functions.log

G = symbolic_functions.tgamma(unit + e / two) / (symbolic_functions.cln(4) * pi) ** (d / two)

def M1(a, b, c):
    raise NotImplementedError()

def M2(a, c):
    ln43 = ln(cln(4) / cln(3))
    return unit / (cln(4) * e) * ((two * c - cln(3) * a) / e * a ** (unit - e) + a * c * (unit + ln43) - 3 * a ** 2 * (unit + ln43 / two) + c ** 2 / cln(3))

I301 = -cln(3)/8/e/e*(2+e+e*ln(cln(4)/3))
print "I301", I301.subs(e == 2 * e).series(e == 0, 0).evalf()

I202 = unit/4/e/e*(2 - e + e * ln(cln(4)/3))
print "I202", I202.subs(e == 2 * e).series(e == 0, 0).evalf()

I301 = -cln(3)/8/e/e*(2 + e + e * ln(cln(4)/3))
print "I301", I301.subs(e == 2 * e).series(e == 0, 0).evalf()