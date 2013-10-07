#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'

import phi4.symbolic_functions
from phi4.symbolic_functions import G, e, l
import sys


def I(n1, n2, n3, n4, n5):
    results = {
        #(2, 1, 1, 0, 1): G(2, 1 + e) * G(1, 1),
        #(1, 2, 1, 1, 0): G(1 + e, 2) * G(1, 1),
    }
    if isinstance(n3, int) and isinstance(n4, int) and isinstance(n5, int):

        if n3 == 0:
            return G(n1, n2) * G(n4, n5)
        if n4 == 0:
            return G(n3, n5) * G(n1, n2 + n3 + n5 - l - 1)
        if n5 == 0:
            return G(n3, n4) * G(n2, n1 + n3 + n4 - l - 1)
        if (n1, n2, n3, n4, n5) in results:
            return results[(n1, n2, n3, n4, n5)]
        if 0 in (n1, n2, n3, n4, n5):
            raise NotImplementedError("%s" % str((n1, n2, n3, n4, n5)))

        return 1 / (4 - 2 * e - n1 - n2 - 2 * n3) * (
            n1 * (I(n1 + 1, n2, n3 - 1, n4, n5) - I(n1 + 1, n2, n3, n4 - 1, n5)) + n2 * (
                I(n1, n2 + 1, n3 - 1, n4, n5) - I(n1, n2 + 1, n3, n4, n5 - 1)))
    else:
        if isinstance(n1, int) and isinstance(n2, int) and isinstance(n3, int):
            return I(n4, n5, n3, n1, n2)
        else:
            raise NotImplementedError("%s" % str((n1, n2, n3, n4, n5)))


n = 3
print I(1, 1, 1, 1, 1).series(e == 0, n).evalf()
print I(1 + e, 1, 1, 1, 1).series(e == 0, n).evalf()
print I(e, 2, 1, 1, 1).series(e == 0, n).evalf()
print I(e, 1, 2, 1, 1).series(e == 0, n).evalf()
print

qi1 = (1 + e) * (G(2 + e, 1) * G(1, 1) - G(1, 1) * G(2 + e, 2 - l)) + (
    G(1 + e, 2) * G(1, 1) - G(1, 1) * G(2, 2 - l + e))
i1 = qi1 / (4 - 2 * e - (1 + e) - 1 - 2)
print i1.series(e == 0, n).evalf()

qi2 = e * (G(1, 1) * G(2, 1 + e) - G(1, 1) * G(1 + e, 3 - l)) + 2 * (G(e, 3) * G(1, 1) - G(1, 1) * G(3, 1 - l + e))
i2 = qi2 / (4 - 2 * e - e - 2 - 2)

print i2.series(e == 0, n).evalf()


#qi0 = e * (i1 - G(1, 2) * G(3 - l, 1 + e)) + (i2 - G(2, 1) * G(4 - l, e))
qi0 = e * (i1 - G(1, 2) * G(3 - l, 1 + e)) + (i2 - G(2, 1) * G(3 - 2*l, 2))
i0 = qi0 / (4 - 2 * e - e - 1 - 4)
print i0.series(e == 0, n).evalf()

I = i0 * G(1, 1)
I_series = I.series(e == 0, n)
print I_series.evalf()
#(-0.5)*e**(-3)+4.25*e**(-2)+(-17.375)*e**(-1)+Order(1)
ISE = I_series.evalf()
