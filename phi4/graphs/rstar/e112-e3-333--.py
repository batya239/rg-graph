#!/usr/bin/python
# -*- coding: utf8
import sys

__author__ = 'mkompan'

from rggraphenv.symbolic_functions import e, G, G1, G2, series, var, cln

x = var('x')

print
print
print
print

K = lambda x: series(x,e,0,0,True).expand()
kr1 = series(G(1, 1) * G1(2, e), e, 0, 0, True).expand()
kr2 = K(G(1,1)*G(e,1))   #e111-e-
print kr1
print kr2
ir1 = 1 / e
ir2_1 = series(G(1, 1) * G1(2, e) * G(1+2*e, 1) * x**(-3*e) - kr2*2*(-1*e/2/e) * G(1, 1)*x**(-e) + ir1 * kr1, e, 0, 0, True).expand()
print ir2_1
ir2 = series(G(1, 1) * G1(2, e) * G(1+2*e, 1) * x**(-3*e) - kr1 * G(1, 1)*x**(-e) + ir1 * kr1 + K(G(1,1)*K(G1(1,1)*G1(2,1))) , e, 0, 0, True).expand()
# ir2 = 1/e/24  #fake
print "ir2", ir2



kr_1 =  K(G(1,1)*G(1,e)*G(1+2*e,1)-kr2*G(1,1)) #ee12-ee3-333--
ir3 = K(kr_1 +kr2*ir1)
print "ir3", ir3

ir4 = K((1/e/e/e/3-2/e/e/3+1/e/3) + 1/e*(1/e/e)+2*(-1/e/e/2+1/e/2)*(1/e))
print "ir4", ir4

ir5 = ir3

print "ir5", ir5
print
print "---"
print

t1_1 = K(2*(2*e/(4-2*e))*
         (G(1,1)*G(1,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)+G(1,1)*x**(-e)*ir3))
t1_2 = K((2*e/(4-2*e))*
         (G(1,1)*G(2,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)+G(1,1)*x**(-e)*ir4+G(1,1)*G(2+e,e)*G(1,1)*x**(-3*e)*ir1))

t1_3 = K(2*(4/(4-2*e))*
         (G(1,1)*G1(2,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)+G(1,1)*x**(-e)*ir2))
t1_4 = K((4/(4-2*e))*
         (G(1,1)*G(1,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)+G(1,1)*x**(-e)*ir5))
t2 = K((2*e/(4-2*e))
       *(-kr2)*(G(2,e)*G(1,1)*x**(-2*e)+ir1*G(1,1)*x**(-e)))

print "r1", K(G(1,1)*G(1,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)+G(1,1)*x**(-e)*ir3)
# print "i1", K(ir3)
print
print "r2", K((G(1,1)*G(2,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)
               +G(1,1)*x**(-e)*ir4
               +G(1,1)*G(2+e,e)*G(1,1)*x**(-3*e)*ir1)).subs(x==1)
# print "i2", K(ir4)
print
print "r3", K((G(1,1)*G1(2,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)
               +G(1,1)*x**(-e)*ir2)).subs(x==1)
# print "i3", K(ir2)
print

print "r4", K((G(1,1)*G(1,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)+G(1,1)*x**(-e)*ir5)).subs(x==1)
# print "i4", K(ir5)
print

print "r5", series(G(2,e)*G(1,1)*x**(-2*e)+ir1*G(1,1)*x**(-e),e,0,2).expand()

print "t1", K(t1_1).subs(x==1), K(t1_1).coeff(e,-3)
print "t2", K(t1_2).subs(x==1), K(t1_2).coeff(e,-3)
print "t3", K(t1_3).subs(x==1), K(t1_3).coeff(e,-3)
print "t4", K(t1_4).subs(x==1), K(t1_4).coeff(e,-3)
print "t5", K(t2).subs(x==1), K(t2).coeff(e,-3)
print K(t1_1+t1_2+t1_3+t1_4+t2)
print K(t1_1+t1_2+t1_3+t1_4+t2).subs(x==1)

print
print
print "=============="
print
print series(G(1,1)*G(1,e)*G(1+2*e,e)*G(1,1)*(1-4*e)*(4-2*e-8*e)/(4-2*e),e,0,4).expand()
print series(G(1,1)*G(1,e)*G(1+2*e,1+e)*G(1,2)*(2*e)/(4-2*e),e,0,4).expand()
print series(1/(G(1,1)*G(1,e)*G(1+2*e,e)*G(1,1)*(1-4*e)*(4-2*e-8*e)/(4-2*e) /(G(1,1)*G(1,e)*G(1+2*e,1+e)*G(1,2)*(2*e)/(4-2*e))),e,0,4).expand()

y1 = K(2*(2*e/(4-2*e))*
         (G(1,1)*G(1,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)))
y2 = K((2*e/(4-2*e))*
         (G(1,1)*G(2,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)))

y3 = K(2*(4/(4-2*e))*
         (G(1,1)*G1(2,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)))
