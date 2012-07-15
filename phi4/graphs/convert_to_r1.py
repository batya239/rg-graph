#!/usr/bin/python

import sys
table=eval(open(sys.argv[1]).read())
table['ee11-22-ee-']=[0,]
table['ee11-22-33-ee-']=[0,]

import kleinert

import sympy
from graphs import Graph
zeta = lambda x: sympy.special.zeta_functions.zeta(x).evalf()

def f(nomenkl):

    if nomenkl not in table.keys():
        raise ValueError, "no such graph in table: %s"%nomenkl
    g=Graph(nomenkl)
    g.GenerateNickel()
    e=sympy.var('e')
    res=0
    i=0
    for value in table[nomenkl]:
        res+=value*e**i/g.sym_coef()
        i+=1
    return res

def K_ms(expr):
    e=sympy.var('e')
    return expr.series(e,0,0).removeO()

def K(expr,N=1000):
    e=sympy.var('e')
    return expr.series(e,0,N).removeO()

def printKR1(key):
    print key
    print "   ", KR1_ms[key]
    res=0
    bad=False
    if isinstance(key,tuple):
        for t_ in key:
            coef,g_=t_
            if g_ in kleinert.MS.keys():
                res+=coef*kleinert.MS[g_].evalf()
            else:
                bad=True
#                print bad, g_
    elif key in kleinert.MS.keys():
         res=kleinert.MS[key].evalf()
    else:
         bad=True
    if not bad:
        print "   ", res
#    print "       ", KR1[key]
#    print "       ", G[key]
    print

e=sympy.var('e')
KR1=dict()
KR1_ms=dict()
G=dict()

#4x 1loop 1
KR1['ee11-ee-'] = K(2/e*f('ee11-ee-'))
KR1_ms['ee11-ee-'] = K_ms(2/e*f('ee11-ee-'))
G['ee11-ee-'] = KR1['ee11-ee-']
printKR1('ee11-ee-')

#2x 2loop 1
KR1['e111-e-'] = K(1/e*f('e111-e-'))
KR1_ms['e111-e-'] = K_ms(KR1['e111-e-'])
G['e111-e-'] = KR1['e111-e-']
printKR1('e111-e-')


#4x 2loop 1
KR1['ee11-22-ee-'] = K(1/e*(sympy.Number(0)-2*KR1['ee11-ee-']*f('ee11-ee-')))
KR1_ms['ee11-22-ee-'] = K_ms(KR1['ee11-22-ee-']+2*2/e*f('ee11-ee-')*(KR1['ee11-ee-']-KR1_ms['ee11-ee-']))
G['ee11-22-ee-'] = K( KR1['ee11-22-ee-']+2*G['ee11-ee-']*KR1['ee11-ee-'])
printKR1('ee11-22-ee-')

#4x 2loop 2
KR1['ee12-e22-e-'] = K(1/e*(f('ee12-e22-e-')-KR1['ee11-ee-']*f('ee11-ee-')))
KR1_ms['ee12-e22-e-'] = K_ms(KR1['ee12-e22-e-'] + 2/e*f('ee11-ee-')*(2/e*f('ee11-ee-')-K_ms(2/e*f('ee11-ee-'))))
G['ee12-e22-e-'] = K(KR1['ee12-e22-e-'] + G['ee11-ee-']*KR1['ee11-ee-'])
printKR1('ee12-e22-e-')

#2x 3loop 1
gamma='e112-22-e-'
KR1[gamma] = K(sympy.Number(2)/3/e*(f(gamma)
    - 2*KR1['e111-e-']*f('ee11-ee-')
    ))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + 2*G['e111-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    )

G[gamma] = K(KR1[gamma]
    + 2*G['e111-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-']))
printKR1(gamma)


