#!/usr/bin/python

import sympy

import utils

w=sympy.var('w0 w1 w2 w3 w4 w5 w6 w7')
e, e1,  g=sympy.var('e e1 g')
c1=sympy.var('c1')
N=4
W=e
for i in range(2,N+1):
   W=W+w[i]*e**i
print (W/e).expand()    

i_w = ((utils.series_f(1/((W/e).expand()), e, N)-1)/e).expand()
i_W = utils.series_f(i_w,e,N).subs(e, e1)

gZ= utils.series_f(c1*e*sympy.exp(sympy.integrate(i_W, (e1, 0, e))), e, N)
print gZ

#print gZ.subs(w2, -0.629629629).subs(w3, 1.6182206).subs(c1, 1/3.)

gamma=sympy.var('gamma')

gamma_= utils.series_f(-g/c1*sympy.exp(sympy.integrate(i_W, (e1, 0, -gamma))), gamma, N-1)

print gamma_
print
res=0
for i in range(N):
    res=utils.series_f(gamma_.subs(gamma, res), g, i+1)
    print i,  res
    
r_str=""
for i in range(94):
    r_str+="r%s "%i
r=sympy.var(r_str)

r1=r[1]
r2=r[2]
r3=r[3]
r4=r[4]
r5=r[5]
r6=r[6]
r7=r[7]
r8=r[8]
r9=r[9]
r10=r[10]
r11=r[11]
r12=r[12]

w4_=(-0.000253939208809883*r1**3/r2**6 - 0.00744158462408191*r1**2/r2**4 + 0.0137140974178241*r1**2*r3/r2**6 + 0.0487924150336687*r1/r2**2 + 0.0745499319902718*r1*r3/r2**4 - 0.0209055449004418*r1*r4/r2**4 + 0.157926859272442*r1*r3/r2**5 - 0.0384923960946759*r1*r5/r2**5 + 0.186418195994931*r1*r6/r2**5 - 0.246878598578788*r1*r3**2/r2**6 + 0.747383944861562*r10/r2**4 - 0.0476807153690079*r11/r2**4 - 0.863662891433473*r12/r2**4 - 0.389110028587743*r13/r2**4 - 0.28674716518754*r14/r2**4 + 0.174700170381595*r3/r2**2 + 4.21675250788677*r3/r2**3 - 0.758602130105229*r5/r2**3 + 2.34545713754091*r6/r2**3 - 1.1945513460449*r3**2/r2**4 + 4.54163862663559*r8/r2**4 + 0.413564907177677*r9/r2**4 - 2.84296957410093*r3**2/r2**5 + 0.692932864210392*r3*r5/r2**5 - 3.35586525125592*r3*r6/r2**5 + 1.48142067682392*r3**3/r2**6) 
w3_=(0.00274285700923649*r1**2/r2**4 + 0.101812264551014*r1/r2**2 - 0.0987527904916615*r1*r3/r2**4 - 0.447962883452375*r3/r2**2 - 1.0661281762381*r3/r2**3 + 0.259853379194076*r5/r2**3 - 1.25846668659961*r6/r2**3 + 0.888864566859487*r3**2/r2**4) 
w2_=(-0.0370328030888595*r1/r2**2 + 0.666657545843249*r3/r2**2) 



res1=res.subs(c1, 1/(r[2]*3)).subs(w2, w2_).subs(w3, w3_).subs(w4, w4_).expand()
print res1

print
print utils.series_f(res1, g, 3)
