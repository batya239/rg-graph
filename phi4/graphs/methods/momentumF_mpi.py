#!/usr/bin/python

#from momentumF import Prepare,  save,  compile, execute,   result
import momentumF
import calculate

save=momentumF.save
compile=momentumF.compile
execute=momentumF.execute
result=momentumF.result



#global method_name
momentumF.method_name="momentumF_mpi"
momentumF.code_=calculate.core_pvmpi_code
momentumF.compile_=calculate.compile_mpi
momentumF.execute_=calculate.execute_mpi