#4x 3loop 1
KR1['ee11-22-33-ee-'] = K(sympy.Number(2)/3/e*(sympy.Number(0)-3*KR1['ee11-22-ee-']*f('ee11-ee-')))  #-2*G['ee11-ee-']*f('ee11-22-ee-')))
KR1_ms['ee11-22-33-ee-'] = K_ms(KR1['ee11-22-33-ee-']
                                + 3*G['ee11-22-ee-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
                                + 2*G['ee11-ee-']*(KR1['ee11-22-ee-']-KR1_ms['ee11-22-ee-'])
                                - G['ee11-ee-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2))
G['ee11-22-33-ee-'] = K(KR1['ee11-22-33-ee-']
                        + 3*G['ee11-22-ee-']*KR1['ee11-ee-']
                        +2*G['ee11-ee-']*KR1['ee11-22-ee-']
                        -G['ee11-ee-']*KR1['ee11-ee-']**2)
printKR1('ee11-22-33-ee-')

#4x 3loop 2
KR1['ee11-23-e33-e-'] = K(sympy.Number(2)/3/e*(sympy.Number(0)
    -KR1['ee11-22-ee-']*f('ee11-ee-')
    -KR1['ee11-ee-']*f('ee12-e22-e-')
    -KR1['ee12-e22-e-']*f('ee11-ee-')))
KR1_ms['ee11-23-e33-e-'] = K_ms(KR1['ee11-23-e33-e-']
    +G['ee12-e22-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    +G['ee11-ee-']*(KR1['ee12-e22-e-']-KR1_ms['ee12-e22-e-'])
    +G['ee11-22-ee-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    -G['ee11-ee-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2)
    )
G['ee11-23-e33-e-'] = K(KR1['ee11-23-e33-e-']
    +G['ee12-e22-e-']*(KR1['ee11-ee-'])
    +G['ee11-ee-']*(KR1['ee12-e22-e-'])
    +G['ee11-22-ee-']*(KR1['ee11-ee-'])
    -G['ee11-ee-']*(KR1['ee11-ee-']**2)
    )
printKR1('ee11-23-e33-e-')



G['ee11-ee-_1']=sympy.Number(1)/2*f('ee11-ee-')
G['ee11-ee-_1k']=G['ee11-ee-']-G['ee11-ee-_1']
KR1['ee11-ee-_1k']=G['ee11-ee-_1k']

#4x 3loop 3
KR1['ee12-ee3-333--'] = K(sympy.Number(2)/3/e*(f('ee12-ee3-333--')
                                               -KR1['ee11-ee-_1k']*f('e111-e-')))
KR1_ms['ee12-ee3-333--'] = K_ms(KR1['ee12-ee3-333--']
                                +G['ee11-ee-_1k']*(KR1['e111-e-']-KR1_ms['e111-e-'])
                                )
G['ee12-ee3-333--'] = K(KR1['ee12-ee3-333--']
                        +G['ee11-ee-_1k']*(KR1['e111-e-'])
                        )
printKR1('ee12-ee3-333--')


#4x 3loop 4
KR1['e123-e23-e3-e-'] = K(sympy.Number(2)/3/e*f('e123-e23-e3-e-'))
KR1_ms['e123-e23-e3-e-'] = K_ms(KR1['e123-e23-e3-e-'])
G['e123-e23-e3-e-'] = KR1['e123-e23-e3-e-']
printKR1('e123-e23-e3-e-')


#4x 3loop 5
KR1['ee12-e33-e33--'] = K(sympy.Number(2)/3/e*(f('ee12-e33-e33--')-2*KR1['ee12-e22-e-']*f('ee11-ee-')))
KR1_ms['ee12-e33-e33--'] = K_ms(KR1['ee12-e33-e33--']
    + 2 * G['ee12-e22-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee11-ee-']*(KR1['ee11-22-ee-']-KR1_ms['ee11-22-ee-'])
    )

G['ee12-e33-e33--'] = K(KR1['ee12-e33-e33--']
    + 2 * G['ee12-e22-e-']*(KR1['ee11-ee-'])
    + G['ee11-ee-']*(KR1['ee11-22-ee-'])
    )
printKR1('ee12-e33-e33--')


#4x 3loop 6
KR1['e112-e3-e33-e-'] = K(sympy.Number(2)/3/e*(f('e112-e3-e33-e-')-2*KR1['ee12-e22-e-']*f('ee11-ee-')))
KR1_ms['e112-e3-e33-e-'] = K_ms(KR1['e112-e3-e33-e-']
    + 2 * G['ee12-e22-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    - G['ee11-ee-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2)
    )

G['e112-e3-e33-e-'] = K(KR1['e112-e3-e33-e-']
    + 2 * G['ee12-e22-e-']*(KR1['ee11-ee-'])
    - G['ee11-ee-']*(KR1['ee11-ee-']**2)
    )
printKR1('e112-e3-e33-e-')


#4x 3loop 7
gamma='ee12-e23-33-e-'
KR1[gamma] = K(sympy.Number(2)/3/e*(f(gamma)-KR1['ee12-e22-e-']*f('ee11-ee-')-KR1['ee11-ee-']*f('ee12-e22-e-')))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + G['ee12-e22-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee11-ee-']*(KR1['ee12-e22-e-']-KR1_ms['ee12-e22-e-'])
    )

G[gamma] = K(KR1[gamma]
    + G['ee12-e22-e-']*(KR1['ee11-ee-'])
    + G['ee11-ee-']*(KR1['ee12-e22-e-'])
    )
printKR1(gamma)

#4x 3loop 8
gamma='ee12-223-3-ee-'
KR1[gamma] = K(sympy.Number(2)/3/e*(f(gamma)-2*KR1['ee11-ee-']*f('ee12-e22-e-')-KR1['ee11-22-ee-']*f('ee11-ee-')))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + 2*G['ee11-ee-']*(KR1['ee12-e22-e-']-KR1_ms['ee12-e22-e-'])
    + G['ee11-22-ee-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    )

G[gamma] = K(KR1[gamma]
    + 2*G['ee11-ee-']*(KR1['ee12-e22-e-'])
    + G['ee11-22-ee-']*(KR1['ee11-ee-'])
    )
printKR1(gamma)


#4x 4loop 1
gamma='ee11-22-33-44-ee-'
KR1[gamma] = K(sympy.Number(1)/2/e*(0-4*KR1['ee11-22-33-ee-']*f('ee11-ee-')))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + 4*G['ee11-22-33-ee-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + 3*G['ee11-22-ee-']*(KR1['ee11-22-ee-']-KR1_ms['ee11-22-ee-'])
    + 2*G['ee11-ee-']*(KR1['ee11-22-33-ee-']-KR1_ms['ee11-22-33-ee-'])
    - 3*G['ee11-22-ee-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2)
    - 2*G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee11-22-ee-']-KR1_ms['ee11-ee-']*KR1_ms['ee11-22-ee-'])
    )

G[gamma] = K(KR1[gamma]
    + 4*G['ee11-22-33-ee-']*(KR1['ee11-ee-'])
    + 3*G['ee11-22-ee-']*(KR1['ee11-22-ee-'])
    + 2*G['ee11-ee-']*(KR1['ee11-22-33-ee-'])
    - 3*G['ee11-22-ee-']*(KR1['ee11-ee-']**2)
    - 2*G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee11-22-ee-'])
)
printKR1(gamma)


#4x 4loop 2
gamma='ee11-22-34-e44-e-'
KR1[gamma] = K(sympy.Number(1)/2/e*(0
     - 2*KR1['ee11-23-e33-e-']*f('ee11-ee-')
     - KR1['ee11-22-33-ee-']*f('ee11-ee-')
     - KR1['ee11-22-ee-']*f('ee12-e22-e-')
     ))
KR1_ms[gamma] = K_ms(KR1[gamma]
     + 2*G['ee11-23-e33-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
     + G['ee11-22-33-ee-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
     + G['ee11-22-ee-']*(KR1['ee12-e22-e-']-KR1_ms['ee12-e22-e-'])
     + G['ee11-ee-']*(KR1['ee11-23-e33-e-']-KR1_ms['ee11-23-e33-e-'])
     + G['ee12-e22-e-']*(KR1['ee11-22-ee-']-KR1_ms['ee11-22-ee-'])
     - 2*G['ee11-22-ee-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2)
     - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-']-KR1_ms['ee11-ee-']*KR1_ms['ee12-e22-e-'])
     - G['ee11-ee-']*(KR1['ee11-22-ee-']*KR1['ee11-ee-']-KR1_ms['ee11-22-ee-']*KR1_ms['ee11-ee-'])
     )

G[gamma] = K(KR1[gamma]
     + 2*G['ee11-23-e33-e-']*(KR1['ee11-ee-'])
     + G['ee11-22-33-ee-']*(KR1['ee11-ee-'])
     + G['ee11-22-ee-']*(KR1['ee12-e22-e-'])
     + G['ee11-ee-']*(KR1['ee11-23-e33-e-'])
     + G['ee12-e22-e-']*(KR1['ee11-22-ee-'])
     - 2*G['ee11-22-ee-']*(KR1['ee11-ee-']**2)
     - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-'])
     - G['ee11-ee-']*(KR1['ee11-22-ee-']*KR1['ee11-ee-'])
     )

printKR1(gamma)


#4x 4loop 3
gamma='e112-e2-34-e44-e-'
KR1[gamma] = K(sympy.Number(1)/2/e*(0
    - 2*KR1['ee12-e22-e-']*f('ee12-e22-e-')
    - 2*KR1['ee11-23-e33-e-']*f('ee11-ee-')
    ))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + 2*G['ee12-e22-e-']*(KR1['ee12-e22-e-']-KR1_ms['ee12-e22-e-'])
    + 2*G['ee11-23-e33-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    - 2*G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-']-KR1_ms['ee11-ee-']*KR1_ms['ee12-e22-e-'])
    - G['ee11-22-ee-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2)
    )

G[gamma] = K(KR1[gamma]
    + 2*G['ee12-e22-e-']*(KR1['ee12-e22-e-'])
    + 2*G['ee11-23-e33-e-']*(KR1['ee11-ee-'])
    - 2*G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-'])
    - G['ee11-22-ee-']*(KR1['ee11-ee-']**2)
    )

printKR1(gamma)

#4x 4loop 4
gamma='ee11-23-e44-e44--'
KR1[gamma] = K(sympy.Number(1)/2/e*(0
    - KR1['ee12-e33-e33--']*f('ee11-ee-')
    - KR1['ee11-ee-']*f('ee12-e33-e33--')
    - 2*KR1['ee11-23-e33-e-']*f('ee11-ee-')
    ))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + G['ee12-e33-e33--']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee11-ee-']*(KR1['ee12-e33-e33--']-KR1_ms['ee12-e33-e33--'])
    + 2*G['ee11-23-e33-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee11-22-ee-']*(KR1['ee11-22-ee-']-KR1_ms['ee11-22-ee-'])
    - 2*G['ee12-e22-e-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee11-22-ee-']-KR1_ms['ee11-ee-']*KR1_ms['ee11-22-ee-'])
    )

G[gamma] = K(KR1[gamma]
    + G['ee12-e33-e33--']*(KR1['ee11-ee-'])
    + G['ee11-ee-']*(KR1['ee12-e33-e33--'])
    + 2*G['ee11-23-e33-e-']*(KR1['ee11-ee-'])
    + G['ee11-22-ee-']*(KR1['ee11-22-ee-'])
    - 2*G['ee12-e22-e-']*(KR1['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee11-22-ee-'])
    )

printKR1(gamma)


G['ee11-22-ee-_1']=K(G['ee11-ee-']*G['ee11-ee-_1']) # K(G['ee11-22-ee-']-G['ee11-ee-']*G['ee11-ee-_1'])
G['ee11-22-ee-_1k']=K(G['ee11-ee-']*G['ee11-ee-_1k']) # K(G['ee11-22-ee-']-G['ee11-ee-']*G['ee11-ee-_1'])
KR1['ee11-22-ee-_1k']=K(G['ee11-22-ee-_1k']-G['ee11-ee-']*KR1['ee11-ee-_1k']-G['ee11-ee-_1k']*KR1['ee11-ee-'])

#4x 4loop 5
gamma='ee11-23-ee4-444--'
KR1[gamma] = K(sympy.Number(1)/2/e*(0
    - KR1['ee12-ee3-333--']*f('ee11-ee-')
    - KR1['ee11-ee-']*f('ee12-ee3-333--')
    - KR1['ee11-22-ee-_1k']*f('e111-e-')
    ))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + G['ee12-ee3-333--']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee11-22-ee-_1k']*(KR1['e111-e-']-KR1_ms['e111-e-'])
    + G['ee11-ee-']*(KR1['ee12-ee3-333--']-KR1_ms['ee12-ee3-333--'])
    - G['ee11-ee-_1k']*(KR1['ee11-ee-']*KR1['e111-e-']-KR1_ms['ee11-ee-']*KR1_ms['e111-e-'])
    )

G[gamma] = K(KR1[gamma]
    + G['ee12-ee3-333--']*(KR1['ee11-ee-'])
    + G['ee11-22-ee-_1k']*(KR1['e111-e-'])
    + G['ee11-ee-']*(KR1['ee12-ee3-333--'])
    - G['ee11-ee-_1k']*(KR1['ee11-ee-']*KR1['e111-e-'])
    )

printKR1(gamma)

#4x 4loop 6
gamma='ee11-23-e34-44-e-'
KR1[gamma] = K(sympy.Number(1)/2/e*(0
    - KR1['ee12-e23-33-e-']*f('ee11-ee-')
    - KR1['ee11-23-e33-e-']*f('ee11-ee-')
    - KR1['ee11-22-ee-']*f('ee12-e22-e-')
    - KR1['ee11-ee-']*f('ee12-e23-33-e-')
    ))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + G['ee12-e23-33-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee11-23-e33-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee11-22-ee-']*(KR1['ee12-e22-e-']-KR1_ms['ee12-e22-e-'])
    + G['ee11-ee-']*(KR1['ee12-e23-33-e-']-KR1_ms['ee12-e23-33-e-'])
    - G['ee12-e22-e-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-']-KR1_ms['ee11-ee-']*KR1_ms['ee12-e22-e-'])
    )

G[gamma] = K(KR1[gamma]
    + G['ee12-e23-33-e-']*(KR1['ee11-ee-'])
    + G['ee11-23-e33-e-']*(KR1['ee11-ee-'])
    + G['ee11-22-ee-']*(KR1['ee12-e22-e-'])
    + G['ee11-ee-']*(KR1['ee12-e23-33-e-'])
    - G['ee12-e22-e-']*(KR1['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-'])
    )

printKR1(gamma)


#4x 4loop 7
gamma='ee11-23-334-4-ee-'
KR1[gamma] = K(sympy.Number(1)/2/e*(0
    - KR1['ee12-223-3-ee-']*f('ee11-ee-')
    - KR1['ee11-ee-']*f('ee12-223-3-ee-')
    - KR1['ee11-22-33-ee-']*f('ee11-ee-')
    - 2*KR1['ee11-22-ee-']*f('ee12-e22-e-')
    ))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + G['ee12-223-3-ee-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee11-ee-']*(KR1['ee12-223-3-ee-']-KR1_ms['ee12-223-3-ee-'])
    + G['ee11-22-33-ee-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + 2*G['ee11-22-ee-']*(KR1['ee12-e22-e-']-KR1_ms['ee12-e22-e-'])
    + G['ee11-ee-']*(KR1['ee11-23-e33-e-']-KR1_ms['ee11-23-e33-e-'])
    - G['ee11-22-ee-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-']-KR1_ms['ee11-ee-']*KR1_ms['ee12-e22-e-'])
    )

G[gamma] = K(KR1[gamma]
    + G['ee12-223-3-ee-']*(KR1['ee11-ee-'])
    + G['ee11-ee-']*(KR1['ee12-223-3-ee-'])
    + G['ee11-22-33-ee-']*(KR1['ee11-ee-'])
    + 2*G['ee11-22-ee-']*(KR1['ee12-e22-e-'])
    + G['ee11-ee-']*(KR1['ee11-23-e33-e-'])
    - G['ee11-22-ee-']*(KR1['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-'])
    )

printKR1(gamma)

#4x 4loop 8
gamma='ee12-233-34-4-ee-'
KR1[gamma] = K(sympy.Number(1)/2/e*(f(gamma)
    - KR1['ee12-223-3-ee-']*f('ee11-ee-')
    - KR1['ee11-22-ee-']*f('ee12-e22-e-')
    - 2*KR1['ee11-ee-']*f('ee12-e23-33-e-')
    ))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + G['ee12-223-3-ee-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee11-22-ee-']*(KR1['ee12-e22-e-']-KR1_ms['ee12-e22-e-'])
    + 2*G['ee11-ee-']*(KR1['ee12-e23-33-e-']-KR1_ms['ee12-e23-33-e-'])
    )

