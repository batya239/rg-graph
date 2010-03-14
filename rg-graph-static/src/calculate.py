#!/usr/bin/python
# -*- coding: utf8 -*-

from phi3 import *
from multiprocessing import Process
import time

def execute_method(method, G, debug=False):
    if method in G.model.methods:
        G.model.methods[method](G, debug)
    else:
        raise NotImplementedError, "method %s not implemented for model %s" %(method, G.model.name)

if __name__ == '__main__':
    
    if "-graph" in sys.argv:
        g_list = [sys.argv[sys.argv.index('-graph')+1],]
    else:
        g_list = phi3.GraphList()
        
    if "-debug" in sys.argv:
        debug = True
    else:
        debug = False
        
    if "-target" in sys.argv:
        phi3.target = int(sys.argv[sys.argv.index('-target')+1])
        
    if "-method" in sys.argv:
        method = sys.argv[sys.argv.index('-method')+1]
    else:
        print "please provide -method <method> option"
        exit(1)
    
    if "-timeout" in sys.argv:
        timeout = float(sys.argv[sys.argv.index('-timeout')+1])
    else:
        timeout = 3600.
        
        
        
    for nickel in g_list:
        print "%s "%nickel,
        #rggrf.utils.print_debug(nickel, debug)
        G = rggrf.Graph(phi3)
        G.Load(nickel)
        G.GenerateNickel()
        G.FindSubgraphs()
        os.chdir(phi3.basepath+"/"+nickel)
        process = Process(target=execute_method, args=(method, G, debug))
        starttime=time.time()
        process.start()
        process.join(timeout)
        if process.is_alive():
            #rggrf.utils.print_debug("terminating %s"%nickel, debug)
            process.terminate()
            print " terminated"
        else:
            print " OK"

