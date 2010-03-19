#!/usr/bin/python
# -*- coding: utf8 -*-

from phi3 import *
from multiprocessing import Process


def execute_method(method, G, debug=False):
    if method in G.model.methods:
        G.model.methods[method](G, debug)
    else:
        raise NotImplementedError, "method %s not implemented for model %s" %(method, G.model.name)

if __name__ == '__main__':

    def usage(progname):
        return "%s -model phi3R -method Method [-graph str_nickel] [-target N] [-timeout] [-debug]"
    
    if "-model" in sys.argv:
        model_module = sys.argv[sys.argv.index('-model')+1]
        try:
            exec('from %s import *'%model_module)
        except:
            print "Error while importing model!"
            sys.exit(1)
    else:
        print "Usage : %s " %usage(sys.argv[0])
        sys.exit(1)
    
    if "-graph" in sys.argv:
        g_list = [sys.argv[sys.argv.index('-graph')+1],]
    else:
        g_list = model.GraphList()
        
    if "-debug" in sys.argv:
        debug = True
    else:
        debug = False
        
    if "-target" in sys.argv:
        model.target = int(sys.argv[sys.argv.index('-target')+1])
        
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
        #print "%s "%nickel
        #rggrf.utils.print_debug(nickel, debug)
        G = rggrf.Graph(model)
        G.Load(nickel)
        G.GenerateNickel()
        G.FindSubgraphs()
        os.chdir(model.basepath+"/"+nickel)
        process = Process(target=execute_method, args=(method, G, debug))
        process.start()
        process.join(timeout)
        if process.is_alive():
            #rggrf.utils.print_debug("terminating %s"%nickel, debug)
            process.terminate()
            rggrf.utils.print_debug(" terminated", debug) 
        else:
            rggrf.utils.print_debug(" OK", debug)

