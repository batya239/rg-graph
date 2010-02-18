#!/usr/bin/python
# -*- coding: utf8

'''
Created on Feb 19, 2010

@author: mkompan
'''

def GenerateGinacCode(k_op, space_dim, n_epsilon_series, n_threads=4, mc_size=10000):
    atoms = k_op.atoms()
# TODO: p=1 m=1
# TODO: усреднение по направлениям p (eps)
# TODO: детерминанант по модулям (eps)
# TODO: инверсия по модулям (0-inf) -> (0 - 1)
# TODO: 
# TODO: разложение в ряд по eps
# TODO: вывод.
    pass

def old():
    from sympy import *
    from sympy.printing.ginac import *
    if "" not in sys.path:
        sys.path.append("")
    
    import graph_new
    
    d=6.0
    size=100000
    nthreads=4
    
    n_epsilon_series=int(open('.n_epsilon_series').read())
    #n_epsilon_series=3;
    moment=eval(open('moment').read())
    try:
        extern_lines=[l for l in eval(open('extern_lines').read())]
    except:
    #
    # в graph.new внешние линии могут определяться неправильно!!! проверить!!!
    #
        extern_lines=graph_new.extern_lines(moment[1],[m for m in moment[1]])
    
    
    symbol_perem=[]
    symbol_ext=[]
    
    print "//extern lines= ",extern_lines
        
    for tm in moment[1]:
        if tm not in extern_lines:
            symbol_perem.append(moment[0][tm])
        else:
            symbol_ext.append(moment[0][tm])
    
    
    symbol_ext='+'.join(symbol_ext).replace('-','+')
    symbol_ext=symbol_ext.split('+')
    symbol_ext=list(set(symbol_ext)-set('p'))
    print "//symbol ext=",symbol_ext
                
    symbol_perem='+'.join(symbol_perem).replace('-','+')
    symbol_perem=symbol_perem.split('+')
    symbol_perem=list(set(symbol_perem)-set(symbol_ext))
        
    def xcombinations(items, n):
        if n==0: yield []
        else:
            for i in xrange(len(items)):
                for cc in xcombinations(items[:i]+items[i+1:],n-1):
                    yield [items[i]]+cc
    
    symbol_angle=[]
    for c in xcombinations(symbol_perem,2):
        symbol_angle.append(''.join(c))
            
    symbol_angle=list(set(symbol_angle))
    
    print "//" + str( symbol_perem)
    symbol_int=list(set(symbol_perem)-set(['p','']))
    
    symbol_int.sort()
    print "//" +str (symbol_int)
    print "//" +str (symbol_angle)
    var(' '.join(symbol_angle))
    
    var('m')
    
    gamma=dict()
    if len(extern_lines)==2:
       base_filename="K2_R.gamma"
    elif len(extern_lines)==3:
       base_filename="K0_R.gamma"
    else:
       raise WrongExternLines, "wrong number of external lines"
    
    for i in range(20):
        try:
            expr=open(base_filename+str(i)).read()
        except: 
            continue
        exec(expr)
        gamma[str(i)]=e
        
    
    #print_python(gamma)
    
    print "#include <iostream>"
    print "#include <fstream>"
    print "#include <ginac/ginac.h>"
    print "using namespace std;"
    print "using namespace GiNaC;"
    print "int main(int argc, char **argv)"
    print "  {"
    print "    symbol e(\"e\");"
    print "    symbol m(\"m\");"
    print "    symbol p(\"p\");"
    for cur_imp in symbol_int:
       cur_inv=cur_imp.replace("q","y")
       print "symbol "+cur_inv+"(\""+cur_inv+"\");"
       print "symbol "+cur_imp+"(\""+cur_imp+"\");"
    for cur_ang in symbol_angle:
       print "symbol "+cur_ang+"(\""+cur_ang+"\");"
    
    line0="symbol"
    cur_num=0
    symbol_angel_int=[]
    for cur_imp in symbol_int[1:]:
       cur_num+=1
       ct_0_cur="ct_0_"+str(cur_num)
       symbol_angel_int.append(ct_0_cur)
       line0+=" " + ct_0_cur+"(\""+ct_0_cur+"\"),"
       if(cur_num>=2):
           ct_1_cur="ct_1_"+str(cur_num)
           symbol_angel_int.append(ct_1_cur)
           line0+=" " + ct_1_cur+"(\""+ct_1_cur+"\"),"
       if(cur_num>=3):
          ct_2_cur="ct_2_"+str(cur_num)
          symbol_angel_int.append(ct_2_cur)
          line0+=" " + ct_2_cur+"(\""+ct_2_cur+"\"),"
    
    if line0=="symbol":
       line0=""
    else:
       line0=line0[:-1]+";"
    print line0
    
    
    
    for i in gamma.keys():
       tmp=ginac(gamma[i])
       tmp=tmp.replace("symbol .*;","")
       tmp=tmp.replace("ex f =","ex f_"+i+"=")
       print tmp
    
       if len(extern_lines)==2:
          print "ex f1_"+i+"=normal(f_"+i+".subs(p==1.0).subs(m==1.0));"
          line="ex f2_"+i+"=(f1_"+i+".subs(lst("
          for cur_imp in symbol_int:
              line+="p"+cur_imp+"==0,"
          line=line[:-1]+"))"
    
          for cur_imp1 in symbol_int:
             line+="+f1_"+i+".diff(p"+cur_imp1+").diff(p"+cur_imp1+").subs(p"+cur_imp1+"==0).subs(p"+cur_imp1+"==0)/("+str(d)+"-e)/2.0"
             for cur_imp2 in symbol_int:
                if symbol_int.index(cur_imp1)<symbol_int.index(cur_imp2):
                    line+="+f1_"+i+".diff(p"+cur_imp1+").diff(p"+cur_imp2+").subs(p"+cur_imp1+"==0).subs(p"+cur_imp2+"==0)/("+str(d)+"-e)*"+cur_imp1+cur_imp2
          line+=");"
       elif len(extern_lines)==3:
          print "ex f1_"+i+"=normal(f_"+i+".subs(m==1.0));"
          line="ex f2_"+i+"=f1_"+i+";"
       else:
          raise WrongExternLines, "wrong number of external lines"
    
       print line
    
       line="ex f3_"+i+"=f2_"+i
       for cur_imp in symbol_int:
          line+="*pow("+cur_imp+","+str(d)+"-1.0-e)"
       line+=";"
       print line
       line="f3_"+i
       for cur_imp in symbol_int:
          cur_inv=cur_imp.replace("q","y")
          line="1.0/"+cur_inv+"/"+cur_inv+"*"+line+".subs("+cur_imp+"==(1.0-"+cur_inv+")/"+cur_inv+")"
       line="ex f4_"+i+"=" + line + ";\n";
       print line
       line="ex f5_"+i+"=f4_"+i
       line2="ex f6_"+i+"=f5_"+i
    
       cur_num=0
       for cur_imp in symbol_int[1:]:
          cur_num+=1
          ct_0_cur="ct_0_"+str(cur_num)
          line+=".subs(lst("+symbol_int[0]+symbol_int[cur_num]+"=="+ct_0_cur
          line2+="*pow(1-pow("+ct_0_cur+",2.0),("+str(d)+"-3.0-e)*0.5)"
          if(cur_num>=2):
              ct_1_cur="ct_1_"+str(cur_num)
              line+=","+symbol_int[1]+symbol_int[cur_num]+"=="+"ct_0_1*"+ct_0_cur+"+pow(1.0-pow(ct_0_1,2.0),0.5)*pow(1.0-pow("+ct_0_cur+",2.0),0.5)*"+ct_1_cur
              line2+="*pow(1.0-pow("+ct_1_cur+",2.0),("+str(d)+"-4.0-e)*0.5)"
          if(cur_num<3):
              line+="))"
          else:
     
              ct_2_cur="ct_2_"+str(cur_num)
              line+=","+symbol_int[2]+symbol_int[cur_num]+"==ct_0_2*"+ct_0_cur+"+pow(1.0-pow(ct_0_2,2.0),0.5)*pow(1.0-pow("+ct_0_cur+",2.0),0.5)*(ct_1_2*"+ct_1_cur+"+pow(1.0-pow(ct_1_2,2.0),0.5)*pow(1.0-pow("+ct_1_cur+",2.0),0.5)*"+ct_2_cur + ")"
              line2+="*pow(1.0-pow("+ct_2_cur+",2.0),("+str(d)+"-5.0-e)*0.5)"
              line+="))"
    
       line2+=";"
       line+=";"
       print line
       print line2
    n_int=len(symbol_int)+len(symbol_int)*(len(symbol_int)-1)/2
    tmp=1
    
    vars=""
    count=0
    reg={}
    for cur_imp in symbol_int:
       cur_inv=cur_imp.replace("q","y")
       vars+= "out <<\"double "+cur_inv+"=k["+str(count)+"];\" << endl;\n"
       reg[count]=0
       reg[count+n_int]=1
       count+=1
    for cur_ang in symbol_angel_int:
        vars+="out <<\" double "+cur_ang+"=k["+str(count)+"];\" << endl;\n";
        reg[count]=-1
        reg[count+n_int]=1
        count+=1
    #for i in gamma.keys():
    #    vars+="cout <<\"double f_"+i+"[FUNCTIONS];\" <<endl;\n";
    
    region="out <<\"double reg[2*DIMENSION]= {"
    for i in range(2*n_int):
        region+=str(reg[i])+".0,"
    region=region[:-1]+"};\"<<endl;\n;"
    
    print "ofstream out;"
    print "char str[20];"
    print "int i;\n   for(i=1;i<="+str(n_epsilon_series+1)+";i++)\n      {\n  " 
    print "sprintf(str,\"function_%d.h\",i-1);"
    print "out.open(str,ios::trunc);\n"
    print "out <<endl<<\"//--\"<< i-1 <<\"---\"<<endl;"
    print "out <<\"#define DIMENSION "+str(n_int)+"\"<< endl << \"#define FUNCTIONS "+str(tmp) +"\"<<endl<<\"#define ITERATIONS "+str(size)+"\"<<endl<<\"#define NTHREADS "+str(nthreads)+"\"<< endl<<\"#define NEPS \"<<i-1<<endl;\n"
    print region 
    
    print "out << \"void func (double k[DIMENSION], double f[FUNCTIONS]) {\" << endl;\n"
    print vars
    print "out << csrc_double << endl << \"double tmp=0.0;\";\n"
    for i in gamma.keys():
        print " out << \"tmp += \" << f6_"+i+".subs(e==0) << \";\" << endl;\n"
    print "out  << \"f[0]=tmp;\";\n"
    
    #print "cout << \"return f_res;  }\" << endl;\n";
    
    for i in  gamma.keys():
        print "      f6_"+i+" = f6_"+i+".diff(e)/(double(i));";
     
    
    print "out << \"  }\" << endl;\n"
    print "out.close();\n"
    print "   }\n"
    
    #print "cout <<\"return 0;}\"<<endl;\n";
    print "}\n"
    
    #print "cout << \"//\"<< f2 << endl;\n";
    #print "}"    
