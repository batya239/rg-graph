#!/usr/bin/python

import sympy
zeta = lambda x: sympy.special.zeta_functions.zeta(x).evalf()
e=sympy.var('e')
MS={
    'e111-e-':(-0.5/e)/4,
    'ee11-ee-':(2./e)/2,
    'ee11-22-ee-':(-4./e**2)/4,
    'ee12-e22-e-':(-1./e-2./e/e)/4,
    'e112-22-e-':(-1./6/e+2./3/e/e)/8,

    'ee11-22-33-ee-':(8./e**2)/8,
    'ee11-23-e33-e-':(-2/e**2+4./e**3)/8,
    'ee12-ee3-333--':(-3./4/e+2./3/e**2)/8,
    'e123-e23-e3-e-':(4*zeta(3))/8,
    'ee12-e33-e33--':(-2./3/e-4./3/e**2+8./3/e**3)/8,
    'e112-e3-e33-e-':(-2./3/e-4./3/e**2+8./3/e**3)/8,
    'ee12-e23-33-e-':(4./3/e-2./e**2+4./3/e**3)/8,
    'ee12-223-3-ee-':(2./3/e-8./3/e**2+8./3/e**3)/8,

    'ee11-22-33-44-ee-':(-16./e**4)/16,
    'ee11-22-34-e44-e-':(4./e**3-8./e**4)/16,
    'e112-e2-34-e44-e-':(-1./e+4./e**2-4./e**3)/16,
    'ee11-23-e44-e44--':(4./3/e+8./3/e**2-16./3/e**3)/16,
    'ee11-23-ee4-444--':(3./2/e**2-4./3/e**3)/16,
    'ee11-23-e34-44-e-':(-8./3./e**2-4./e**3-8./3/e**4)/16,
    'ee11-23-334-4-ee-':(-4./3./e**2+16./3/e**3-16./3/e**4)/16,
    'ee12-233-34-4-ee-':((11./6-zeta(3))-13./3./e**2+10./3/e**3-4./3/e**4)/16,
    'ee12-223-4-e44-e-':(-0.5/e**1+1./6/e**2+10./3/e**3-10./3/e**4)/16,
#4x 4l-10
    'e123-e24-34-e4-e-':(10*zeta(5)/e)/16,

    'e112-34-e34-e4-e-':((3*zeta(3)-1.5*zeta(4))/e**1-2*zeta(3)/e**2)/16,
    'e112-e3-e34-44-e-':(-2./3/e**1-5./6/e**2+8./3/e**3-2./e**4)/16,
    'e112-e3-e44-e44--':((0.5-zeta(3))/e+1./e**2+2./e**3-4./e**4)/16,
    'ee12-334-334--ee-':(-(2-2*zeta(3))/e+4./3/e**2+8./3/e**3-8./3./e**4)/16,
    'ee12-ee3-344-44--':(-7./12/e+1./e**2-2./3/e**3)/16,
    'ee12-e23-e4-444--':(-121./96/e+11./8/e**2-1./2/e**3)/16,
    'ee12-e34-e34-44--':(-(1-2*zeta(3))/e-5./3/e**2+8./3/e**3-4./3/e**4)/16,
    'ee12-e33-e44-44--':((0.5-zeta(3))/e+1./e**2+2./e**3-4./e**4)/16,
    'ee12-e33-444-e4--':(37./96/e+5./8/e**2-5./6/e**3)/16,
    'ee12-233-44-e4-e-':(-(5./6 -zeta(3))/e-1./3/e**2+2./e**3-4./3/e**4)/16,

    'ee12-234-34-e4-e-':((3*zeta(3)+1.5*zeta(4))/e-6.*zeta(3)/e**2)/16,
    'ee12-334-344-e-e-':(-5./6/e-1./3/e**2+2./e**3-4./3/e**4)/16,
    'ee12-e33-344-4-e-':(-2./3/e-5./6/e**2+8./3/e**3-2./e**4)/16,
    'ee12-e23-44-e44--':(-(5./6-zeta(3))/e-1./3/e**2+2./e**3-4./3/e**4)/16,
    'ee12-e34-334-4-e-':((5./2-2*zeta(3))/e-19./6/e**2+2./e**3-2./3/e**4)/16,
    'ee12-e23-34-44-e-':(5./2/e-19./6/e**2+2./e**3-2./3/e**4)/16,
#2x 4l

    'e112-33-e33--':(5./16/e+1./4/e**2-1./e**3)/16,
    'e112-e3-333--':(5./16/e-1./8/e**2)/16,
    'e123-e23-33--':(-13./48/e+7./12/e**2-1./3/e**3)/16,
    'e112-23-33-e-':(-2./3/e+2./3/e**2-2./3/e**3)/16,
    }

