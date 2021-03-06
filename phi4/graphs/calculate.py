#!/usr/bin/python
# -*- coding:utf8
import os
import roperation
import sympy
import utils
import subprocess
import fnmatch
import re as regex
import time
from graphs import Graph




def result(model, method,  normalize=lambda y, x:x, struct=None):
    res=dict()
    err=dict()
    e=sympy.var('e')
    method_=method
    regex_=regex.match('methods.(.*)', method_)
    if regex_:
        method_=regex_.groups()[0]
    os.chdir(model.workdir+"/%s/"%method_)
    for file in os.listdir('.'): 
        try:
            f=open("%s/result"%(file),'r')
            g=Graph(file)
            nloop=g.NLoops()
            n_ext=len(g.ExternalLines())
    
            answ=eval(f.read())

            res_,err_=normalize(g, answ)
#            print file, res_,err_

            f.close()
            if n_ext not in res.keys():
                res[n_ext]=dict()
                err[n_ext]=dict()            
                
            g_res=res[n_ext]
            g_err=err[n_ext]
            
        
            if not nloop in g_res:
                g_res[nloop]=0.
                g_err[nloop]=0.

            if struct<>None:
                struct_=struct[file]
            else:
                struct_=1

            g_res[nloop]+=reduce(lambda x,y: x+y, [res_[x]*e**x for x in range(len(res_))])*struct_
            g_err[nloop]+=reduce(lambda x,y: x+y, [err_[x]*e**x for x in range(len(err_))])*struct_
        except IOError:
            pass
    return (res, err)
    
    
