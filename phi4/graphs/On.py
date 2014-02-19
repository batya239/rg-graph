#!/usr/bin/python

import sys
import sympy

from dummy_model import _phi3,_phi4
from graphs import Graph
import utils
from copy import copy

def vertex_strucutre(lst):
    """ generate vertex strucutre for node. lst - list of line numbers (len=4 for phi4)
    """
#    print "lst=", lst
    if len(lst)<>4:
        raise ValueError,  "for phi4 model len(lst)==4 !!"
    a, b, c, d=tuple(lst)
    res=[[a, b, c, d], [a, c, b, d], [a, d, b, c]]
    
    sympy_res=sympy.Number(0)
    for term in res:
        d1, d2=sympy.var('d_%s_%s d_%s_%s'%tuple(term))
        sympy_res+=d1*d2
#    print sympy_res
    return sympy_res
    
def On(graph):
    res=sympy.Number(1)
    factor=sympy.Number(1)
    for node in graph.xInternalNodes():
        res=res*vertex_strucutre([i.idx() for i in node.Lines()])
        factor=factor/3
    for line in graph.ExternalLines():
        phi=sympy.var('phi_%s'%line.idx())
        res=res*phi
#    return utils.kronecker.contract(res)*factor
    return utils.kronecker.contract(res)
            


def reduce_to_r(expr):
    r_str='n'
    for i in xrange(1, 96):
        r_str+=' r%s'%i
    r=sympy.var(r_str)
    n=r[0]
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
       3*n**5 + 36*n**4 + 180*n**3 + 480*n**2 + 752*n + 736 : r[92]*2187,

       n**5 + 12*n**4 + 60*n**3 + 160*n**2 + 240*n + 256    : r[93]*729,
       }
    res=expr
    if isinstance(expr, sympy.Mul):
        res=sympy.Number(1)
        for arg in expr.args:
            if isinstance(arg, sympy.Add):
                if arg in r_map.keys():
                    res=res*r_map[arg]
                else:
                    res=res*arg
            else:
                res=res*reduce_to_r(arg)
    elif isinstance(expr, sympy.Pow):
        arg1, arg2=expr.args
        res=reduce_to_r(arg1)**arg2
    elif isinstance(expr, sympy.Add):
        if expr in r_map.keys():
            return r_map[expr]
        else:
            return expr
    return res
        


phi4 = _phi4('dummy')
g1 = Graph(sys.argv[1])
O = On(g1)
#print O
#print
#print sympy.simplify(O)
#print
O1=sympy.factor(O)
print O1
phi__=sympy.var('phi')
O2=sympy.factor(O1.subs(phi__, 1))

#print O2,  type(O2), O2.args    
Nnodes=len([i for i in g1.xInternalNodes()])
print reduce_to_r(O2)/3**Nnodes
