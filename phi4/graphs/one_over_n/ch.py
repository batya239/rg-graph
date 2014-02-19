#!/usr/bin/python
# -*- coding: utf8
import swiginac

__author__ = 'mkompan'

from rggraphenv.symbolic_functions import e, tgamma, series, var, Pi, zeta, Euler, safe_integer_numerators

D = 4-2*e


def H(*args):
    if len(args) == 1:
        a = args[0]
        return tgamma(D/2-a)/tgamma(a)
    else:
        res = 1
        for a in args:
            res = res * H(a)
        return res


def I135(alpha1, alpha2,alpha3, alpha4, alpha5):
    if alpha1 == alpha4 == alpha5:
        alpha = alpha1
        beta = alpha2
        gamma = alpha3
        #res = Pi**D*H(D-2)/tgamma(alpha)*(H(beta, 2-beta)/(gamma-1)/(2-beta-gamma)
        res = H(D-2)/tgamma(alpha)*(H(beta, 2-beta)/(gamma-1)/(2-beta-gamma)
                                     + H(gamma, 2-gamma)/(beta-1)/(2-beta-gamma)
                                     + H(beta+gamma-1, 3-beta-gamma)/(beta-1)/(gamma-1))
        return res
    else:
        raise NotImplementedError("%s %s %s %s %s " %(alpha1,alpha2,alpha3,alpha4,alpha5))


def IKaz(a1, a2, a3, a4, a5):
    aa = a1+a2+a3+a4
    aa2 = a1**2+a2**2+a3**2+a4**2
    aa3 = a1**3+a2**3+a3**3+a4**3
    aa4 = a1**4+a2**4+a3**4+a4**4
    A0 = 6
    A1 = 9
    A2 = 42+ 30*aa + 45*a5+10*aa2+15*a5**2+15*aa*a5 \
         + 10*(a1*a2+a3*a4+a1*a4+a2*a3) +5*(a1*a3+a2*a4)
    A3 = swiginac.numeric(5)/2*(A2-6)
    A4 = 46+42*aa+45*a5+14*aa2+15*a5**2+33*a5*aa+50*(a1*a2+a3*a4) \
         + 31*(a1*a3+a2*a4) + 14*(a1*a4+a2*a3)+6*a5*aa2++6*a5**2*aa+24*a5*(a1*a2+a3*a4) \
         + 12*a5*(a1*a3+a2*a4) + 12*(a1*a2*a3+a1*a2*a4+a1*a3*a4+a2*a3*a4) \
         + 12*(a1**2*a2+a2**2*a1+a3**2*a4+a4**2*a3) + 6 * (a1**2*a3+a3**2*a1+a2**2*a4+a4**2*a2)
    A5 = eval(safe_integer_numerators("294 + 402*aa + 2223/4*a5+260*aa2 + 3183/8*a5**2 + 516*a5*aa "
                                      "+ 386*(a1*a2+a3*a4+a1*a4+a2*a3) + 575/2*(a1*a3+a2*a4) + 84*aa3 + 567/4*a5**3 "
                                      "+ 168*(a1**2*a2+a2**2*a1+a3**2*a4+a4**2*a3+a1**2*a4+a4**2*a1+a2**2*a3+a3**2*a2)"
                                      "+ 441/4*(a1**2*a3+a3**2*a1+a2**2*a4+a4**2*a2) + 945/4*a5*aa2 + 252*a5**2*aa"
                                      "+ 693/2*a5*(a1*a2+a3*a4+a1*a4+a2*a3) + 945/4*(a1*a3+a2*a4)*a5 "
                                      "+ 210*(a1*a2*a3+a1*a2*a4+a1*a3*a4+a2*a3*a4)+ 14*aa4+189/8*a5**4"
                                      "+ 42*a5*aa3+189/4*a5**3*aa+ 525/8*a5**2*aa2 "
                                      "+ 357/4*a5**2*(a1*a2+a3*a4+a1*a4+a2*a3)"
                                      "+105/2*a5**2*(a1*a3+a2*a4)"
                                      "+84*a5*(a1**2*a2+a2**2*a1+a3**2*a4+a4**2*a3+a1**2*a4+a4**2*a1+a2**2*a3+a3**2*a2)"
                                      "+189/4*a5*(a1**2*a3+a3**2*a1+a2**2*a4+a4**2*a2)"
                                      "+ 357/4*a5*(a1*a2*a3+a1*a3*a4+a1*a2*a4+a2*a3*a4)"
                                      "+28*(a1**3*a2+a2**3*a1 +a3**3*a4+a4**3*a3+a1**3*a4+a4**3*a1+a2**3*a3+a3**3*a2) "
                                      "+14*(a1**3*a3+a3**3*a1+a2**3*a4+a4**3*a2)"
                                      "+ 42*(a1**2*a2**2+a3**2*a4**2+a1**2*a4**2+a2**2*a3**2) "
                                      "+ 189/8*(a1**2*a3**2+a2**2*a4**2)"
                                      "+ 42*(a1**2*(a2*a3+a2*a4+a3*a4)+a2**2*(a1*a4+a1*a3+a3*a4)"
                                      "     +a3**2*(a1*a4+a2*a4+a1*a2)+a4**2*(a2*a3+a1*a3+a1*a2))+315/4*a1*a2*a3*a4"))
    A6 = 3*(A4 - 1)

    res = swiginac.exp((-2*(Euler*e+zeta(2)/2*e*e)))/(1-2*e)
    res *= (A0*zeta(3)+A1*zeta(4)*e+A2*zeta(5)*e*e+A3*zeta(6)*e**3
            - A4*zeta(3)**2*e**3+A5*zeta(7)*e**4-A6*zeta(3)*zeta(4)*e**4
            + swiginac.Order(e**5))
    return res

print series(I135(1-e, 1-e, 1-e, 1-e, 1-e), e, 0, 2).expand()

print series(IKaz(-1,-1,-1,-1,-1),e,0,2).expand()

print series(I135(1-e, 1-e, 1-e, 1-e, 1-e) -IKaz(-1,-1,-1,-1,-1),e,0,6).expand()
print series(I135(1-e, 1-2*e, 1-8*e, 1-e, 1-e) -IKaz(-1,-2,-8,-1,-1),e,0,6).expand()