def _execute(name, model, points=10000, threads=2, calc_delta=0., neps=0, start_arg_lst=list()):
    dirname = '%s/%s/'%(model.workdir,name)
    MAXPOINTS=10**9
    if points >= MAXPOINTS:
        iterations = 2*int(points/MAXPOINTS)
        points = MAXPOINTS
    else:
        iterations = 2
    os.chdir(dirname)
    filelist=os.listdir(".")
    result=[]
    error=[]
    for n in range(neps+1):
        result.append(0.)
        error.append(0.)
        for file in filelist:
            if fnmatch.fnmatch(file,"*E%s_*.run"%n):
                arg_lst=start_arg_lst + ["./%s"%file, "%s"%points, "%s"%threads]
                arg_lst.append(str(iterations))
                if calc_delta<>0:
                    arg_lst.append("%s"%calc_delta)
                process = subprocess.Popen(arg_lst, shell=False, 
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                exit_code = process.wait()
                (std_out,std_err) = process.communicate()
                if exit_code<>0:
                    raise Exception,  "Failed while executing %s"%file
                res,err=parse_output(std_out)
                if res==None or err==None:
                    raise ValueError, "Failed while parsing %s output:%s"%(file, std_out)
                result[n]+=res
                error[n]+=err
    time_str=time.strftime("-%Y-%m-%d-%H:%M:%S")
    f=open("result_%s"%time_str,'w')
    g=open("result",'w')
    f.write(str((result,error)))
    g.write(str((result,error)))
    f.close()
    g.close()
    f=open("points_%s"%time_str,'w')
    g=open("points",'w')
    f.write(str(points))
    g.write(str(points))
    f.close()
    g.close()
    return (result, error)

def execute(name, model, **kwargs):
    return _execute(name, model, **kwargs)

def execute_mpi(name, model, **kwargs):
    return _execute(name, model, start_arg_lst=["mpirun", "-np", "%s"%kwargs["threads"]], **kwargs)


def parse_output(stdout):
    res=None
    err=None
    for line in stdout.splitlines():
        reg = regex.match("^result = (.+)$", line)
        if reg:
            if 'nan' not in reg.groups()[0]:
                res = float(reg.groups()[0])
        reg = regex.match("^std_dev = (.+)$", line)
        if reg:
            if 'nan' not in reg.groups()[0]:
                err = abs(float(reg.groups()[0]))
    return (res, err)

def _compile(name,model, options=list(), cc="gcc"):
    dirname = '%s/%s/'%(model.workdir,name)
    os.chdir(dirname)
    for file in os.listdir("."):
        if fnmatch.fnmatch(file,"*.c"):
            print "Compiling %s ..."%file,
            prog_name=file[:-2]+".run"
            process = subprocess.Popen(["rm", "-f", prog_name], shell=False, 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = process.wait()
            (std_out, std_err) = process.communicate()
            process = subprocess.Popen([cc, file] + options + ["-o", prog_name], shell=False, 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = process.wait()
            (std_out, std_err) = process.communicate()

            if exit_code <> 0 :
                print "FAILED"
            else: 
                if len(std_err) == 0:
                    print "OK"
                else:
                    print "CHECK"
                    print std_err
                        
    return

def compile(name,model):
    _compile(name, model, options=["-lm", "-lpthread", "-lpvegas", "-O2"])

def compile_mpi(name,model):
    _compile(name, model, options=["-lm", "-lpvegas_mpi", "-O2"], cc="mpicc")

def save(name, graph, model, overwrite=True):
    dirname = '%s/%s/'%(model.workdir,name)
    try:
        os.mkdir(dirname)
    except:
        if overwrite:
            file_list = os.listdir(dirname)
            for file in file_list:
                if fnmatch.fnmatch(file,"*.c") or fnmatch.fnmatch(file,"*.run"):
                    os.remove(dirname+file)

    jakob,subsvars = roperation.subs_vars(graph)
    cnt=0
    d,e=sympy.var('d e')
    if "_nloops_orig" in graph.__dict__:
        _nloops_orig=graph._nloops_orig
    else:
        _nloops_orig=graph.NLoops()
    print "norm start"
    norm=utils.series_f(utils.norm(graph.NLoops(),model.space_dim-e)*graph.sym_coef(), e, model.target-_nloops_orig)
    print norm
    print utils.series_f(utils.norm(graph.NLoops(),model.space_dim-e), e, model.target-_nloops_orig), graph.sym_coef()
    for g in model.dTau(graph):
        roperation.strechMoments(g, model)
        print cnt, g
        det=roperation.det(g, model)
        #expr=(jakob*det*roperation.AvgByExtDir(roperation.expr(g,model))).subs(d, model.space_dim-e)
        expr=(norm*jakob*det*roperation.AvgByExtDir(roperation.expr(g,model))).subs(d, model.space_dim-e)
        strechs=roperation.find_strech_atoms(expr)
        eps_cnt=0


        for _expr in utils.series_lst(expr,e,model.target-_nloops_orig):
            integrand=roperation.export_subs_vars_pv(subsvars,strechs)
            integrand+= "\nf[0]=1.0e-38;\n"
            integrand+= "f[0]+=%s;\n"%sympy.printing.ccode(_expr)
            f=open('%s/%s_E%s_%s.c'%(dirname,name,eps_cnt,cnt),'w')
            f.write(core_pv_code(integrand))
            f.close()
            eps_cnt+=1
        cnt+=1  
    


def core_pv_code(integrand, mpi=False):
    a1="""#include <math.h>
#include <stdio.h>
#include <vegas.h>
#include <stdlib.h>
#include <time.h>
#define gamma tgamma
"""
    if mpi:
        a1+="#include <mpi.h>\n"
    a1=a1+integrand
    a1=a1+ """ }



int t_gfsr_k;
unsigned int t_gfsr_m[SR_P];
double gfsr_norm;


int main(int argc, char **argv)
{
  int i;
  long long npoints;
  int nthreads;
  int niter;
  double region_delta;
  double reg[2*DIMENSION];
  int idx;
  if(argc >= 2)
    {
      npoints = atoll(argv[1]);

    }
  else 
    {
      npoints = ITERATIONS;
    }

  if(argc >= 3)
    {
      nthreads = atoi(argv[2]);

    }
  else 
    {
      nthreads = NTHREADS;
    }
   
   if(argc >= 5)
    {
      region_delta = atof(argv[4]);

    }
  else 
    {
      region_delta = 0.;
    } 

  if(argc >= 4)
    {
      niter = atoi(argv[3]);

    }
  else 
    {
      niter = NITER;
    }    
    
    for(idx=0; idx<2*DIMENSION; idx++)
      {
         if(idx<DIMENSION)
           {
             reg[idx] = reg_initial[idx]+region_delta;
           }
         else
           {
             reg[idx] = reg_initial[idx]-region_delta;
           }
      }
      
  double estim[FUNCTIONS];   /* estimators for integrals                     */
  double std_dev[FUNCTIONS]; /* standard deviations                          */
  double chi2a[FUNCTIONS];   /* chi^2/n                                      */
    clock_t start, end;
    double elapsed;
    start = clock();
"""
    if mpi:
        a1+="""
    MPI_Init(&argc, &argv);
"""

    a1+="""
  vegas(reg, DIMENSION, func,
        0, npoints/10, 5, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
  vegas(reg, DIMENSION, func,
        2, npoints , niter, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
    int rank=0;
"""
    if mpi:
        a1+="""

    MPI_Comm_rank(MPI_COMM_WORLD,&rank);
    MPI_Finalize();
"""
    a1+="""
    if(rank==0) {
        end = clock();
        elapsed = ((double) (end - start)) / CLOCKS_PER_SEC;
        double delta= std_dev[0]/estim[0];
        printf ("result = %20.18g\\nstd_dev = %20.18g\\ndelta = %20.18g\\ntime = %20.10g\\n", estim[0], std_dev[0], delta, elapsed);
    }
    return(0);
}
"""



    return a1

def core_pvmpi_code(integrand):
    return core_pv_code(integrand, mpi=True)
