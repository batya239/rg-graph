#!/usr/bin/python

import sympy

import utils
r_str=""
for i in range(94):
    r_str+="r%s "%i
r=sympy.var(r_str)
n=sympy.var('n')
r_map={
   n+2                          :   r[1]*3,  
   n+8                          :   r[2]*9,
   5*n+22                       :   r[3]*27, 
   n*n+6*n+20                   :   r[4]*27, 
   3*n*n+22*n+56                :   r[5]*81, 
   n*n+20*n+60                  :   r[6]*81, 
   n*n*n+8*n*n+24*n+48          :   r[7]*81, 
   
   2*n**2 + 55*n + 186                  :   r[8]*243, 
   3*n**3 + 24*n**2 + 80*n + 136        :   r[9]*243, 
   7*n**2 + 72*n + 164                  :   r[10]*243, 
   11*n**2 + 76*n + 156                 :   r[11]*243, 
   n**3 + 10*n**2 + 72*n + 160          :   r[12]*243, 
   n**3 + 14*n**2 + 76*n + 152          :   r[13]*243, 
   n**3 + 18*n**2 + 80*n + 144          :   r[14]*243,        
   n**4 + 10*n**3 + 40*n**2 + 80*n + 112:   r[15]*243, 

   14*n**2 + 189*n + 526                    : r[16]*729, 
   19*n**2 + 206*n + 504                    : r[17]*729,        
   n**3 + 26*n**2 + 210*n + 492             : r[18]*729,
   n**3 + 32*n**2 + 224*n + 472             : r[19]*729,
   n**3 + 36*n**2 + 244*n + 448             : r[20]*729,
   n**3 + 44*n**2 + 252*n + 432             : r[21]*729,  
   3*n**3 + 38*n**2 + 224*n + 464           : r[22]*729, 
   3*n**3 + 42*n**2 + 244*n + 440           : r[23]*729, 
   3*n**3 + 50*n**2 + 252*n + 424           : r[24]*729, 
   5*n**3 + 56*n**2 + 252*n + 416           : r[25]*729, 
   5*n**3 + 64*n**2 + 260*n + 400           : r[26]*729, 
   9*n**3 + 76*n**2 + 260*n + 384           : r[27]*729,       
   n**4 + 16*n**3 + 88*n**2 + 256*n + 368   : r[28]*729,
   n**4 + 16*n**3 + 96*n**2 + 264*n + 352   : r[29]*729,       
   n**4 + 12*n**3 + 68*n**2 + 248*n + 400   : r[30]*729,
   n**4 + 12*n**3 + 76*n**2 + 256*n + 384   : r[31]*729,
   3*n**4 + 30*n**3 + 120*n**2 + 256*n + 320: r[32]*729,        

   53*n**2 + 598*n + 1536                               : r[33]*2187,
   n**3 + 65*n**2 + 619*n + 1502                        : r[34]*2187,       
   2*n**3 + 76*n**2 + 643*n + 1466                      : r[35]*2187, 
   2*n**3 + 87*n**2 + 674*n + 1424                      : r[36]*2187,
   2*n**3 + 89*n**2 + 668*n + 1428                      : r[37]*2187,
   2*n**3 + 97*n**2 + 708*n + 1380                      : r[38]*2187,       
   3*n**3 + 78*n**2 + 630*n + 1476                      : r[39]*2187,
   4*n**3 + 111*n**2 + 716*n + 1356                     : r[40]*2187,
   5*n**3 + 100*n**2 + 678*n + 1404                     : r[41]*2187,
   5*n**3 + 110*n**2 + 712*n + 1360                     : r[42]*2187,       
   7*n**3 + 114*n**2 + 686*n + 1380                     : r[43]*2187,
   7*n**3 + 124*n**2 + 720*n + 1336                     : r[44]*2187,
   7*n**3 + 136*n**2 + 748*n + 1296                     : r[45]*2187,
   9*n**3 + 138*n**2 + 728*n + 1312                     : r[46]*2187, 
   9*n**3 + 150*n**2 + 756*n + 1272                     : r[47]*2187,
   9*n**3 + 158*n**2 + 796*n + 1224                     : r[48]*2187,
   9*n**3 + 174*n**2 + 812*n + 1192                     : r[49]*2187,       
   11*n**3 + 128*n**2 + 680*n + 1368                    : r[50]*2187, 
   11*n**3 + 148*n**2 + 748*n + 1280                    : r[51]*2187, 
   13*n**3 + 150*n**2 + 728*n + 1296                    : r[52]*2187, 
   13*n**3 + 162*n**2 + 756*n + 1256                    : r[53]*2187, 
   13*n**3 + 170*n**2 + 796*n + 1208                    : r[54]*2187, 
   13*n**3 + 186*n**2 + 812*n + 1176                    : r[55]*2187, 
   15*n**3 + 164*n**2 + 736*n + 1272                    : r[56]*2187, 
   17*n**3 + 182*n**2 + 796*n + 1192                    : r[57]*2187, 
   17*n**3 + 198*n**2 + 812*n + 1160                    : r[58]*2187, 
   21*n**3 + 226*n**2 + 828*n + 1112                    : r[59]*2187, 
   29*n**3 + 250*n**2 + 828*n + 1080                    : r[60]*2187,  
   3*n**4 + 36*n**3 + 204*n**2 + 744*n + 1200           : r[61]*2187,
   3*n**4 + 36*n**3 + 228*n**2 + 800*n + 1120           : r[62]*2187,
   3*n**4 + 40*n**3 + 232*n**2 + 760*n + 1152           : r[63]*2187,
   3*n**4 + 40*n**3 + 240*n**2 + 800*n + 1104           : r[64]*2187,
   3*n**4 + 40*n**3 + 256*n**2 + 816*n + 1072           : r[65]*2187,
   3*n**4 + 44*n**3 + 268*n**2 + 816*n + 1056           : r[66]*2187,
   3*n**4 + 44*n**3 + 284*n**2 + 832*n + 1024           : r[67]*2187,
   3*n**4 + 48*n**3 + 280*n**2 + 816*n + 1040           : r[68]*2187,
   3*n**4 + 52*n**3 + 308*n**2 + 832*n + 992            : r[69]*2187,
   5*n**4 + 62*n**3 + 304*n**2 + 808*n + 1008           : r[70]*2187,
   5*n**4 + 62*n**3 + 320*n**2 + 824*n + 976            : r[71]*2187,
   9*n**4 + 90*n**3 + 368*n**2 + 808*n + 912            : r[72]*2187,       
   n**4 + 14*n**3 + 144*n**2 + 724*n + 1304             : r[73]*2187,
   n**4 + 14*n**3 + 164*n**2 + 792*n + 1216             : r[74]*2187,
   n**4 + 14*n**3 + 180*n**2 + 808*n + 1184             : r[75]*2187,
   n**4 + 18*n**3 + 156*n**2 + 724*n + 1288             : r[76]*2187,
   n**4 + 18*n**3 + 168*n**2 + 752*n + 1248             : r[77]*2187,
   n**4 + 18*n**3 + 176*n**2 + 792*n + 1200             : r[78]*2187,
   n**4 + 22*n**3 + 180*n**2 + 752*n + 1232             : r[79]*2187,
   n**4 + 22*n**3 + 204*n**2 + 808*n + 1152             : r[80]*2187,
   n**4 + 26*n**3 + 196*n**2 + 740*n + 1224             : r[81]*2187,
   n**4 + 26*n**3 + 208*n**2 + 768*n + 1184             : r[82]*2187,
   n**4 + 26*n**3 + 216*n**2 + 808*n + 1136             : r[83]*2187,
   n**4 + 26*n**3 + 232*n**2 + 824*n + 1104             : r[84]*2187,
   n**4 + 30*n**3 + 228*n**2 + 808*n + 1120             : r[85]*2187,
   n**4 + 30*n**3 + 244*n**2 + 824*n + 1088             : r[86]*2187,
   n**5 + 14*n**4 + 84*n**3 + 312*n**2 + 784*n + 992    : r[87]*2187,
   n**5 + 14*n**4 + 92*n**3 + 336*n**2 + 784*n + 960    : r[88]*2187,
   n**5 + 14*n**4 + 92*n**3 + 352*n**2 + 800*n + 928    : r[89]*2187,
   n**5 + 18*n**4 + 120*n**3 + 400*n**2 + 784*n + 864   : r[90]*2187,
   n**5 + 18*n**4 + 120*n**3 + 416*n**2 + 800*n + 832   : r[91]*2187, 
   3*n**5 + 36*n**4 + 180*n**3 + 480*n**2 + 752*n + 736 : r[92]*2187
   }
   