G[gamma] = K(KR1[gamma]
    + G['ee12-223-3-ee-']*(KR1['ee11-ee-'])
    + G['ee11-22-ee-']*(KR1['ee12-e22-e-'])
    + 2*G['ee11-ee-']*(KR1['ee12-e23-33-e-'])
    )

printKR1(gamma)

#4x 4loop 9
gamma='ee12-223-4-e44-e-'
KR1[gamma] = K(sympy.Number(1)/2/e*(f(gamma)
    - KR1['ee12-223-3-ee-']*f('ee11-ee-')
    - KR1['ee11-23-e33-e-']*f('ee11-ee-')
    - KR1['ee12-e22-e-']*f('ee12-e22-e-')
    - KR1['ee11-ee-']*f('e112-e3-e33-e-')
    ))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + G['ee12-223-3-ee-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee11-23-e33-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee12-e22-e-']*(KR1['ee12-e22-e-']-KR1_ms['ee12-e22-e-'])
    + G['ee11-ee-']*(KR1['e112-e3-e33-e-']-KR1_ms['e112-e3-e33-e-'])
    - G['ee11-22-ee-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-']-KR1_ms['ee11-ee-']*KR1_ms['ee12-e22-e-'])
    )

G[gamma] = K(KR1[gamma]
    + G['ee12-223-3-ee-']*(KR1['ee11-ee-'])
    + G['ee11-23-e33-e-']*(KR1['ee11-ee-'])
    + G['ee12-e22-e-']*(KR1['ee12-e22-e-'])
    + G['ee11-ee-']*(KR1['e112-e3-e33-e-'])
    - G['ee11-22-ee-']*(KR1['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-'])
    )
