import sympy
from Gfunc import G, e
from normed5loop import MS

#e1123-e24--445-5--

print MS['ee12-223-4-445-5-ee-'].evalf()

I1 = G(1, 1) * G(2, e) * G(2 + 2 * e, 1) * G(1, 2) * G(1 + 3 * e, 1 + e)
I4 = MS['ee12-e22-e-'] * G(2, 1) * G(2, 1) * G(1 + e, 1 + e)

res_ = (I1 - I4).series(e, 0, 0).removeO()

#11--
delta_i_1 = 1 / e
print "11--", delta_i_1

#11-22--
delta_i_2 = MS['ee11-22-ee-'] + 2 / e * delta_i_1
print "11-22--", delta_i_2


#11-22-33--
delta_i_3 = MS['ee11-22-33-ee-'] + 3 / e * delta_i_2 + 2 * MS['ee11-22-ee-'] * delta_i_1 - 1 / e / e * delta_i_1
print "11-22-33--", delta_i_3

#1123-23---
delta_i_4 = MS['ee12-223-3-ee-'] + 1 / e * delta_i_2 + 2 * MS['ee12-e22-e-'] * delta_i_1
print "1123-23---", delta_i_4







#e112-e2--
r1a1 = G(1, 1) * G(2, e)
r_term_1 = ((r1a1 - MS['ee12-e22-e-']) * (delta_i_4 - 1 / e * delta_i_2 - MS['ee12-e22-e-'] * delta_i_1)).series(e, 0,
                                                                                                                0).removeO()
print "S e112-e2--", (delta_i_4 - 1 / e * delta_i_2 - MS['ee12-e22-e-'] * delta_i_1).series(e, 0, 0).evalf()

#e112-e3-33--
r1a2 = G(1, 1) * G(2 + e, e) * G(1, 1) - 1 / e * G(2, 1) * G(1 + e, 1)

r_term_2 = ((r1a2 - MS['e112-e3-e33-e-']) * delta_i_2).series(e, 0, 0).removeO()
print "S e112-e3-33--", delta_i_2.evalf()

#e112-e3-334-4--
r1a3 = G(2, 1) * G(1 + e, 1) * G(2 + 2 * e, e) * G(1, 1) - MS['ee12-e22-e-'] * (G(1, 1) * G(2, e))
r_term_3 = ((r1a3 - MS['ee12-223-4-e44-e-']) * delta_i_1).series(e, 0, 0).removeO()
print "S e112-e3-334-4--", delta_i_1

#e1123-e24-44--

r1a4 = G(1, 1) * G(2 + e, 1) * G(2, 1) * G(1 + 2 * e, 1 + e) - 1 / e * G(2, 1) ** 2 * G(1 + e, 1 + e)
r_term_4 = ((r1a4 - MS['ee12-223-4-e44-e-']) * delta_i_1).series(e, 0, 0).removeO()
print "S e1123-e24-44--", delta_i_1

res = res_ + r_term_1 + r_term_2 + r_term_3 + r_term_4
print res.evalf()