rr_map=dict()
for rn in r_map:
    f,  r_=r_map[rn].args
#    print r_,  f
    rr_map[r_]=rn/f







w=sympy.var('w0 w1 w2 w3 w4 w5 w6 w7')
e, e1,  g=sympy.var('e e1 g')
c1=sympy.var('c1')
N=4
W=e
for i in range(2,N+1):
   W=W+w[i]*e**i
   

i_w = ((utils.series_f(1/((W/e).expand()), e, N)-1)/e).expand()
i_W = utils.series_f(i_w,e,N).subs(e, e1)
print i_W

gZ= utils.series_f(c1*e*sympy.exp(sympy.integrate(i_W, (e1, 0, e))), e, N)
print "g* = ",  gZ

#print gZ.subs(w2, -0.629629629).subs(w3, 1.6182206).subs(c1, 1/3.)

gamma=sympy.var('gamma')

gamma_= utils.series_f(-g/c1*sympy.exp(sympy.integrate(-i_W, (e1, 0, -gamma))), gamma, N-1)

print "gamma_ ",  gamma_
print
res=0
for i in range(0, N):
    res=utils.series_f(gamma_.subs(gamma, res), g, i+1)
    print i,  res
gammaG_w=res
print
print "gammaG=", res
print


gH_2=0
gH_1=0
for i in range(2, N + 1):
    for j in range(N-i+1):
        hij=sympy.var('h%s_%s'%(i, j))
        gH_2+=hij*g**i*e**j
