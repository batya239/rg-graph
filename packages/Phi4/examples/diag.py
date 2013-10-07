#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'

import phi4.symbolic_functions
from phi4.symbolic_functions import G, e, l
qi1 = (1+e)*(G(2+e,1)*G(1,1)-G(1,1)*G(2+e,2-l)) + (G(1+e,2)*G(1,1)-G(1,1)*G(2,2-l+e))
i1 = qi1/(4-2*e-(1+e)-1-2)
qi2 = e*(G(1,1)*G(2,1+e)-G(1,1)*G(1+e,3-l)) + 2*(G(e,3)*G(1,1)-G(1,1)*G(3,1-l+e))
i2 = qi2/(4-2*e-e-2-2)
qi0 = e*(i1-G(1,2)*G(3-l,1+e))+(i2-G(2,1)*G(4-l,e))
i0 = qi0/(4-2*e-e-1-4)
I = i0 * G(1,1)
I_series = I.series(e==0, 0)
I_series.evalf()
(-0.5)*e**(-3)+4.25*e**(-2)+(-17.375)*e**(-1)+Order(1)
ISE = I_series.evalf()