printKR1(gamma)

#4x 4loop 10
gamma='e123-e24-34-e4-e-'
KR1[gamma] = K(sympy.Number(1)/2/e*(f(gamma) ))
KR1_ms[gamma] = K_ms(KR1[gamma])

G[gamma] = K(KR1[gamma])
printKR1(gamma)

#4x 4loop 11
gamma='e112-34-e34-e4-e-'
KR1[gamma] = K(sympy.Number(1)/2/e*(f(gamma)
    - KR1['e123-e23-e3-e-']*f('ee11-ee-')
    ))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + G['e123-e23-e3-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    )

G[gamma] = K(KR1[gamma]
    + G['e123-e23-e3-e-']*(KR1['ee11-ee-'])
    )
printKR1(gamma)

#4x 4loop 12
gamma='e112-e3-e34-44-e-'
KR1[gamma] = K(sympy.Number(1)/2/e*(f(gamma)
    - KR1['ee12-e23-33-e-']*f('ee11-ee-')
    - KR1['e112-e3-e33-e-']*f('ee11-ee-')
    - KR1['ee12-e22-e-']*f('ee12-e22-e-')
    ))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + G['ee12-e23-33-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['e112-e3-e33-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee12-e22-e-']*(KR1['ee12-e22-e-']-KR1_ms['ee12-e22-e-'])
    - G['ee12-e22-e-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-']-KR1_ms['ee11-ee-']*KR1_ms['ee12-e22-e-'])
    )

