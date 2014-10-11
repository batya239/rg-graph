#!/usr/bin/python
__author__ = 'mkompan'

from rggraphenv.symbolic_functions import var, series
import swiginac

p1, p2, p3, p4 = var('p1 p2 p3 p4')
P1, P2, P3, P4 = var('P1 P2 P3 P4')
k1, k2, k3 = var('k1 k2 k3')
cp1k1, cp1k3, cp1p2, cp2k3, cp1p3, cp2k3, cp2p3, cp3k3 = var('cp1k1 cp1k3 cp1p2 cp2k3 cp1p3 cp2k3 cp2p3 cp3k3')
cp1k2, cp2k2, cp3k2, ck1k3, ck2k3, ck1k2, cp3k1 = var('cp1k2  cp2k2 cp3k2 ck1k3 ck2k3 ck1k2 cp3k1')
u1, u2, u3, u4, u5, u6, u7, u8, u9, u10, u11 = var('u1 u2 u3 u4 u5 u6 u7 u8 u9 u10 u11')
print p1

# B = (u1 *(p1+k1)**2 + u2 *(p1+k3)**2 + u3 *(p1+p2+k3)**2
#      + u4 *(p1+p2+p3+k3)**2 + u5 *(p1+p2+p3+k2)**2 + u6 *(k2)**2
#      + u7 *(k1)**2 + u8 * (k1-k3)**2 + u9 * (k2-k3)**2
#      + u10*(k1-k2)**2 + u11*(p3-k1)**2)

B = (u1 *(P1+k1)**2 + u2 *(P1+k3)**2 + u3 *(P2+k3)**2
     + u4 *(P3+k3)**2 + u5 *(P3+k2)**2 + u6 *(k2)**2
     + u7 *(k1)**2 + u8 * (k1-k3)**2 + u9 * (k2-k3)**2
     + u10*(k1-k2)**2 + u11*(k3)**2)
     #+ u10*(k1-k2)**2 + u11*(P4-k1)**2)

# B = (u1 *(p1**2+k1**2+2*cp1k1*p1*k1) +
#      u2 *(p1**2+k3**2+cp1k3*2*p1*k3) +
#      u3 *(p1**2+p2**2+k3**2+2*cp1p2*p1*p2+2*cp1k3*p1*k3+2*cp2k3*p2*k3)
#      + u4 *(p1**2+p2**2+p3**2+k3**2 +2*cp1p2*p1*p2+2*cp1k3*p1*k3+2*cp2k3*p2*k3
#             +2*cp1p3*p1*p3+2*cp3k3*p3*k3
#             +2*cp2p3*p2*p3)
#      + u5 *(p1**2+p2**2+p3**2+k2**2 +2*cp1p2*p1*p2+2*cp1k2*p1*k2+2*cp2k2*p2*k2
#             +2*cp1p3*p1*p3+2*cp3k2*p3*k2
#             +2*cp2p3*p2*p3)
#      + u6 *(k2)**2
#      + u7 *(k1)**2
#      + u8 * (k1**2-2*ck1k3*k1*k3+k3**2)
#      + u9 * (k2**2-2*ck2k3*k2*k3+k3**2)
#      + u10*(k1**2-2*ck1k2*k1*k2+k2**2)
#      + u11*(p3**2-2*cp3k1*p3*k1+k1**2))
#

v = swiginac.matrix([
    [B.diff(k1, 2)/2,        B.diff(k1).diff(k2)/2, B.diff(k1).diff(k3)/2],
    [B.diff(k1).diff(k2)/2, B.diff(k2, 2)/2,        B.diff(k2).diff(k3)/2],
    [B.diff(k1).diff(k3)/2, B.diff(k2).diff(k3)/2, B.diff(k3, 2)/2]])
det = v.determinant()
print "det"
print det

# print B.diff(k1).subs(k1==0).subs(k2==0).subs(k3==0)
# print B.diff(k2).subs(k1==0).subs(k2==0).subs(k3==0)
# print B.diff(k3).subs(k1==0).subs(k2==0).subs(k3==0)

a = swiginac.matrix([[B.diff(k1).subs(k1==0).subs(k2==0).subs(k3==0),
                     B.diff(k2).subs(k1==0).subs(k2==0).subs(k3==0),
                     B.diff(k3).subs(k1==0).subs(k2==0).subs(k3==0)]])

at = a.transpose()
# print B.subs(k1==0).subs(k2==0).subs(k3==0)
c = (B.subs(k1==0).subs(k2==0).subs(k3==0)*det-(a*(v.inverse()*det)*at)[0,0].expand()).expand()

# P1 = p1
# P2 = p1+p2
# P3 = p1+p2+p3
# P4 = p3

# t = 0
# P1 = p1
# P2 = p1+p2
# P3 = p1
# P4 = -p2


# c = c.subs(cp2k2*cp3k2==cp2p3)\
#     .subs(cp2k3*cp3k3==cp2p3)\
#     .subs(cp2k2*cp3k2==cp2p3)\
#     .subs(cp1k2*cp2k2==cp1p2)\
#     .subs(cp1k3*cp1k3==1)

# c=c.subs(P4==-P3).subs(P3==P1)
# print c
print
# print "P2**2"
# print c.diff(P2,2)/2
print


# print "P1**2"
# print (c.diff(P1,2)/2).expand()
print

# print "P1*P2"
# print c.diff(P1,1).diff(P2,1)
print

print c.diff(P2,2)/2 + c.diff(P1,1).diff(P2,1)/2
