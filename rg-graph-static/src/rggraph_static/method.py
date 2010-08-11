#!/usr/bin/python

'''
Created on Aug 10, 2010

@author: mkompan
'''

class option:
    def __init__(self,name, type_, default):
        self.name = name
        self.type = type_
        self.value = self.type(default)
        
    def get_value(self,argv):
        if "-"+self.name in argv:
            if self.type <> bool:
                self.value= self.type(argv[argv.index('-'+self.name)+1])
            else:
                self.value =  not self.value
# TODO: спорное решение ^^


class method:
    def __init__(self, name, argv, options=list(), generate_expr=None, 
                 generate_code=None, compile=None, execute = None):
        
        self.name = name
        self.options = options
        for option in self.options:
            option.get_value(argv)
        
        try:
            tmp = self.get_option_value("code_ext")
            tmp = self.get_option_value("exec_ext")
        except:
            raise ValueError, "code_ext and exec_ext options must be defined"
                
        if generate_expr <> None :
            self.generate_expr_method = generate_expr
        else: 
            raise ValueError, "Please define generate_expr method"
        
        if generate_code <> None :
            self.generate_code_method = generate_code
        else: 
            raise ValueError, "Please define generate_code method"
        
        if compile <> None :
            self.compile_method = compile
        else: 
            raise ValueError, "Please define compile method"
        
        if execute <> None :
            self.execute_method = execute
        else: 
            raise ValueError, "Please define execute method"
        
    def refine_options(self, argv):
        for option in self.options:
            option.get_value(argv)
            
    def get_option_value(self, name):
        for option in self.options:
            if option.name == name:
                return option.value
        raise ValueError, "No such option: %s"%name 
    
    def print_options(self):
        
        print "Options:\n"
        if len(self.options)<>0:
            for option in self.options:
                print "%s = %s , type: %s\n"%(option.name,option.value,option.type)
        else:
            print "\tEmpty\n"
            
        print "---------------\n"
        
    def generate_expr(self, G, bar):
        return self.generate_expr_method(G, self.options, bar)
    
    def generate_code(self, G, exprs, bar):
        self._remove_files(self._get_progs_name(G))
        self._remove_files(self._get_execs_name(G))    
        return self.generate_expr_method(exprs, self.options, bar)
    
    def compile(self, progs, bar):
        return self.compile_method(progs, self.options, bar)
    
    def execute(self, progs, bar):
        return self.compile_method(progs, self.options, bar)
    
    def _get_names(self, G, pattern):
        import os
        import re
        G.WorkDir()
        dirlist=os.listdir("./")
        res = list()
        for line in dirlist:
            reg = re.match(pattern, line)
            if reg:
                res.append(line)
        return res
        
    
    def _get_progs_name(self, G):
        ext = self.get_option_value("code_ext")
        pattern = "^%s_%s_.*e\d+\.%s$"%(self.name,str(G.nickel), ext)
        return self._get_names(G,pattern)
    
    
    def _get_execs_name(self, G):
        ext = self.get_option_value("exec_ext")
        pattern = "^%s_%s_.*e\d+%s$"%(self.name,str(G.nickel), ext)
        return self._get_names(G,pattern)
    
    def _remove_files(self, filelist):
        import os
        for file in filelist:
            os.remove(file)
        
        
        