i=1
for j in range(N):
        hij=sympy.var('h%s_%s'%(i, j))
        gH_1+=hij*e**j


gH_tosolve=(-e-gH_2)/gH_1


print gH_tosolve
gZ_res=0
for i in range(0, N):
    gZ_res=utils.series_f(gH_tosolve.subs(g, gZ_res), e, i+1)
    print i, gZ_res

print 
print "g*=", gZ_res
print

omega=-g*(e+g*gH_1+gH_2).diff(g)
print "omega ", omega
print
omega_=utils.series_f(omega.subs(g, gZ_res), e, N)
omega_i=utils.series_lst(omega_.subs(g, gZ_res), e, N)
print omega_i

print
gammaG=utils.series_f(res.subs(w2, omega_i[2]).subs(w3, omega_i[3]).subs(w4, omega_i[4]).subs(c1, -0.5/sympy.var('h1_0')), g, N)  # 2??
print "gammagG=", gammaG
gammaG_NP=(
           e**4*(0.0125785894539531*g**4*r1**2 + 0.0244664827532654*g**4*r1*r2**2 - 0.203379923855108*g**4*r1*r3 + 0.0462377463256604*g**3*r1*r2) 
           + e**3*(-0.0169403753361917*g**4*r1**2 - 0.0543414384839708*g**4*r1*r2**2 + 0.277588662881174*g**4*r1*r3 - 0.0717760375468434*g**3*r1*r2 
                   + 0.308425137312248*g*r2) 
           + e**2*(0.0150492366991987*g**4*r1**2 + 0.0703122977658966*g**4*r1*r2**2 - 0.254365907271113*g**4*r1*r3 + 0.125286908115665*g**3*r1*r2 
                   - 0.224308621804452*g**2*r1 + 3.62678745416055*g**2*r3 - 0.616850274624496*g*r2) 
           + e*(-0.00629313277497334*g**4*r1**2 - 0.132142532832557*g**4*r1*r2**2 + 0.108883359585485*g**4*r1*r3 - 0.40809562828402*g**3*r1*r2 
                + 6.43859494845474*g**3*r3 - 1.94114008372852*g**3*r5 + 7.13974525137978*g**3*r6 + 0.151045244716095*g**2*r1 - 2.50790918535522*g**2*r3 
                + 0.74999999946066*g*r2) 
           + 0.0128519864336552*g**4*r1**2 + 0.331742167619902*g**4*r1*r2**2 - 0.445150718864824*g**4*r1*r3 - 0.0339567027763824*g**4*r1*r4 
           + 1.3322988318821*g**4*r10 - 0.0464861951294422*g**4*r11 - 1.45023319036459*g**4*r12 - 0.645365935620574*g**4*r13 - 0.482640945053168*g**4*r14 
           + 3.30387629715355*g**4*r2*r3 + 7.66544260402541*g**4*r8 + 0.708205994267152*g**4*r9 + 0.121276268021738*g**3*r1*r2 - 1.79859289190365*g**3*r3 
           + 0.438514092784669*g**3*r5 - 2.12152048330189*g**3*r6 - 0.0833277841590041*g**2*r1 + 1.49991430369165*g**2*r3 - 1.49999999892132*g*r2
           )

gammaG_NP_g=utils.series_lst(gammaG_NP, g, N)
gammaG_=gammaG
for i in range(len(gammaG_NP_g)):
    term=utils.series_lst(gammaG_NP_g[i], e, N-i) 
    if term <>0:
        for j in range(len(term)):
            term_=term[j]
            hij=sympy.var('h%s_%s'%(i, j))
            print "%s %s = %s"%(i, j, term_)
            gammaG_=gammaG_.subs(hij, term_)
        
gammaG__=utils.series_f(gammaG_.subs(c1, 1/(3*r2)).expand(), g, N)
print
print gammaG__
gammaG_n1=gammaG__
for i in range(15):
    gammaG_n1=gammaG_n1.subs(r[i], 1)

print 
print gammaG_n1


gammaG_n2=gammaG__
for r in rr_map:
    gammaG_n2=gammaG_n2.subs(r, rr_map[r])
print
for i in range(N+1):
    print "g**i ", utils.series_f(utils.series_lst(gammaG_n2, g, N)[i]*3888, n, 2*N) 
#print utils.series_f(utils.series_lst(gammaG_n2, g, N)[4]*3888, n, 2*N).subs(n, 1)
#print (rr_map[r[2]]*rr_map[r[3]]*3-rr_map[r[5]]-2*rr_map[r[6]]).expand()