y4 = K((4/(4-2*e))*
         (G(1,1)*G(1,e)*G(2+2*e,e)*G(1,1)*x**(-4*e)))

y5 = K((2*e/(4-2*e))
       *(-kr2)*(G(2,e)*G(1,1)*x**(-2*e)))


print series((y1+y2+y3+y4).subs(x==1),e,0,4).expand()
print K((y1+y2+y3+y4-kr2*(G(1,1)*G(1,e)*(1-2*e)*(4-2*e-4*e)/(4-2*e))).subs(x==1))
print "+++"
print "+++"
print K((y1+y2+y3+y4+y5).subs(x==1))
ir6 = 1/e/e

u1 = K(2*(2*e/(4-2*e))*
       ((G(1,1)*x**(-1*e)-K(G(1,1)))*ir3))

u2 = K((2*e/(4-2*e))*
         ((G(1,1)*x**(-1*e)-K(G(1,1)))*ir4
          +(G(1,1)*G(2+e,e)*G(1,1)*x**(-3*e)
            -(cln(1)/3*e**(-3)-cln(1)/3*e**(-2)-cln(1)/3*e**(-1))
            -K(G(1,1))*G(2,e)*G(1,1)*x**(-2*e))*ir1
          +(-(G(1,1)*x**(-e)-K(G(1,1)))*K(G(1,1))*ir6)))

x1=var('x1')
x2=var('x2')
x3=var('x3')
# ir2 = x2/e/e+x1/e
# ir2 = 1/e/24
print
print ir2
print kr2
u3 = K(2*(4/(4-2*e))*
         ((G(1,1)*x**(-e)-K(G(1,1)))*ir2))

u4 = K((4/(4-2*e))*
         ((G(1,1)*x**(-e)-K(G(1,1)))*ir5))

u5 = K((2*e/(4-2*e))
       *(-kr2)*(ir1*(G(1,1)*x**(-e)-K(G(1,1)))))

print
for i, u in enumerate([u1, u2, u3, u4, u5, u1+u2+u3+u4+u5]):
    print i+1, u
    print u.coeff(e,-3), u.coeff(e,-2), u.coeff(e,-1)
    print

print
for i, u in enumerate([y1+u1, y2+u2, y3+u3, y4+u4, y5+u5, y1+y2+y3+y4+y5+u1+u2+u3+u4+u5]):
    print i+1, u
    print u.coeff(e,-3), u.coeff(e,-2),u.coeff(e,-1)
    print

print "------"
print
E=e
iro_0 = 1/e #e11|e|
iro_1 = 0   #e11|e|:1|E|

kro_2 = K(E*(cln(1)/6*e**(-2)-cln(3)/8*e**(-1)))  #e12|e3|333||:1|E|1|1|
iro_2 = K(kro_2+K(G(1,1)*G(1,e))*iro_1)
print "kro_2", kro_2
print "iro_2", iro_2


kro_3 = 0  #e11|22|e|:1|1|E|
iro_3 = 0  #e11|22|e|:1|1|E|

kro_4 = K(G(1,1)*G(1+e,1)*E*x**(-2*e)-K(G(1,1))*G(1,1)*E*x**(-1*e))   # ee12|e22|e|:E|1|1|
kro_4a = kro_4+cln(1)/4
kro_4b = kro_4+cln(1)/4
kro_4b = kro_4
print kro_4, K(G(1,1)*G(2,e)*E), kro_4a
kro_5 = K(G(2,e)*G(1,1)*G(1+2*e,1)*E*x**(-3*e) - kro_4*G(1,1)*x**(-1*e))  # ee12|223|3|ee:1|1|1|E|
print kro_5
print K(G(2,e)*G(1,1)*G(1+2*e,1)*E*x**(-3*e) - K(G(1,1)*G(1+e,1)-G(1,1)**2)*E*G(1,1)*x**(-1*e)
        +G(1,1)*G(1,e)*E*iro_0*x**(-2*e)-1/e*E*G(1,1)*iro_0*x**(-1*e)-kro_2*iro_0), "!!!!!!!!!!!"
iro_5 = K(kro_5 + kro_4b *(iro_0)) # ee12|223|3|ee:1|1|1|E|
print iro_5
kro_6 = K(G(1,1)**2*G(2+e,e))   # e112|e3|33||


o1 = 4 * K(G(1,1)*G(1,e)*G(1,1)*G(2+2*e,e)*E*x**(-4*e)
           -K(G(1,1)*G(1,e))*(G(1,1)*G(2,e)*E)*x**(-2*e)
           -0
           +0)
o1i = 4 * K(G(1,1)*iro_2*x**(-1*e)
            -0
            -K(G(1,1))*iro_2
            +0)

o2 = 2*K(E*G(2,e)*G(1,1)**2*G(2+2*e,e)*x**(-4*e)
         -kro_4a*G(1,1)*G(2,e)*x**(-2*e)
         +0
         +0
         +0
         +0
         +0)

