#!/usr/bin/python
# encoding: utf8

## Исполняем все cuba-файлы 

## Параметры cuba:
EpsRel = '1e-5'
EpsAbs = '1e-10'
MaxPoints = '1e6'
Method  = 'cuhre' ## one of: 'vegas', 'suave', 'divonne', 'cuhre'

def method_num(method):
    if method   == 'vegas': return '0'
    elif method == 'suave': return '1'
    elif method == 'divonne': return '2'
    elif method == 'cuhre': return '3'

import os

CUR_DIR = os.getcwd()
print CUR_DIR

#WORKDIR=$HOME'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
WORKDIR = '/home/kirienko/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'


#cd $WORKDIR
os.chdir(WORKDIR)

for d in [ d for d in os.listdir('.') if os.path.isdir(d) ]:
        print 'Processing', d, '...'
        os.chdir(os.path.join(WORKDIR,d))
        #./cuba.run 3 10000000 EpsRel EpsAbs > out_${PWD##*/}_10M_e-5_e-12_$METHOD
        cmd = ' '.join(('./cuba.run', method_num(Method), MaxPoints, EpsRel, EpsAbs, \
                        '>', '_'.join(('out', d, MaxPoints, EpsRel, EpsAbs, Method)) \
                        ))
        print cmd
        os.system(cmd)
        os.chdir('..')

#cd $CUR_DIR
os.chdir(CUR_DIR)
#python get_answer.py $METHOD
#python compare.py $METHOD