G[gamma] = K(KR1[gamma]
    + G['ee12-e23-33-e-']*(KR1['ee11-ee-'])
    + G['e112-e3-e33-e-']*(KR1['ee11-ee-'])
    + G['ee12-e22-e-']*(KR1['ee12-e22-e-'])
    - G['ee12-e22-e-']*(KR1['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee12-e22-e-'])
    )
printKR1(gamma)


#4x 4loop 13
gamma='e112-e3-e44-e44--'
KR1[gamma] = K(sympy.Number(1)/2/e*(f(gamma)
    - KR1['ee12-e33-e33--']*f('ee11-ee-')
    - 2*KR1['e112-e3-e33-e-']*f('ee11-ee-')
    ))
KR1_ms[gamma] = K_ms(KR1[gamma]
    + G['ee12-e33-e33--']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + 2*G['e112-e3-e33-e-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
    + G['ee12-e22-e-']*(KR1['ee11-22-ee-']-KR1_ms['ee11-22-ee-'])
    - 2*G['ee12-e22-e-']*(KR1['ee11-ee-']**2-KR1_ms['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee11-22-ee-']-KR1_ms['ee11-ee-']*KR1_ms['ee11-22-ee-'])
    )

G[gamma] = K(KR1[gamma]
    + G['ee12-e33-e33--']*(KR1['ee11-ee-'])
    + 2*G['e112-e3-e33-e-']*(KR1['ee11-ee-'])
    + G['ee12-e22-e-']*(KR1['ee11-22-ee-'])
    - 2*G['ee12-e22-e-']*(KR1['ee11-ee-']**2)
    - G['ee11-ee-']*(KR1['ee11-ee-']*KR1['ee11-22-ee-'])
    )
printKR1(gamma)

def KR(gamma, R1op, nloops):
    e=sympy.var('e')
    if isinstance(gamma, tuple):
        kr1=0
        for t_ in gamma:
           coef, gamma_=t_
           kr1+=coef*f(gamma_)
    else:
        kr1=f(gamma)
    for r1term in R1op:
        coef, g, subs = r1term
#        print coef,g,subs,subs[0]
        if len(subs)==1:
           kr1-= coef*KR1[g]*f(subs[0])
    kr1=K(kr1*2/nloops/e)
    
    kr1_ms=kr1
    g_=kr1
    for r1term in R1op:
        kr1_ms_term=1.
        kr1_term=1.
        coef, g, subs = r1term
        if len(subs)==0:
            raise Exception, "no subgraphs in R1op:"%R1op

        for sub in subs:
            kr1_ms_term=kr1_ms_term*KR1_ms[sub]
            kr1_term=kr1_term*KR1[sub]
        kr1_ms+=coef*G[g]*(kr1_term-kr1_ms_term)
        g_+=coef*G[g]*(kr1_term)
    kr1_ms=K_ms(kr1_ms)
    g_=K(g_)
    KR1[gamma]=kr1
    KR1_ms[gamma]=kr1_ms
    G[gamma]=g_
        
    

#4x 4loop 14
#gamma='ee12-334-334--ee-'
#KR1[gamma] = K(sympy.Number(1)/2/e*(f(gamma)
#    - 2*KR1['ee12-223-3-ee-']*f('ee11-ee-')
#    - 2*KR1['ee11-ee-']*f('ee12-e33-e33--')
#    ))
#KR1_ms[gamma] = K_ms(KR1[gamma]
#    + 2*G['ee12-223-3-ee-']*(KR1['ee11-ee-']-KR1_ms['ee11-ee-'])
#    + 2*G['ee11-ee-']*(KR1['ee12-e33-e33--']-KR1_ms['ee12-e33-e33--'])
#    + G['ee11-22-ee-']*(KR1['ee11-22-ee-']-KR1_ms['ee11-22-ee-'])
#    )
#
#G[gamma] = K(KR1[gamma]
#    + 2*G['ee12-223-3-ee-']*(KR1['ee11-ee-'])
#    + 2*G['ee11-ee-']*(KR1['ee12-e33-e33--'])
#    + G['ee11-22-ee-']*(KR1['ee11-22-ee-'])
#    )
#printKR1(gamma)


#4x 4loop 14
gamma='ee12-334-334--ee-'
R1op=[
      (2,'ee12-223-3-ee-',('ee11-ee-',)),
      (2,'ee11-ee-',('ee12-e33-e33--',)),
      (1,'ee11-22-ee-',('ee11-22-ee-',)),
     ]
KR(gamma, R1op, 4)
printKR1(gamma)

#4x 4loop 15
gamma='ee12-ee3-344-44--'
R1op=[
      (2,'ee12-ee3-333--',('ee11-ee-',)),
      (1,'ee11-ee-_1k',('e112-22-e-',)),
     ]
KR(gamma, R1op, 4)
printKR1(gamma)

G['ee12-e22-e-_']=f('ee12-e22-e-')+f('ee11-ee-')*KR1['ee11-ee-']
G['ee12-e22-e-_k']=K(G['ee12-e22-e-']-G['ee12-e22-e-_'])
KR1['ee12-e22-e-_k']=K(G['ee12-e22-e-_k']-2*G['ee11-ee-']*KR1['ee11-ee-_1k']-2*G['ee11-ee-_1k']*KR1['ee11-ee-'])

print "16+19"
#4x 4loop 16+19
gamma=(
       (1,'ee12-e23-e4-444--'),
       (1,'ee12-e33-444-e4--'),
      )
R1op=[  
      (0.5,'ee12-e22-e-_k',('e111-e-',)),
      (1,'ee11-ee-',('ee12-ee3-333--',)),
      (1,'ee12-ee3-333--',('ee11-ee-',)),
      (-1,'ee11-ee-_1k',('ee11-ee-','e111-e-',)),
     ]
KR(gamma, R1op, 4)
printKR1(gamma)

#4x 4loop 17
gamma='ee12-e34-e34-44--'
R1op=[
      (1,'ee12-e33-e33--',('ee11-ee-',)),
      (2,'ee12-e22-e-',('ee12-e22-e-',)),
      (1,'ee11-ee-',('ee12-223-3-ee-',)),
     ]
KR(gamma, R1op, 4)
printKR1(gamma)

print "18"
#4x 4loop 18
gamma='ee12-e33-e44-44--'
R1op=[
      (3,'ee12-e33-e33--',('ee11-ee-',)),
      (2,'ee12-e22-e-',('ee11-22-ee-',)),
      (1,'ee11-ee-',('ee11-22-33-ee-',)),
      (-1,'ee12-e22-e-',('ee11-ee-','ee11-ee-')),
     ]
KR(gamma, R1op, 4)
printKR1(gamma)

print "20"
#4x 4loop 20
gamma='ee12-233-44-e4-e-'
R1op=[
      (2,'ee12-e23-33-e-',('ee11-ee-',)),
      (1,'ee11-ee-',('e112-e3-e33-e-',)),
      (-1,'ee12-e22-e-',('ee11-ee-','ee11-ee-')),
     ]
KR(gamma, R1op, 4)
printKR1(gamma)

print "21"
#4x 4loop 21
gamma='ee12-234-34-e4-e-'
R1op=[
      (1,'ee11-ee-',('e123-e23-e3-e-',)),
     ]
KR(gamma, R1op, 4)
printKR1(gamma)

print "22"
#4x 4loop 20
gamma='ee12-334-344-e-e-'
R1op=[
      (2,'ee12-e23-33-e-',('ee11-ee-',)),
      (1,'ee11-ee-',('e112-e3-e33-e-',)),
      (-1,'ee12-e22-e-',('ee11-ee-','ee11-ee-')),
     ]
KR(gamma, R1op, 4)
printKR1(gamma)