o2i = 2*K(G(1,1)*iro_5*x**(-1*e)
          -G(1,1)*iro_0*kro_4a*x**(-1*e)
          -K(G(1,1))*iro_5
          +K(G(1,1))*iro_0*kro_4a
          +0
          +0
          +0)


o3 = 8 * K(G1(2,e)*G(1,1)*G(2+2*e,e)*G(1,1)*x**(-4*e)
           -K(G1(2,e)*G(1,1))*G(2,e)*G(1,1)*x**(-2*e)
           -0
           -0
           -0
           -0
           +0)

o3i = 8 * K(G(1,1)*ir2*x**(-1*e)
            -K(G1(2,e)*G(1,1))*G(1,1)*iro_0*x**(-1*e)
            -K(G(1,1)*ir2)
            -K(G(1,1))*G(1,1)*x**(-1*e)*K(G1(1,1)*G1(2,1))
            -0
            +K(G(1,1))**2*K(G1(1,1)*G1(2,1))
            +K(G(1,1))*K(G1(2,e)*G(1,1))*iro_0)


o4 = 4 * K(G(1,1)*G(1,e)*G(1,1)*G(2+2*e,e)*x**(-4*e)
           -K(G(1,1)*G(1,e))*(G(1,1)*G(2,e))*x**(-2*e)
           -0
           +0)
o4i = 4 * K(G(1,1)*ir3*x**(-1*e)
            -K(G(1,1)*G(1,e))*G(1,1)*x**(-1*e)*iro_0
            -K(G(1,1))*ir3
            +K(G(1,1)*G(1,e))*K(G(1,1))*iro_0)

terms = [o1+o1i,o2+o2i,o3+o3i,o4+o4i]


for term in terms:
    print K(term)
print

print K(sum(terms))
print "       ", K(sum(terms)/(4-2*e))

print cln(5)/32*e**(-1)-cln(1)/32*e**(-2)-K(sum(terms))
print (terms[2]+cln(5)/32*e**(-1)-cln(1)/32*e**(-2)-K(sum(terms)))
print (terms[2]+cln(5)/32*e**(-1)-cln(1)/32*e**(-2)-K(sum(terms)))/8

print "-----------------------"


o2a = 2*K(E*G(2,e)*G(1,1)**2*G(2+2*e,e)*x**(-4*e)
          -kro_4a*G(1,1)*G(2,e)*x**(-2*e)
          +0
          +0
          +0
          +0
          +0)

iro_1a = 1/e/e
iro_5a = K(cln(1)/3*e**(-3)-cln(2)/3*e**(-2)+cln(1)/3*e**(-1)+2*K(G(1,1)*G(1+e,1)-G(1,1)*G(1,1))*iro_0+K(G(1,1))*iro_1a)



o2ia = 2*K(G(1,1)*iro_5a*E*x**(-1*e)+G(1,1)**2*G(2+e,e)*iro_0*x**(-3*e)*E   #1
           -G(1,1)*iro_0*kro_4a*x**(-1*e)  #4
           -K(G(1,1))*iro_5a*E    #2
           +K(G(1,1))*iro_0*kro_4a #7
           -K(cln(1)/3*e**(-3)-cln(1)/3*e**(-2)-cln(1)/3*e**(-1))*iro_0*E  #5
           +K(G(1,1))**2*iro_1a*E #6
           -K(G(1,1))*iro_0*G(1,1)*G(2,e)*E*x**(-2*e)-K(G(1,1))*iro_1a*G(1,1)*x**(-1*e)*E)

print K(o2a+o2ia).subs(x==1)
print K(o2a+o2ia)
print K(o2a).subs(x==1)
print K(o2ia).subs(x==1)
print K(o2+o2i)-K(o2a+o2ia).subs(x==x)


print K(o3).subs(x==1)
print kro_4,kro_4a

sys.exit()


























u1 = K(2*(2*e/(4-2*e))*
         (G(1,1)*ir3))

u2 = K((2*e/(4-2*e))*
         (G(1,1)*ir4+G(1,1)*G(2+e,e)*G(1,1)*ir1))

x1=var('x1')
x2=var('x2')
x3=var('x3')
ir2 = x2/e/e+x1/e
# ir2 = 1/e/24
print
print ir2
u3 = K(2*(4/(4-2*e))*
         (G(1,1)*ir2))

u4 = K((4/(4-2*e))*
         (G(1,1)*ir5))

u5 = K((2*e/(4-2*e))
       *(-kr2)*(ir1*G(1,1)))

print
for i, u in enumerate([u1, u2, u3, u4, u5, u1+u2+u3+u4+u5]):
    print i+1, u
    print u.coeff(e,-3), u.coeff(e,-2), u.coeff(e,-1)
    print

print
for i, u in enumerate([y1+u1, y2+u2, y3+u3, y4+u4, y5+u5, y1+y2+y3+y4+y5+u1+u2+u3+u4+u5]):
    print i+1, u
    print u.coeff(e,-3), u.coeff(e,-2)
    print